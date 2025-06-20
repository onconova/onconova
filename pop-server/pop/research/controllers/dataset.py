import pghistory
from django.shortcuts import get_object_or_404


from ninja import Query
from ninja.errors import HttpError
from ninja_extra import route, api_controller
from ninja_extra.pagination import paginate
from ninja_extra import api_controller, ControllerBase, route

from pop.core.auth import permissions as perms
from pop.core.auth.token import XSessionTokenAuth
from pop.core.schemas import ModifiedResource as ModifiedResourceSchema, Paginated
from pop.core.history.schemas import HistoryEvent

from pop.research.models.dataset import Dataset
from pop.research.models.project import Project
from pop.research.schemas.dataset import (
    Dataset as DatasetSchema,
    DatasetCreate as DatasetCreateSchema,
    DatasetFilters,
)


@api_controller("/datasets", auth=[XSessionTokenAuth()], tags=["Datasets"])
class DatasetsController(ControllerBase):

    @route.get(
        path="",
        response={
            200: Paginated[DatasetSchema],
            401: None,
            403: None,
        },
        permissions=[perms.CanViewDatasets],
        operation_id="getDatasets",
    )
    @paginate()
    def get_all_datasets_matching_the_query(self, query: Query[DatasetFilters]):  # type: ignore
        queryset = Dataset.objects.all().order_by("-created_at")
        return query.filter(queryset)

    @route.post(
        path="",
        response={
            201: ModifiedResourceSchema,
            401: None,
            403: None,
        },
        permissions=[perms.CanManageDatasets],
        operation_id="createDataset",
    )
    def create_dataset(self, payload: DatasetCreateSchema):  # type: ignore
        # Check that requesting user is a member of the project
        project = get_object_or_404(Project, id=payload.projectId)
        if (
            not project.is_member(self.context.request.user)
            and self.context.request.user.access_level < 3
        ):
            raise HttpError(403, "User is not a member of the project")
        return 201, payload.model_dump_django()

    @route.get(
        path="/{datasetId}",
        response={
            200: DatasetSchema,
            404: None,
            401: None,
            403: None,
        },
        permissions=[perms.CanViewDatasets],
        operation_id="getDatasetById",
    )
    def get_dataset_by_id(self, datasetId: str):
        return get_object_or_404(Dataset, id=datasetId)

    @route.delete(
        path="/{datasetId}",
        response={
            204: None,
            404: None,
            401: None,
            403: None,
        },
        permissions=[perms.CanDeleteDatasets],
        operation_id="deleteDatasetById",
    )
    def delete_dataset(self, datasetId: str):
        get_object_or_404(Dataset, id=datasetId).delete()
        return 204, None

    @route.put(
        path="/{datasetId}",
        response={
            200: ModifiedResourceSchema,
            404: None,
            401: None,
            403: None,
        },
        permissions=[perms.CanManageDatasets],
        operation_id="updateDataset",
    )
    def update_dataset(self, datasetId: str, payload: DatasetCreateSchema):  # type: ignore
        return payload.model_dump_django(
            instance=self.get_object_or_exception(Dataset, id=datasetId)
        )

    @route.get(
        path="/{datasetId}/history/events",
        response={
            200: Paginated[HistoryEvent.bind_schema(DatasetCreateSchema)],
            404: None,
            401: None,
            403: None,
        },
        permissions=[perms.CanViewCases],
        operation_id="getAllDatasetHistoryEvents",
    )
    @paginate()
    def get_all_dataset_history_events(self, datasetId: str):
        instance = get_object_or_404(Dataset, id=datasetId)
        return pghistory.models.Events.objects.tracks(instance).all()

    @route.get(
        path="/{datasetId}/history/events/{eventId}",
        response={
            200: HistoryEvent.bind_schema(DatasetCreateSchema),
            404: None,
            401: None,
            403: None,
        },
        permissions=[perms.CanViewCases],
        operation_id="getDatasetHistoryEventById",
    )
    def get_dataset_history_event_by_id(self, datasetId: str, eventId: str):
        instance = get_object_or_404(Dataset, id=datasetId)
        return get_object_or_404(
            pghistory.models.Events.objects.tracks(instance), pgh_id=eventId
        )

    @route.put(
        path="/{datasetId}/history/events/{eventId}/reversion",
        response={
            201: ModifiedResourceSchema,
            404: None,
            401: None,
            403: None,
        },
        permissions=[perms.CanManageCases],
        operation_id="revertDatasetToHistoryEvent",
    )
    def revert_dataset_to_history_event(self, datasetId: str, eventId: str):
        instance = get_object_or_404(Dataset, id=datasetId)
        return 201, get_object_or_404(instance.events, pgh_id=eventId).revert()
