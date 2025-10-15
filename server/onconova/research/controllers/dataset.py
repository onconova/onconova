import pghistory
from django.shortcuts import get_object_or_404
from ninja import Query
from ninja.errors import HttpError
from ninja_extra import ControllerBase, api_controller, route
from ninja_extra.ordering import ordering
from ninja_extra.pagination import paginate

from onconova.core.auth import permissions as perms
from onconova.core.auth.token import XSessionTokenAuth
from onconova.core.history.schemas import HistoryEvent
from onconova.core.schemas import ModifiedResource as ModifiedResourceSchema
from onconova.core.schemas import Paginated
from onconova.core.utils import COMMON_HTTP_ERRORS
from onconova.research import (
    models as orm,
    schemas as scm,
)

@api_controller("/datasets", auth=[XSessionTokenAuth()], tags=["Datasets"])
class DatasetsController(ControllerBase):

    @route.get(
        path="",
        response={200: Paginated[scm.Dataset], **COMMON_HTTP_ERRORS},
        permissions=[perms.CanViewDatasets],
        operation_id="getDatasets",
    )
    @paginate()
    @ordering()
    def get_all_datasets_matching_the_query(self, query: Query[scm.DatasetFilters]):  # type: ignore
        queryset = orm.Dataset.objects.all().order_by("-created_at")
        return query.filter(queryset)  # type: ignore

    @route.post(
        path="",
        response={201: ModifiedResourceSchema, **COMMON_HTTP_ERRORS},
        permissions=[perms.CanManageDatasets],
        operation_id="createDataset",
    )
    def create_dataset(self, payload: scm.DatasetCreate):
        # Check that requesting user is a member of the project
        project = get_object_or_404(orm.Project, id=payload.projectId)  
        if (
            not project.is_member(self.context.request.user)  # type: ignore
            and self.context.request.user.access_level < 3  # type: ignore
        ):
            raise HttpError(403, "User is not a member of the project")
        return 201, payload.model_dump_django()

    @route.get(
        path="/{datasetId}",
        response={200: scm.Dataset, 404: None, **COMMON_HTTP_ERRORS},
        permissions=[perms.CanViewDatasets],
        operation_id="getDatasetById",
    )
    def get_dataset_by_id(self, datasetId: str):
        return get_object_or_404(orm.Dataset, id=datasetId)

    @route.delete(
        path="/{datasetId}",
        response={204: None, 404: None, **COMMON_HTTP_ERRORS},
        permissions=[perms.CanDeleteDatasets],
        operation_id="deleteDatasetById",
    )
    def delete_dataset(self, datasetId: str):
        get_object_or_404(orm.Dataset, id=datasetId).delete()
        return 204, None

    @route.put(
        path="/{datasetId}",
        response={200: ModifiedResourceSchema, 404: None, **COMMON_HTTP_ERRORS},
        permissions=[perms.CanManageDatasets],
        operation_id="updateDataset",
    )
    def update_dataset(self, datasetId: str, payload: scm.DatasetCreate):  # type: ignore
        return payload.model_dump_django(
            instance=self.get_object_or_exception(orm.Dataset, id=datasetId)
        )

    @route.get(
        path="/{datasetId}/history/events",
        response={
            200: Paginated[HistoryEvent.bind_schema(scm.DatasetCreate)],
            404: None,
            **COMMON_HTTP_ERRORS,
        },
        permissions=[perms.CanViewCases],
        operation_id="getAllDatasetHistoryEvents",
    )
    @paginate()
    @ordering()
    def get_all_dataset_history_events(self, datasetId: str):
        instance = get_object_or_404(orm.Dataset, id=datasetId)
        return pghistory.models.Events.objects.tracks(instance).all()  # type: ignore

    @route.get(
        path="/{datasetId}/history/events/{eventId}",
        response={
            200: HistoryEvent.bind_schema(scm.DatasetCreate),
            404: None,
            **COMMON_HTTP_ERRORS,
        },
        permissions=[perms.CanViewCases],
        operation_id="getDatasetHistoryEventById",
    )
    def get_dataset_history_event_by_id(self, datasetId: str, eventId: str):
        instance = get_object_or_404(orm.Dataset, id=datasetId)
        return get_object_or_404(
            pghistory.models.Events.objects.tracks(instance), pgh_id=eventId  # type: ignore
        )

    @route.put(
        path="/{datasetId}/history/events/{eventId}/reversion",
        response={201: ModifiedResourceSchema, 404: None, **COMMON_HTTP_ERRORS},
        permissions=[perms.CanManageCases],
        operation_id="revertDatasetToHistoryEvent",
    )
    def revert_dataset_to_history_event(self, datasetId: str, eventId: str):
        instance = get_object_or_404(orm.Dataset, id=datasetId)
        return 201, get_object_or_404(instance.events, pgh_id=eventId).revert()
