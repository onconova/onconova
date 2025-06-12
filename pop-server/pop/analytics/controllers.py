from typing import List

from django.db.models import Count, Window, F
from django.db.models.functions import TruncMonth

from ninja_extra import route, api_controller
from ninja_extra import api_controller, ControllerBase, route

from pop.oncology import models as oncological_models
from pop.research.models.project import Project
from pop.research.models.cohort import Cohort
from pop.core.auth.token import XSessionTokenAuth
from pop.analytics.schemas import EntityStatisticsSchema, DataPlatformStatisticsSchema, CasesPerMonthSchema
from pop.core.aggregates import Median


@api_controller(
    "/dashboard", 
    auth=[XSessionTokenAuth()], 
    tags=["Dashboard"]
)
class DashboardController(ControllerBase):

    @route.get(
        path='/stats', 
        response={
            200: DataPlatformStatisticsSchema,
            401: None, 403: None,
        },
        operation_id='getFullCohortStatistics',
    )
    def get_full_cohort_statistics(self):
        return DataPlatformStatisticsSchema(
            cases = oncological_models.PatientCase.objects.count(),
            primarySites = oncological_models.NeoplasticEntity.objects.select_properties('topography_group').filter(
                relationship=oncological_models.NeoplasticEntityRelationship.PRIMARY
            ).distinct('topography_group').count(),
            entries = sum([model.objects.count() for model in oncological_models.MODELS]),
            mutations = oncological_models.GenomicVariant.objects.count(),
            clinicalCenters = oncological_models.PatientCase.objects.distinct('clinical_center').count(),
            contributors = oncological_models.PatientCase.pgh_event_model.objects.values('pgh_context__username').distinct().count(),
            cohorts = Cohort.objects.count(),
            projects = Project.objects.count(),
        )
    
    @route.get(
        path='/primary-site-stats', 
        response={
            200: List[EntityStatisticsSchema],
            401: None, 403: None,
        },
        operation_id='getPrimarySiteStatistics',
    )
    def get_primary_site_statistics(self):
        primary_entities = oncological_models.NeoplasticEntity.objects.select_properties('topography_group').filter(
                relationship=oncological_models.NeoplasticEntityRelationship.PRIMARY
            ).values('topography_group__code','topography_group__display').distinct()
        statistics = []
        for entity in primary_entities:
            entity_code, entity_display = entity.get('topography_group__code'),entity.get('topography_group__display')
            entity_cohort = oncological_models.PatientCase.objects.filter(neoplastic_entities__topography__code__contains=entity_code).filter(neoplastic_entities__relationship=oncological_models.NeoplasticEntityRelationship.PRIMARY)
            statistics.append(EntityStatisticsSchema(
                population = entity_cohort.count(),                
                dataCompletionMedian = entity_cohort.aggregate(Median('data_completion_rate')).get('data_completion_rate__median'),
                topographyCode=entity_code,
                topographyGroup=entity_display,
            ))
        statistics.sort(key=lambda x: x.population, reverse=True)
        return statistics
    
    @route.get(
        path='/cases-over-time', 
        response={
            200: List[CasesPerMonthSchema],
            401: None, 403: None,
        },
        operation_id='getCasesOverTime',
    )
    def get_cases_over_time(self):
        return oncological_models.PatientCase.objects.select_properties('created_at').annotate(
                month=TruncMonth('created_at')
            ).values('month').annotate(
                cumulativeCount=Window(expression=Count('id'), order_by=F('month').asc())
            ).order_by('month')
