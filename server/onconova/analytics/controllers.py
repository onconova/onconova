"""
This module provides API endpoints for dashboard analytics in the Onconova platform.
It exposes statistics and metrics related to patient cases, primary sites, data completion,
and temporal trends for use in dashboard visualizations.
"""

from collections import Counter
from typing import List

from django.db.models import (
    Count,
    Exists,
    ExpressionWrapper,
    F,
    FloatField,
    OuterRef,
    Subquery,
    Window,
)
from django.db.models.functions import Cast, TruncMonth
from ninja_extra import ControllerBase, api_controller, route

from onconova.analytics.schemas import (
    CountsPerMonth,
    DataCompletionStatistics,
    DataPlatformStatistics,
    EntityStatistics,
    IncompleteCategory,
)
from onconova.core.aggregates import Median
from onconova.core.auth.token import XSessionTokenAuth
from onconova.core.utils import COMMON_HTTP_ERRORS
from onconova.oncology import models as oncological_models
from onconova.oncology.models.neoplastic_entity import NeoplasticEntityRelationshipChoices
from onconova.research.models.cohort import Cohort
from onconova.research.models.project import Project
from onconova.terminology.models import CancerTopographyGroup


@api_controller("/dashboard", auth=[XSessionTokenAuth()], tags=["Dashboard"])
class DashboardController(ControllerBase):
    """
    DashboardController provides API endpoints for retrieving various analytics and statistics
    related to oncological data on the platform. Each endpoint returns structured data models 
    representing the requested statistics, supporting data-driven insights for platform users.
    """

    @route.get(
        path="/stats",
        response={200: DataPlatformStatistics, **COMMON_HTTP_ERRORS},
        operation_id="getFullCohortStatistics",
    )
    def get_full_cohort_statistics(self):
        """
        Retrieves comprehensive statistics for the full cohort, including counts of cases, primary sites,
        entries, mutations, clinical centers, contributors, cohorts, and projects.
        """
        return DataPlatformStatistics(
            cases=oncological_models.PatientCase.objects.count(),
            primarySites=oncological_models.NeoplasticEntity.objects.select_properties(
                "topography_group"
            )
            .filter(relationship=NeoplasticEntityRelationshipChoices.PRIMARY)
            .distinct("topography_group")
            .count(),
            entries=sum([model.objects.count() for model in oncological_models.MODELS]),
            mutations=oncological_models.GenomicVariant.objects.count(),
            clinicalCenters=oncological_models.PatientCase.objects.distinct(
                "clinical_center"
            ).count(),
            contributors=oncological_models.PatientCase.pgh_event_model.objects.values(
                "pgh_context__username"
            )
            .distinct()
            .count(),
            cohorts=Cohort.objects.count(),
            projects=Project.objects.count(),
        )

    @route.get(
        path="/primary-site-stats",
        response={200: List[EntityStatistics], **COMMON_HTTP_ERRORS},
        operation_id="getPrimarySiteStatistics",
    )
    def get_primary_site_statistics(self):
        """
        Retrieves statistical data for primary neoplastic entities grouped by topography.

        This method performs the following steps:
        
        1. Selects distinct topography groups from primary neoplastic entities.
        2. For each topography group, identifies the cohort of patient cases associated with primary neoplastic entities matching the group's code.
        3. Calculates the population size and the median data completion rate for each cohort.
        4. Constructs a list of EntityStatistics objects containing the computed statistics and topography information.
        5. Sorts the statistics by population size in descending order.
        """
        primary_entities = (
            oncological_models.NeoplasticEntity.objects.select_properties(
                "topography_group"
            )
            .filter(relationship=NeoplasticEntityRelationshipChoices.PRIMARY)
            .values("topography_group__code", "topography_group__display")
            .distinct()
        )
        statistics = []
        for entity in primary_entities:
            entity_code = entity.get("topography_group__code")
            entity_cohort = oncological_models.PatientCase.objects.filter(
                Exists(
                    oncological_models.NeoplasticEntity.objects.filter(
                        relationship=NeoplasticEntityRelationshipChoices.PRIMARY,
                        topography__code__contains=entity_code,
                        case_id=OuterRef("pk"),
                    )
                )
            )
            statistics.append(
                EntityStatistics(
                    population=entity_cohort.count(),
                    dataCompletionMedian=entity_cohort.aggregate(
                        Median("data_completion_rate")
                    ).get("data_completion_rate__median"),
                    topographyCode=entity_code,
                    topographyGroup=entity.get("topography_group__display"),
                )
            )
        statistics.sort(key=lambda x: x.population, reverse=True)
        return statistics

    @route.get(
        path="/cases-over-time",
        response={200: List[CountsPerMonth], **COMMON_HTTP_ERRORS},
        operation_id="getCasesOverTime",
    )
    def get_cases_over_time(self):
        """
        Retrieves the cumulative count of patient cases over time, grouped by month.
        """
        return (
            oncological_models.PatientCase.objects.select_properties("created_at")
            .annotate(month=TruncMonth("created_at"))
            .values("month")
            .annotate(
                cumulativeCount=Window(
                    expression=Count("id"), order_by=F("month").asc()
                )
            )
            .order_by("month")
        )

    @route.get(
        path="/data-completion-stats",
        response={200: DataCompletionStatistics, **COMMON_HTTP_ERRORS},
        operation_id="getDataCompletionStats",
    )
    def get_data_completion_statistics(self):
        """
        Computes and returns statistics on data completion for patient cases.

        - If there are no patient cases, returns zeroed statistics.
        - Uses Django ORM aggregation and annotation for efficient computation.
        - Identifies most incomplete categories and the most affected sites for each.
        - Tracks completion progress over time using monthly aggregation.
        """
        # Total count of PatientCases (denominator for percentages)
        total_cases = oncological_models.PatientCase.objects.count()
        if total_cases == 0:
            return 200, DataCompletionStatistics(
                totalCases=total_cases,
                overallCompletion=0,
                mostIncompleteCategories=[],
                completionOverTime=[],
            )
        overall_completion = round(
            oncological_models.PatientCaseDataCompletion.objects.count()
            / (
                total_cases
                * oncological_models.PatientCaseDataCompletion.DATA_CATEGORIES_COUNT
            )
            * 100
        )
        # Aggregated counts from PatientCaseDataCompletion by category
        queryset = oncological_models.PatientCaseDataCompletion.objects.values(
            "category"
        ).annotate(
            counts=Count("id"),
            percentage=ExpressionWrapper(
                Cast(Count("id"), FloatField()) * 100.0 / total_cases,
                output_field=FloatField(),
            ),
        )
        # Create a dictionary for quick access to counts/cases per category
        data_map = {item["category"]: item for item in queryset}
        # Map to all defined categories (even those with 0 occurrences)
        results = [
            {
                "category": category.value,
                "counts": data_map.get(category.value, {}).get("counts", 0),
                "cases": data_map.get(category.value, {}).get("cases", 0.0),
            }
            for category in oncological_models.PatientCaseDataCompletion.PatientCaseDataCategories
        ]
        results.sort(key=lambda x: x["counts"])
        top_most_incomplete = []
        for result in results[:3]:
            affected_cases = oncological_models.PatientCase.objects.exclude(
                completed_data_categories__category=result["category"]
            )
            most_affected_sites = Counter(
                affected_cases.annotate(
                    site_code=Subquery(
                        oncological_models.NeoplasticEntity.objects.filter(
                            case_id=OuterRef("id"), relationship="primary"
                        )
                        .select_properties("topography_group")
                        .values_list(f"topography_group__code")[:1]
                    ),
                ).values_list("site_code", flat=True)
            ).most_common(4)
            most_affected_sites = [code for (code, count) in most_affected_sites]
            top_most_incomplete.append(
                IncompleteCategory(
                    category=result["category"],
                    cases=affected_cases.count(),
                    affectedSites=list(
                        CancerTopographyGroup.objects.filter(
                            code__in=most_affected_sites
                        )
                    ),
                )
            )

        completion_over_time = (
            oncological_models.PatientCaseDataCompletion.objects.select_properties(
                "created_at"
            )
            .annotate(month=TruncMonth("created_at"))
            .values("month")
            .annotate(
                cumulativeCount=Window(
                    expression=Count("id"), order_by=F("month").asc()
                )
            )
            .order_by("month")
            .distinct()
        )

        return 200, DataCompletionStatistics(
            totalCases=total_cases,
            overallCompletion=overall_completion,
            mostIncompleteCategories=top_most_incomplete,
            completionOverTime=completion_over_time,
        )
