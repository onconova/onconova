import pghistory
import json 
import hashlib
from enum import Enum
from datetime import datetime
from collections import Counter
from typing import List, Any

from django.conf import settings 
from django.shortcuts import get_object_or_404
from django.db.models import Subquery, F, OuterRef, Value
from django.db.models.functions import Coalesce


from ninja import Query
from ninja_extra import route, api_controller
from ninja_extra.pagination import paginate
from ninja_extra import route, api_controller, status, ControllerBase
from ninja_extra.exceptions import APIException

from pop.core.auth import permissions as perms
from pop.core.utils import camel_to_snake
from pop.core.auth.token import XSessionTokenAuth
from pop.core.anonymization import anonymize
from pop.core.schemas import ModifiedResource as ModifiedResourceSchema, Paginated
from pop.core.history.schemas import HistoryEvent

from pop.oncology import schemas as oncological_schemas
from pop.interoperability.schemas import ExportMetadata

from pop.research.compilers import construct_dataset
from pop.research.models.dataset import Dataset
from pop.research.models.cohort import Cohort
from pop.research.schemas.dataset import DatasetRule, PatientCaseDataset
from pop.research.schemas.cohort import (
    CohortSchema, CohortCreateSchema, 
    CohortFilters, CohortTraitAverage, 
    CohortTraitMedian, CohortTraitCounts,
    CohortContribution, KapplerMeierCurve
)
from pop.research.analysis import (
    calculate_Kappler_Maier_survival_curve, 
    calculate_pfs_by_combination_therapy, 
    calculate_pfs_by_therapy_classification
)



def convert_api_path_to_snake_case_path(path):
    components = path.split('.')
    components = [camel_to_snake(component) for component in components]
    return '__'.join(components)



class EmptyCohortException(APIException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    default_detail = 'Unprocessable. Requested cohort is empty.'


@api_controller(
    "/cohorts", 
    auth=[XSessionTokenAuth()], 
    tags=["Cohorts"]
)
class CohortsController(ControllerBase):


    @route.get(
        path='', 
        response={
            200: Paginated[CohortSchema],
            401: None, 403: None,
        },
        permissions=[perms.CanViewCohorts],
        operation_id='getCohorts',
    )
    @paginate()
    def get_all_cohorts_matching_the_query(self, query: Query[CohortFilters]):
        queryset = Cohort.objects.all().order_by('-created_at')
        return query.filter(queryset)

    @route.post(
        path='', 
        response={
            201: ModifiedResourceSchema,
            401: None, 403: None,
        },
        permissions=[perms.CanManageCohorts],
        operation_id='createCohort',
    )
    def create_cohort(self, payload: CohortCreateSchema):
        cohort = payload.model_dump_django()
        cohort.update_cohort_cases()
        return 201, cohort
        

    @route.get(
        path='/{cohortId}', 
        response={
            200: CohortSchema,
            404: None, 401: None, 403: None,
        },
        permissions=[perms.CanViewCohorts],
        operation_id='getCohortById',
    )
    def get_cohort_by_id(self, cohortId: str):
        return get_object_or_404(Cohort, id=cohortId)
        

    @route.delete(
        path='/{cohortId}', 
        response={
            204: None, 
            404: None, 401: None, 403: None,
        },
        permissions=[perms.CanManageCohorts],
        operation_id='deleteCohortById',
    )
    def delete_cohort(self, cohortId: str):
        get_object_or_404(Cohort, id=cohortId).delete()
        return 204, None
    
    
    @route.put(
        path='/{cohortId}', 
       response={
            200: ModifiedResourceSchema,
            404: None, 401: None, 403: None,
        },
        permissions=[perms.CanManageCohorts],
        operation_id='updateCohort',
    )
    def update_cohort(self, cohortId: str, payload: CohortCreateSchema):
        cohort = get_object_or_404(Cohort, id=cohortId)
        cohort = payload.model_dump_django(instance=cohort)
        cohort.update_cohort_cases()
        return cohort

    @route.get(
        path='/{cohortId}/cases', 
        response={
            200: Paginated[oncological_schemas.PatientCaseSchema],
            404: None, 401: None, 403: None,
        },
        permissions=[perms.CanViewCohorts],
        operation_id='getCohortCases',
    )
    @paginate()
    @anonymize()
    def get_cohort_cases(self, cohortId: str, anonymized: bool = True):
        return get_object_or_404(Cohort, id=cohortId).cases.all()

    @route.get(
        path='/{cohortId}/contributors', 
        response={
            200: List[CohortContribution],
            404: None, 401: None, 403: None,
        },
        permissions=[perms.CanViewCohorts],
        operation_id='getCohortContributors',
    )
    @paginate()
    def get_cohort_contributions(self, cohortId: str):
        cohort = get_object_or_404(Cohort, id=cohortId)
        contributions = Counter([contributor for case in cohort.cases.all() for contributor in case.contributors])
        return 200, [
            CohortContribution(contributor=contributor, contributions=contributions)
            for contributor, contributions in contributions.items() if contributor
        ]


    @route.get(
        path='/{cohortId}/history/events', 
        response={
            200: Paginated[HistoryEvent.bind_schema(CohortCreateSchema)],
            404: None, 401: None, 403: None,
        },
        permissions=[perms.CanViewCases],
        operation_id='getAllCohortHistoryEvents',
    )
    @paginate()
    def get_all_cohort_history_events(self, cohortId: str):
        instance = get_object_or_404(Cohort, id=cohortId)
        return pghistory.models.Events.objects.tracks(instance).all()

    @route.get(
        path='/{cohortId}/history/events/{eventId}', 
        response={
            200: HistoryEvent.bind_schema(CohortCreateSchema),
            404: None, 401: None, 403: None,
        },
        permissions=[perms.CanViewCases],
        operation_id='getCohortHistoryEventById',
    )
    def get_cohort_history_event_by_id(self, cohortId: str, eventId: str):
        instance = get_object_or_404(Cohort, id=cohortId)
        return get_object_or_404(pghistory.models.Events.objects.tracks(instance), pgh_id=eventId)

    @route.put(
        path='/{cohortId}/history/events/{eventId}/reversion', 
        response={
            201: ModifiedResourceSchema,
            404: None, 401: None, 403: None,
        },
        permissions=[perms.CanManageCases],
        operation_id='revertCohortToHistoryEvent',
    )
    def revert_cohort_to_history_event(self, cohortId: str, eventId: str):
        instance = get_object_or_404(Cohort, id=cohortId)
        return 201, get_object_or_404(instance.events, pgh_id=eventId).revert()
    
    @route.post(
        path='/{cohortId}/dataset/export', 
        response={
            200: Any,
            404: None, 401: None, 403: None,
        },
        permissions=[perms.CanExportData],
        operation_id='exportCohortDataset',
    )
    def export_cohort_dataset(self, cohortId: str, rules: List[DatasetRule]):
        cohort = get_object_or_404(Cohort, id=cohortId)
        dataset = [PatientCaseDataset.model_validate(subset) for subset in construct_dataset(cohort=cohort, rules=rules)]
        checksum = hashlib.md5(json.dumps([subset.model_dump(mode='json') for subset in dataset], sort_keys=True, default=str).encode('utf-8')).hexdigest()
        export = {
            **ExportMetadata(
                exportedAt=datetime.now(),
                exportedBy=self.context.request.user.username,
                exportVersion=settings.VERSION,
                checksum=checksum,
            ).model_dump(mode='json'),
            'dataset': dataset,
        }
        with pghistory.context(dataset=[rule.model_dump(mode='json') for rule in rules], checksum=checksum, version=settings.VERSION):
            pghistory.create_event(cohort, label="export")
        return 200, export

    
    @route.post(
        path='/{cohortId}/dataset', 
        response={
            200: Paginated[PatientCaseDataset],
            404: None, 401: None, 403: None,
        },
        permissions=[perms.CanViewCohorts],
        exclude_unset=True,
        operation_id='getCohortDatasetDynamically',
    )
    @paginate()
    def construct_cohort_dataset(self, cohortId: str, rules: List[DatasetRule]):
        return construct_dataset(cohort=get_object_or_404(Cohort, id=cohortId), rules=rules)

    @route.get(
        path='/{cohortId}/datasets/{datasetId}', 
        response={
            200: Paginated[PatientCaseDataset],
            404: None, 401: None, 403: None,
        },
        permissions=[perms.CanViewCohorts],
        operation_id='getCohortDataset',
    )
    @paginate()
    def get_cohort_dataset(self, cohortId: str, datasetId: str):
        return construct_dataset(
            cohort=get_object_or_404(Cohort, id=cohortId),
            rules=get_object_or_404(Dataset, id=datasetId).rules,
        )



    @route.get(
        path='/{cohortId}/traits/{trait}/average', 
        response={
            200: CohortTraitAverage,
            404: None, 422: None,
            401: None, 403: None,
        },
        permissions=[perms.CanViewCohorts],
        operation_id='getCohortTraitAverage',
    )
    def get_cohort_trait_average(self, cohortId: str, trait: str):
        cohort = get_object_or_404(Cohort, id=cohortId)
        if not cohort.cases.exists():
            raise EmptyCohortException
        average, standard_deviation = cohort.get_cohort_trait_average(convert_api_path_to_snake_case_path(trait))
        return 200, CohortTraitAverage(average=average, standardDeviation=standard_deviation)

    @route.get(
        path='/{cohortId}/traits/{trait}/median', 
        response={
            200: CohortTraitMedian,
            404: None, 422: None,
            401: None, 403: None,
        },
        permissions=[perms.CanViewCohorts],
        operation_id='getCohortTraitMedian',
    )
    def get_cohort_trait_median(self, cohortId: str, trait: str):
        cohort = get_object_or_404(Cohort, id=cohortId)
        if not cohort.cases.exists():
            raise EmptyCohortException
        median, iqr = cohort.get_cohort_trait_median(convert_api_path_to_snake_case_path(trait))
        return 200, CohortTraitMedian(median=median, interQuartalRange=iqr)

    @route.get(
        path='/{cohortId}/traits/{trait}/counts', 
        response={
            200: List[CohortTraitCounts],
            404: None, 422: None,
            401: None, 403: None,
        },
        permissions=[perms.CanViewCohorts],
        operation_id='getCohortTraitCounts',
    )
    def get_cohort_trait_counts(self, cohortId: str, trait: str):
        cohort = get_object_or_404(Cohort, id=cohortId)
        if not cohort.cases.exists():
            raise EmptyCohortException
        counter = cohort.get_cohort_trait_counts(convert_api_path_to_snake_case_path(trait))
        return 200, [CohortTraitCounts(category=category, counts=count, percentage=percentage) for category, (count, percentage) in counter.items()]


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
                oncological_schemas.TherapyLine.objects.filter(case_id=OuterRef('id'), label=therapyLine).annotate(
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