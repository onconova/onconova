from typing import Union

import pghistory
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from ninja import Query
from ninja_extra import ControllerBase, api_controller, route
from ninja_extra.ordering import ordering
from ninja_extra.pagination import paginate
from typing_extensions import TypeAliasType

from onconova.core.anonymization import anonymize
from onconova.core.auth import permissions as perms
from onconova.core.auth.token import XSessionTokenAuth
from onconova.core.history.schemas import HistoryEvent
from onconova.core.schemas import ModifiedResource as ModifiedResourceSchema
from onconova.core.schemas import Paginated
from onconova.core.utils import COMMON_HTTP_ERRORS, revert_multitable_model
from onconova.oncology import (
    models as orm,
    schemas as scm,
)

RESPONSE_SCHEMAS = (
    scm.TNMStaging,
    scm.FIGOStaging,
    scm.BinetStaging,
    scm.RaiStaging,
    scm.BreslowDepth,
    scm.ClarkStaging,
    scm.ISSStaging,
    scm.RISSStaging,
    scm.GleasonGrade,
    scm.INSSStage,
    scm.INRGSSStage,
    scm.WilmsStage,
    scm.RhabdomyosarcomaClinicalGroup,
    scm.LymphomaStaging,
)

PAYLOAD_SCHEMAS = (
    scm.TNMStagingCreate,
    scm.FIGOStagingCreate,
    scm.BinetStagingCreate,
    scm.RaiStagingCreate,
    scm.BreslowDepthCreate,
    scm.ClarkStagingCreate,
    scm.ISSStagingCreate,
    scm.RISSStagingCreate,
    scm.GleasonGradeCreate,
    scm.INSSStageCreate,
    scm.INRGSSStageCreate,
    scm.WilmsStageCreate,
    scm.RhabdomyosarcomaClinicalGroupCreate,
    scm.LymphomaStagingCreate,
)

AnyResponseSchemas = TypeAliasType("AnyStaging", Union[RESPONSE_SCHEMAS])  # type: ignore# type: ignore
AnyPayloadSchemas = Union[PAYLOAD_SCHEMAS]


def cast_to_model_schema(model_instance, schemas, payload=None):
    return next(
        (
            schema.model_validate(payload or model_instance)
            for schema in schemas
            if (
                payload
                and payload.stagingDomain
                == schema.model_fields["stagingDomain"].default
            )
            or (
                model_instance
                and model_instance.staging_domain
                == schema.model_fields["stagingDomain"].default
            )
        )
    )


@api_controller(
    "stagings",
    auth=[XSessionTokenAuth()],
    tags=["Stagings"],
)
class StagingController(ControllerBase):

    @route.get(
        path="",
        response={
            200: Paginated[AnyResponseSchemas],
            **COMMON_HTTP_ERRORS,
        },
        permissions=[perms.CanViewCases],
        exclude_none=True,
        operation_id="getStagings",
    )
    @paginate()
    @ordering()
    @anonymize()
    def get_all_stagings_matching_the_query(self, query: Query[scm.StagingFilters]):  # type: ignore
        queryset = orm.Staging.objects.all().order_by("-date")
        return [
            cast_to_model_schema(staging.get_domain_staging(), RESPONSE_SCHEMAS)
            for staging in query.filter(queryset)
        ]

    @route.post(
        path="",
        response={201: ModifiedResourceSchema, **COMMON_HTTP_ERRORS},
        permissions=[perms.CanManageCases],
        operation_id="createStaging",
    )
    def create_staging(self, payload: AnyPayloadSchemas):  # type: ignore
        return 201, payload.model_dump_django()

    @route.get(
        path="/{stagingId}",
        response={200: AnyResponseSchemas, 404: None},
        permissions=[perms.CanViewCases],
        exclude_none=True,
        operation_id="getStagingById",
    )
    @anonymize()
    def get_staging_by_id(self, stagingId: str):
        instance = get_object_or_404(orm.Staging, id=stagingId)
        return cast_to_model_schema(instance.get_domain_staging(), RESPONSE_SCHEMAS)

    @route.put(
        path="/{stagingId}",
        response={200: ModifiedResourceSchema, 404: None, **COMMON_HTTP_ERRORS},
        permissions=[perms.CanManageCases],
        operation_id="updateStagingById",
    )
    def update_staging(self, stagingId: str, payload: AnyPayloadSchemas):  # type: ignore
        instance = get_object_or_404(orm.Staging, id=stagingId)
        return cast_to_model_schema(
            instance.get_domain_staging(), PAYLOAD_SCHEMAS, payload
        ).model_dump_django(instance=instance.get_domain_staging()) 

    @route.delete(
        path="/{stagingId}",
        response={204: None, 404: None, **COMMON_HTTP_ERRORS},
        permissions=[perms.CanManageCases],
        operation_id="deleteStagingById",
    )
    def delete_staging(self, stagingId: str):
        instance = get_object_or_404(orm.Staging, id=stagingId)
        instance.delete()
        return 204, None

    @route.get(
        path="/{stagingId}/history/events",
        response={200: Paginated[HistoryEvent], 404: None, **COMMON_HTTP_ERRORS},
        permissions=[perms.CanViewCases],
        operation_id="getAllStagingHistoryEvents",
    )
    @paginate()
    @ordering()
    def get_all_staging_history_events(self, stagingId: str):
        instance = get_object_or_404(orm.Staging, id=stagingId)
        return pghistory.models.Events.objects.tracks(instance).all()  # type: ignore

    @route.get(
        path="/{stagingId}/history/events/{eventId}",
        response={200: HistoryEvent, 404: None, **COMMON_HTTP_ERRORS},
        permissions=[perms.CanViewCases],
        operation_id="getStagingHistoryEventById",
    )
    def get_staging_history_event_by_id(self, stagingId: str, eventId: str):
        instance = get_object_or_404(orm.Staging, id=stagingId)
        event = instance.parent_events.filter(pgh_id=eventId).first()  # type: ignore
        if not event and hasattr(instance, "events"):
            event = instance.events.filter(pgh_id=eventId).first()
        if not event:
            return 404, None
        return get_object_or_404(
            pghistory.models.Events.objects.tracks(instance), pgh_id=eventId  # type: ignore
        )

    @route.put(
        path="/{stagingId}/history/events/{eventId}/reversion",
        response={201: ModifiedResourceSchema, 404: None, **COMMON_HTTP_ERRORS},
        permissions=[perms.CanManageCases],
        operation_id="revertStagingToHistoryEvent",
    )
    def revert_staging_to_history_event(self, stagingId: str, eventId: str):
        instance = get_object_or_404(orm.Staging, id=stagingId)
        instance = instance.get_domain_staging()
        try:
            return 201, revert_multitable_model(instance, eventId)
        except ObjectDoesNotExist:
            return 404, None
