from typing import List
from django.shortcuts import get_object_or_404
from django.db.models import Subquery, F, OuterRef, Case, When, Value, Q
from django.db.models.functions import Coalesce

from ninja_extra import route, api_controller, ControllerBase

from pop.cohorts.schemas.analysis import KapplerMeierCurve
from pop.cohorts.analysis import calculate_Kappler_Maier_survival_curve, calculate_pfs_by_combination_therapy, calculate_pfs_by_therapy_classification
from pop.cohorts.models import Cohort
from pop.oncology.models import TherapyLine
from pop.core.auth import permissions as perms
from pop.core.auth.token import XSessionTokenAuth

from collections import Counter
from enum import Enum
from .cohort import EmptyCohortException


class FeaturesCounters(str,Enum):
    gender = 'gender'
    age = 'age'
    age_at_diagnosis = 'age_at_diagnosis'
    vital_status = 'vital_status'    
    therapy_line = 'therapy_line'    

@api_controller(
    "/cohorts", 
    auth=[XSessionTokenAuth()], 
    tags=["Cohorts"]
)
class CohortAnalysisController(ControllerBase):
    
    @route.get(
        path='/{cohortId}/overall-survival-curve', 
        response={
            200: KapplerMeierCurve,
            404: None, 422: None,
            401: None, 403: None,
        },
        permissions=[perms.CanViewCohorts],
        operation_id='getCohortOverallSurvivalCurve',
    )
    def get_cohort_overall_survival_curve(self, cohortId: str):
        cohort = get_object_or_404(Cohort, id=cohortId)
        if not cohort.cases.exists():
            raise EmptyCohortException
        # Get all the OS values for the cohort
        overall_survivals = list(cohort.cases.annotate(overall_survival=F('overall_survival')).values_list('overall_survival',flat=True))
        # Compute and return the OS KM-curve
        months, probabilities, confidence_bands = calculate_Kappler_Maier_survival_curve(overall_survivals)
        return 200, KapplerMeierCurve(
            months=months, 
            probabilities=probabilities, 
            lowerConfidenceBand=confidence_bands['lower'],
            upperConfidenceBand=confidence_bands['upper'],
        )

    @route.get(
        path='/{cohortId}/genomics', 
        response={
            200: dict,
            404: None, 422: None,
            401: None, 403: None,
        },
        permissions=[perms.CanViewCohorts],
        operation_id='getCohortGenomics',
    )
    def get_cohort_genomics(self, cohortId: str):
        from pop.oncology.models import GenomicVariant
        cohort = get_object_or_404(Cohort, id=cohortId)
        if not cohort.cases.exists():
            raise EmptyCohortException
        variants = GenomicVariant.objects.filter(case__in=cohort.cases.all())
        genes = [gene[0] for gene in Counter(variants.values_list('genes__display', flat=True)).most_common(25)]
        variants = variants.filter(genes__display__in=genes).annotate(
            pseudoidentifier=F('case__pseudoidentifier'),gene=F('genes__display'), variant=Coalesce(F('protein_hgvs'), F('dna_hgvs'), Value('?')),
        ).values('pseudoidentifier','gene', 'variant', 'is_pathogenic')
        return 200, {'genes': genes, 'cases': list(cohort.cases.values_list('pseudoidentifier',flat=True)),'variants': list(variants)}


    @route.get(
        path='/{cohortId}/progression-free-survival-curve/{therapyLine}', 
        response={
            200: KapplerMeierCurve,
            404: None, 422: None,
            401: None, 403: None,
        },
        permissions=[perms.CanViewCohorts],
        operation_id='getCohortProgressionFreeSurvivalCurve',
    )
    def get_cohort_progression_free_survival_curve(self, cohortId: str, therapyLine: str):
        cohort = get_object_or_404(Cohort, id=cohortId)
        if not cohort.cases.exists():
            raise EmptyCohortException
        progression_free_survivals = cohort.cases.annotate(progression_free_survival=
            # Filter all therapy lines for current patient and by the queries line-label
            Subquery(
                TherapyLine.objects.filter(case_id=OuterRef('id'), label=therapyLine).annotate(
                    # This is needed for the annotated property to be available to values_list()
                    pfs=F('progression_free_survival')
                ).values_list('pfs', flat=True)[:1]
            ) 
        # Limit the queryset to those cases which have a non-null PFS value and extract those as a list
        ).filter(progression_free_survival__isnull=False).values_list('progression_free_survival', flat=True)
        # Compute the PFS KM-curve
        months, probabilities, confidence_bands = calculate_Kappler_Maier_survival_curve(progression_free_survivals)
        return 200, KapplerMeierCurve(
            months=months, 
            probabilities=probabilities, 
            lowerConfidenceBand=confidence_bands['lower'],
            upperConfidenceBand=confidence_bands['upper'],
        )


    @route.get(
        path='/{cohortId}/progression-free-survival/{therapyLine}/drug-combinations', 
        response={
            200: dict,
            404: None, 422: None,
            401: None, 403: None,
        },
        permissions=[perms.CanViewCohorts],
        operation_id='getCohortProgressionFreeSurvivalCurveByDrugCombinations',
    )
    def get_cohort_progression_free_survival_curve_by_drug_combinations(self, cohortId: str, therapyLine: str):
        cohort = get_object_or_404(Cohort, id=cohortId)
        if not cohort.cases.exists():
            raise EmptyCohortException
        return 200, calculate_pfs_by_combination_therapy(cohort, therapyLine)
    

    @route.get(
        path='/{cohortId}/progression-free-survival/{therapyLine}/therapy-classifications', 
        response={
            200: dict,
            404: None, 422: None,
            401: None, 403: None,
        },
        permissions=[perms.CanViewCohorts],
        operation_id='getCohortProgressionFreeSurvivalCurveByTherapyClassifications',
    )
    def get_cohort_progression_free_survival_curve_by_therapy_classifications(self, cohortId: str, therapyLine: str):
        cohort = get_object_or_404(Cohort, id=cohortId)
        if not cohort.cases.exists():
            raise EmptyCohortException
        return 200, calculate_pfs_by_therapy_classification(cohort, therapyLine)