from typing import Literal

from django.db.models import F, OuterRef, Subquery
from django.shortcuts import get_object_or_404
from ninja_extra import ControllerBase, api_controller, route
from pop.core.auth import permissions as perms
from pop.core.auth.token import XSessionTokenAuth
from pop.core.utils import COMMON_HTTP_ERRORS
from pop.oncology.models import TherapyLine
from pop.research.controllers.cohort import EmptyCohortException
from pop.research.models.cohort import Cohort
from pop.research.schemas.analysis import (
    CategorizedSurvivals,
    KaplanMeierCurve,
    OncoplotDataset,
    TherapyLineResponseCounts,
)


def get_nonempty_cohort_or_error(cohortId: str) -> Cohort:
    cohort = get_object_or_404(Cohort, id=cohortId)
    if not cohort.valid_cases.exists():
        raise EmptyCohortException
    return cohort


@api_controller("/cohorts", auth=[XSessionTokenAuth()], tags=["Data Analysis"])
class CohortAnalysisController(ControllerBase):

    @route.get(
        path="/{cohortId}/analysis/overall-survical/kaplan-meier",
        response={200: KaplanMeierCurve, 422: None, **COMMON_HTTP_ERRORS},
        permissions=[perms.CanViewCohorts],
        operation_id="getCohortOverallSurvivalCurve",
    )
    def get_cohort_overall_survival_curve(
        self, cohortId: str, confidence: float = 0.95
    ):
        cohort = get_nonempty_cohort_or_error(cohortId)
        return KaplanMeierCurve.calculate(
            survivals=cohort.valid_cases.annotate(
                overall_survival=F("overall_survival")
            )
            .filter(overall_survival__isnull=False)
            .values_list("overall_survival", flat=True),
            confidence_level=confidence,
        ).add_metadata(cohort)

    @route.get(
        path="/{cohortId}/analysis/oncoplot",
        response={200: OncoplotDataset, 422: None, **COMMON_HTTP_ERRORS},
        permissions=[perms.CanViewCohorts],
        operation_id="getCohortOncoplot",
    )
    def get_cohort_oncoplot_dataset(self, cohortId: str):
        cohort = get_nonempty_cohort_or_error(cohortId)
        return OncoplotDataset.calculate(cohort.valid_cases.all()).add_metadata(cohort)

    @route.get(
        path="/{cohortId}/analysis/{therapyLine}/progression-free-survival/kaplan-meier",
        response={200: KaplanMeierCurve, 422: None, **COMMON_HTTP_ERRORS},
        permissions=[perms.CanViewCohorts],
        operation_id="getCohortLineProgressionFreeSurvivalCurve",
    )
    def get_cohort_line_progression_free_survival_curve(
        self, cohortId: str, therapyLine: str, confidence: float = 0.95
    ):
        cohort = get_nonempty_cohort_or_error(cohortId)
        return 200, KaplanMeierCurve.calculate(
            survivals=cohort.valid_cases.annotate(
                progression_free_survival=Subquery(
                    TherapyLine.objects.filter(
                        case_id=OuterRef("id"), label=therapyLine
                    )
                    .annotate(pfs=F("progression_free_survival"))
                    .values_list("pfs", flat=True)[:1]
                )
            )
            .filter(progression_free_survival__isnull=False)
            .values_list("progression_free_survival", flat=True),
            confidence_level=confidence,
        ).add_metadata(cohort)

    @route.get(
        path="/{cohortId}/analysis/{therapyLine}/progression-free-survivals/categories",
        response={200: CategorizedSurvivals, 422: None, **COMMON_HTTP_ERRORS},
        permissions=[perms.CanViewCohorts],
        operation_id="getCohortLineProgressionFreeSurvivalsByCategories",
    )
    def get_cohort_line_progression_free_survival_by_categories(
        self,
        cohortId: str,
        therapyLine: str,
        categorization: Literal["therapies"] | Literal["drugs"],
    ):
        cohort = get_nonempty_cohort_or_error(cohortId)
        return CategorizedSurvivals.calculate(
            cohort=cohort,
            therapyLine=therapyLine,
            categorization=categorization,
        ).add_metadata(cohort)

    @route.get(
        path="/{cohortId}/analysis/{therapyLine}/counts/therapy-response",
        response={200: TherapyLineResponseCounts, 422: None, **COMMON_HTTP_ERRORS},
        permissions=[perms.CanViewCohorts],
        operation_id="getCohortTherapyLineResponsesCounts",
    )
    def get_cohort_therapy_line_response_counts(self, cohortId: str, therapyLine: str):
        cohort = get_nonempty_cohort_or_error(cohortId)
        return TherapyLineResponseCounts.calculate(cohort, therapyLine).add_metadata(
            cohort
        )
