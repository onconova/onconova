import pghistory
from django.shortcuts import get_object_or_404

from collections import Counter
from typing import List, Any

from ninja import Query
from ninja_extra import route, api_controller
from ninja_jwt.authentication import JWTAuth
from ninja_extra.pagination import paginate
from ninja_extra import route, api_controller, status, ControllerBase
from ninja_extra.exceptions import APIException

from pop.core import permissions as perms
from pop.core.utils import camel_to_snake
from pop.core.models import User
from pop.core.schemas import Paginated, ModifiedResourceSchema, HistoryEvent
from pop.oncology import schemas as oncological_schemas

from pop.analytics.datasets import construct_dataset
from pop.analytics.models import Cohort, Dataset
from pop.analytics.schemas.cohort import (
    CohortSchema, CohortCreateSchema, 
    CohortFilters, CohortTraitAverage, 
    CohortTraitMedian, CohortTraitCounts,
    CohortContribution,
)
from pop.analytics.schemas.datasets import DatasetRule


def convert_api_path_to_snake_case_path(path):
    components = path.split('.')
    components = [camel_to_snake(component) for component in components]
    return '__'.join(components)



class EmptyCohortException(APIException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    default_detail = 'Unprocessable. Requested cohort is empty.'


@api_controller(
    "/cohorts", 
    auth=[JWTAuth()], 
    tags=["Cohorts"]
)
class CohortsController(ControllerBase):


    @route.get(
        path='', 
        response={
            200: Paginated[CohortSchema],
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
            201: ModifiedResourceSchema
        },
        permissions=[perms.CanManageCohorts],
        operation_id='createCohort',
    )
    def create_cohort(self, payload: CohortCreateSchema):
        cohort = payload.model_dump_django()
        cohort.update_cohort_cases()
        return cohort
        

    @route.get(
        path='/{cohortId}', 
        response={
            200: CohortSchema,
            404: None,
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
            404: None,
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
            404: None,
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
            404: None,
        },
        permissions=[perms.CanViewCohorts],
        operation_id='getCohortCases',
    )
    @paginate()
    def get_cohort_cases(self, cohortId: str):
        return get_object_or_404(Cohort, id=cohortId).cases.all()

    @route.get(
        path='/{cohortId}/contributors', 
        response={
            200: List[CohortContribution],
            404: None,
        },
        permissions=[perms.CanViewCohorts],
        operation_id='getCohortContributors',
    )
    @paginate()
    def get_cohort_contributions(self, cohortId: str):
        cohort = get_object_or_404(Cohort, id=cohortId)
        contributions = Counter(list(cohort.cases.select_properties('created_by').values_list('created_by', flat=True)))
        return 200, [
            CohortContribution(contributor=contributor, contributions=contributions)
            for contributor, contributions in contributions.items() if contributor
        ]


    @route.get(
        path='/{cohortId}/history/events', 
        response={
            200: Paginated[HistoryEvent],
            404: None,
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
            200: HistoryEvent,
            404: None,
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
            404: None,
        },
        permissions=[perms.CanManageCases],
        operation_id='revertCohortToHistoryEvent',
    )
    def revert_cohort_to_history_event(self, cohortId: str, eventId: str):
        instance = get_object_or_404(Cohort, id=cohortId)
        return 201, get_object_or_404(instance.events, pgh_id=eventId).revert()
    
    
    @route.post(
        path='/{cohortId}/dynamic-dataset', 
        response={
            200: Paginated[Any],
            404: None,
        },
        permissions=[perms.CanViewCohorts],
        operation_id='getCohortDatasetDynamically',
    )
    @paginate()
    def get_cohort_dataset_dynamically(self, cohortId: str, rules: List[DatasetRule]):
        return construct_dataset(cohort=get_object_or_404(Cohort, id=cohortId), rules=rules)

    @route.get(
        path='/{cohortId}/datasets/{datasetId}', 
        response={
            200: Paginated[Any],
            404: None,
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
            404: None,
            422: None,
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
            404: None,
            422: None,
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
            404: None,
            422: None,
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