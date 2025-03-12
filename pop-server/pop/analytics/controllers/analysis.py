from typing import List
from django.shortcuts import get_object_or_404
from django.db.models import Subquery, F, OuterRef, Case, When, Value, Q

from ninja_extra import route, api_controller
from ninja_jwt.authentication import JWTAuth
from ninja_extra import api_controller, ControllerBase, route

from pop.analytics.schemas.analysis import KapplerMeierCurve
from pop.analytics.analysis import calculate_Kappler_Maier_survival_curve, calculate_pfs_by_combination_therapy
from pop.analytics.models import Cohort
from pop.oncology.models import TherapyLine
from pop.core import permissions as perms

from collections import Counter
from enum import Enum

class FeaturesCounters(str,Enum):
    gender = 'gender'
    age = 'age'
    age_at_diagnosis = 'age_at_diagnosis'
    vital_status = 'vital_status'    
    therapy_line = 'therapy_line'    

@api_controller(
    "/cohorts", 
    auth=[JWTAuth()], 
    tags=["Cohorts"]
)
class CohortAnalysisController(ControllerBase):


    @route.get(
        path='/{cohortId}/counter/{feature}', 
        response={
            200: dict
        },
        permissions=[perms.CanViewCohorts],
        operation_id='getCohortFeatureCounter',
    )
    def get_cohort_feature_counter(self, cohortId: str, feature: FeaturesCounters):
        cohort = get_object_or_404(Cohort, id=cohortId)
        if feature == FeaturesCounters.age:
            feature_values = cohort.cases.annotate(age=F('age')).values_list('age',flat=True)
        elif feature == FeaturesCounters.age_at_diagnosis:
            feature_values = cohort.cases.annotate(age_at_diagnosis=F('age_at_diagnosis')).values_list('age_at_diagnosis',flat=True)
        elif feature == FeaturesCounters.gender:
            feature_values = cohort.cases.values_list('gender__display',flat=True)
        elif feature == FeaturesCounters.vital_status:
            feature_values = cohort.cases.annotate(vital_status=Case(When(Q(is_deceased=True), then=Value('Deceased')), default=Value('Alive'))).values_list('vital_status',flat=True)
        elif feature == FeaturesCounters.therapy_line:
            feature_values = cohort.cases.values_list('therapy_lines__label',flat=True)
        return 200, Counter(feature_values)
    
    @route.get(
        path='/{cohortId}/overall-survival-curve', 
        response={
            200: KapplerMeierCurve
        },
        permissions=[perms.CanViewCohorts],
        operation_id='getCohortOverallSurvivalCurve',
    )
    def get_cohort_overall_survival_curve(self, cohortId: str):
        cohort = get_object_or_404(Cohort, id=cohortId)
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
            200: dict
        },
        permissions=[perms.CanViewCohorts],
        operation_id='getCohortGenomics',
    )
    def get_cohort_genomics(self, cohortId: str):
        from pop.oncology.models import GenomicVariant
        cohort = get_object_or_404(Cohort, id=cohortId)
        variants = GenomicVariant.objects.filter(case__in=cohort.cases.all()).filter(is_pathogenic=True)
        genes = [gene[0] for gene in Counter(variants.values_list('genes__display', flat=True)).most_common(25)]
        variants = variants.filter(genes__display__in=genes).annotate(
            pseudoidentifier=F('case__pseudoidentifier'),gene=F('genes__display'), variant=F('protein_hgvs')
        ).values('pseudoidentifier','gene', 'variant')
        return 200, {'genes': genes, 'cases': list(cohort.cases.values_list('pseudoidentifier',flat=True)),'variants': list(variants)}


    @route.get(
        path='/{cohortId}/progression-free-survival-curve/{therapyLine}', 
        response={
            200: KapplerMeierCurve
        },
        permissions=[perms.CanViewCohorts],
        operation_id='getCohortProgressionFreeSurvivalCurve',
    )
    def get_cohort_progression_free_survival_curve(self, cohortId: str, therapyLine: str):
        cohort = get_object_or_404(Cohort, id=cohortId)
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
        path='/{cohortId}/progression-free-survival-curve/{therapyLine}/drug-combinations', 
        response={
            200: dict
        },
        permissions=[perms.CanViewCohorts],
        operation_id='getCohortProgressionFreeSurvivalCurveByDrugCombinations',
    )
    def get_cohort_progression_free_survival_curve_by_drug_combinations(self, cohortId: str, therapyLine: str):
        cohort = get_object_or_404(Cohort, id=cohortId)
        return 200, calculate_pfs_by_combination_therapy(cohort, therapyLine)