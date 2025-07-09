import pghistory
import json
import hashlib
from enum import Enum
from datetime import datetime
from collections import Counter, OrderedDict
from typing import List

from django.conf import settings
from django.shortcuts import get_object_or_404
from django.db.models import Subquery, F, OuterRef, Value, Max, Min
from django.db.models.functions import Coalesce

from ninja import Query
from ninja.errors import HttpError, ValidationError
from ninja_extra import route, api_controller
from ninja_extra.pagination import paginate
from ninja_extra.ordering import ordering
from ninja_extra import route, api_controller, status, ControllerBase
from ninja_extra.exceptions import APIException

from pop.core.auth import permissions as perms
from pop.core.utils import camel_to_snake
from pop.core.auth.token import XSessionTokenAuth
from pop.core.anonymization import anonymize, anonymize_age
from pop.core.schemas import ModifiedResource as ModifiedResourceSchema, Paginated
from pop.core.history.schemas import HistoryEvent

from pop.oncology import schemas as oncological_schemas
from pop.oncology.models import TherapyLine, TreatmentResponse
from pop.interoperability.schemas import ExportMetadata

from pop.research.compilers import construct_dataset
from pop.research.models.dataset import Dataset
from pop.research.models.cohort import Cohort
from pop.research.models.project import Project
from pop.research.schemas.dataset import (
    DatasetRule,
    PatientCaseDataset,
    ExportedPatientCaseDataset,
)
from pop.research.schemas.cohort import (
    CohortSchema,
    CohortCreateSchema,
    CohortFilters,
    CohortTraits,
    ExportedCohortDefinition,
    CohortTraitMedian,
    CohortTraitCounts,
    CohortContribution,
)
from pop.research.schemas.analysis import (
    KapplerMeierCurve,
    CategorySurvivals,
    OncoplotDataset,
)
from pop.research.analysis import (
    calculate_Kappler_Maier_survival_curve,
    calculate_pfs_by_combination_therapy,
    calculate_pfs_by_therapy_classification,
    count_treatment_responses_by_therapy_line,
)


def convert_api_path_to_snake_case_path(path):
    components = path.split(".")
    components = [camel_to_snake(component) for component in components]
    return "__".join(components)


class EmptyCohortException(APIException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    default_detail = "Unprocessable. Requested cohort is empty."



@api_controller("/cohorts", auth=[XSessionTokenAuth()], tags=["Data Analysis"])
class CohortAnalysisController(ControllerBase):

    @route.get(
        path="/{cohortId}/overall-survival-curve",
        response={
            200: KapplerMeierCurve,
            404: None,
            422: None,
            401: None,
            403: None,
        },
        permissions=[perms.CanViewCohorts],
        operation_id="getCohortOverallSurvivalCurve",
    )
    def get_cohort_overall_survival_curve(self, cohortId: str):
        cohort = get_object_or_404(Cohort, id=cohortId)
        if not cohort.valid_cases.exists():
            raise EmptyCohortException
        # Get all the OS values for the cohort
        overall_survivals = list(
            cohort.valid_cases.annotate(overall_survival=F("overall_survival")).values_list(
                "overall_survival", flat=True
            )
        )
        # Compute and return the OS KM-curve
        months, probabilities, confidence_bands = (
            calculate_Kappler_Maier_survival_curve(overall_survivals)
        )
        return 200, KapplerMeierCurve(
            months=months,
            probabilities=probabilities,
            lowerConfidenceBand=confidence_bands["lower"],
            upperConfidenceBand=confidence_bands["upper"],
        )

    @route.get(
        path="/{cohortId}/genomics",
        response={
            200: OncoplotDataset,
            404: None,
            422: None,
            401: None,
            403: None,
        },
        permissions=[perms.CanViewCohorts],
        operation_id="getCohortGenomics",
    )
    def get_cohort_genomics(self, cohortId: str):
        from pop.oncology.models import GenomicVariant

        cohort = get_object_or_404(Cohort, id=cohortId)
        if not cohort.valid_cases.exists():
            raise EmptyCohortException
        cases = cohort.valid_cases.all()
        variants = GenomicVariant.objects.filter(case__in=cases)
        genes = [
            gene[0]
            for gene in Counter(
                variants.values_list("genes__display", flat=True)
            ).most_common(25)
        ]
        variants = (
            variants.filter(genes__display__in=genes)
            .annotate(
                pseudoidentifier=F("case__pseudoidentifier"),
                gene=F("genes__display"),
                hgvs_expression=Coalesce(F("protein_hgvs"), F("dna_hgvs"), Value("?")),
            )
            .values("pseudoidentifier", "gene", "hgvs_expression", "is_pathogenic")
        )
        return 200, {
            "genes": genes,
            "cases": list(cases.values_list("pseudoidentifier", flat=True)),
            "variants": list(variants),
        }

    @route.get(
        path="/{cohortId}/progression-free-survival-curve/{therapyLine}",
        response={
            200: KapplerMeierCurve,
            404: None,
            422: None,
            401: None,
            403: None,
        },
        permissions=[perms.CanViewCohorts],
        operation_id="getCohortProgressionFreeSurvivalCurve",
    )
    def get_cohort_progression_free_survival_curve(
        self, cohortId: str, therapyLine: str
    ):
        cohort = get_object_or_404(Cohort, id=cohortId)
        if not cohort.valid_cases.exists():
            raise EmptyCohortException
        progression_free_survivals = (
            cohort.valid_cases.annotate(
                progression_free_survival=
                # Filter all therapy lines for current patient and by the queries line-label
                Subquery(
                    TherapyLine.objects.filter(
                        case_id=OuterRef("id"), label=therapyLine
                    )
                    .annotate(
                        # This is needed for the annotated property to be available to values_list()
                        pfs=F("progression_free_survival")
                    )
                    .values_list("pfs", flat=True)[:1]
                )
                # Limit the queryset to those cases which have a non-null PFS value and extract those as a list
            )
            .filter(progression_free_survival__isnull=False)
            .values_list("progression_free_survival", flat=True)
        )
        # Compute the PFS KM-curve
        months, probabilities, confidence_bands = (
            calculate_Kappler_Maier_survival_curve(progression_free_survivals)
        )
        return 200, KapplerMeierCurve(
            months=months,
            probabilities=probabilities,
            lowerConfidenceBand=confidence_bands["lower"],
            upperConfidenceBand=confidence_bands["upper"],
        )

    @route.get(
        path="/{cohortId}/progression-free-survival/{therapyLine}/drug-combinations",
        response={
            200: CategorySurvivals,
            404: None,
            422: None,
            401: None,
            403: None,
        },
        permissions=[perms.CanViewCohorts],
        operation_id="getCohortProgressionFreeSurvivalCurveByDrugCombinations",
    )
    def get_cohort_progression_free_survival_curve_by_drug_combinations(
        self, cohortId: str, therapyLine: str
    ):
        cohort = get_object_or_404(Cohort, id=cohortId)
        if not cohort.valid_cases.exists():
            raise EmptyCohortException
        return 200, calculate_pfs_by_combination_therapy(cohort, therapyLine)

    @route.get(
        path="/{cohortId}/progression-free-survival/{therapyLine}/therapy-classifications",
        response={
            200: CategorySurvivals,
            404: None,
            422: None,
            401: None,
            403: None,
        },
        permissions=[perms.CanViewCohorts],
        operation_id="getCohortProgressionFreeSurvivalCurveByTherapyClassifications",
    )
    def get_cohort_progression_free_survival_curve_by_therapy_classifications(
        self, cohortId: str, therapyLine: str
    ):
        cohort = get_object_or_404(Cohort, id=cohortId)
        if not cohort.valid_cases.exists():
            raise EmptyCohortException
        return 200, calculate_pfs_by_therapy_classification(cohort, therapyLine)

    @route.get(
        path="/{cohortId}/therapy-responses/{therapyLine}",
        response={
            200: List[CohortTraitCounts],
            404: None,
            422: None,
            401: None,
            403: None,
        },
        permissions=[perms.CanViewCohorts],
        operation_id="getCohortTherapyLineResponseDistribution",
    )
    def get_cohort_therapy_line_responses_distribution(
        self, cohortId: str, therapyLine: str
    ):
        cohort = get_object_or_404(Cohort, id=cohortId)
        if not cohort.valid_cases.exists():
            raise EmptyCohortException
        counter = count_treatment_responses_by_therapy_line(cohort, therapyLine)
        return 200, [
            CohortTraitCounts(category=category, counts=count, percentage=percentage)
            for category, (count, percentage) in counter.items()
        ]
