from typing import List, Union

import pghistory
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import QuerySet
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
    scm.UnspecifiedTumorBoard,
    scm.MolecularTumorBoard,
)

PAYLOAD_SCHEMAS = (
    scm.UnspecifiedTumorBoardCreate,
    scm.MolecularTumorBoardCreate,
)

AnyResponseSchemas = TypeAliasType("AnyTumorBoard", Union[RESPONSE_SCHEMAS])  # type: ignore# type: ignore
AnyPayloadSchemas = Union[PAYLOAD_SCHEMAS]


def cast_to_model_schema(model_instance, schemas, payload=None):
    return next(
        (
            schema.model_validate(payload or model_instance)
            for schema in schemas
            if (payload or model_instance).tumor_board_specialty
            == schema.model_fields["category"].default
        )
    )


@api_controller(
    "tumor-boards",
    auth=[XSessionTokenAuth()],
    tags=["Tumor Boards"],
)
class TumorBoardController(ControllerBase):

    @route.get(
        path="",
        response={
            200: Paginated[AnyResponseSchemas],
            **COMMON_HTTP_ERRORS,
        },
        exclude_none=True,
        permissions=[perms.CanViewCases],
        operation_id="getTumorBoards",
    )
    @paginate()
    @ordering()
    @anonymize()
    def get_all_tumor_boards_matching_the_query(self, query: Query[scm.TumorBoardFilters]):  # type: ignore
        queryset = orm.TumorBoard.objects.all().order_by("-date")
        return [
            cast_to_model_schema(tumorboard.specialized_tumor_board, RESPONSE_SCHEMAS)
            for tumorboard in query.filter(queryset)
        ]

    @route.post(
        path="",
        response={201: ModifiedResourceSchema, **COMMON_HTTP_ERRORS},
        permissions=[perms.CanManageCases],
        operation_id="createTumorBoard",
    )
    def create_tumor_board(self, payload: AnyPayloadSchemas):  # type: ignore
        return 201, payload.model_dump_django()

    @route.get(
        path="/{tumorBoardId}",
        response={200: AnyResponseSchemas, 404: None},
        exclude_none=True,
        permissions=[perms.CanViewCases],
        operation_id="getTumorBoardById",
    )
    @anonymize()
    def get_tumor_board_by_id(self, tumorBoardId: str):
        instance = get_object_or_404(orm.TumorBoard, id=tumorBoardId)
        return cast_to_model_schema(instance.specialized_tumor_board, RESPONSE_SCHEMAS)

    @route.put(
        path="/{tumorBoardId}",
        response={200: ModifiedResourceSchema, 404: None, **COMMON_HTTP_ERRORS},
        permissions=[perms.CanManageCases],
        operation_id="updateTumorBoardById",
    )
    def update_tumor_board(self, tumorBoardId: str, payload: AnyPayloadSchemas):  # type: ignore
        instance = get_object_or_404(
            orm.TumorBoard, id=tumorBoardId
        ).specialized_tumor_board
        return payload.model_dump_django(instance=instance)

    @route.delete(
        path="/{tumorBoardId}",
        response={204: None, 404: None, **COMMON_HTTP_ERRORS},
        permissions=[perms.CanManageCases],
        operation_id="deleteTumorBoardById",
    )
    def delete_tumor_board(self, tumorBoardId: str):
        instance = get_object_or_404(orm.TumorBoard, id=tumorBoardId)
        instance.delete()
        return 204, None

    @route.get(
        path="/{tumorBoardId}/history/events",
        response={200: Paginated[HistoryEvent], 404: None, **COMMON_HTTP_ERRORS},
        permissions=[perms.CanViewCases],
        operation_id="getAllTumorBoardHistoryEvents",
    )
    @paginate()
    @ordering()
    def get_all_tumor_board_history_events(self, tumorBoardId: str):
        instance = get_object_or_404(orm.TumorBoard, id=tumorBoardId)
        return pghistory.models.Events.objects.tracks(instance).all()  # type: ignore

    @route.get(
        path="/{tumorBoardId}/history/events/{eventId}",
        response={200: HistoryEvent, 404: None, **COMMON_HTTP_ERRORS},
        permissions=[perms.CanViewCases],
        operation_id="getTumorBoardHistoryEventById",
    )
    def get_tumor_board_history_event_by_id(self, tumorBoardId: str, eventId: str):
        instance = get_object_or_404(orm.TumorBoard, id=tumorBoardId)
        event = instance.parent_events.filter(pgh_id=eventId).first()  # type: ignore
        if not event and hasattr(instance, "events"):
            event = instance.events.filter(pgh_id=eventId).first()
        if not event:
            return 404, None
        return get_object_or_404(
            pghistory.models.Events.objects.tracks(instance), pgh_id=eventId  # type: ignore
        )

    @route.put(
        path="/{tumorBoardId}/history/events/{eventId}/reversion",
        response={201: ModifiedResourceSchema, 404: None, **COMMON_HTTP_ERRORS},
        permissions=[perms.CanManageCases],
        operation_id="revertTumorBoardToHistoryEvent",
    )
    def revert_tumor_board_to_history_event(self, tumorBoardId: str, eventId: str):
        instance = get_object_or_404(orm.TumorBoard, id=tumorBoardId)
        instance = instance.specialized_tumor_board
        try:
            return 201, revert_multitable_model(instance, eventId)
        except ObjectDoesNotExist:
            return 404, None


@api_controller(
    "molecular-tumor-boards",
    auth=[XSessionTokenAuth()],
    tags=["Tumor Boards"],
)
class MolecularTherapeuticRecommendationController(ControllerBase):

    @route.get(
        path="/{tumorBoardId}/therapeutic-recommendations",
        response={
            200: List[scm.MolecularTherapeuticRecommendation],
            404: None,
            **COMMON_HTTP_ERRORS,
        },
        permissions=[perms.CanViewCases],
        operation_id="getMolecularTherapeuticRecommendations",
    )
    def get_molecular_tumor_board_therapeutic_recommendations_matching_the_query(self, tumorBoardId: str):  # type: ignore
        return get_object_or_404(
            orm.MolecularTumorBoard, id=tumorBoardId
        ).therapeutic_recommendations.all()  # type: ignore

    @route.get(
        path="/{tumorBoardId}/therapeutic-recommendations/{recommendationId}",
        response={200: scm.MolecularTherapeuticRecommendation, 404: None},
        exclude_none=True,
        permissions=[perms.CanViewCases],
        operation_id="getMOlecularTherapeuticRecommendationById",
    )
    def get_molecular_tumor_board_therapeutic_recommendation_by_id(
        self, tumorBoardId: str, recommendationId: str
    ):
        return get_object_or_404(
            orm.MolecularTherapeuticRecommendation,
            id=recommendationId,
            molecular_tumor_board__id=tumorBoardId,
        )

    @route.post(
        path="/{tumorBoardId}/therapeutic-recommendations",
        response={201: ModifiedResourceSchema, **COMMON_HTTP_ERRORS},
        permissions=[perms.CanManageCases],
        operation_id="createMolecularTherapeuticRecommendation",
    )
    def create_molecular_tumor_board_therapeutic_recommendation(self, tumorBoardId: str, payload: scm.MolecularTherapeuticRecommendationCreate):  # type: ignore
        instance = orm.MolecularTherapeuticRecommendation(
            molecular_tumor_board=get_object_or_404(
                orm.MolecularTumorBoard, id=tumorBoardId
            )
        )
        return 201, payload.model_dump_django(instance=instance, create=True)

    @route.put(
        path="/{tumorBoardId}/therapeutic-recommendations/{recommendationId}",
        response={200: ModifiedResourceSchema, 404: None, **COMMON_HTTP_ERRORS},
        permissions=[perms.CanManageCases],
        operation_id="updateMolecularTherapeuticRecommendation",
    )
    def update_molecular_tumor_board_therapeutic_recommendation(self, tumorBoardId: str, recommendationId: str, payload: scm.MolecularTherapeuticRecommendationCreate):  # type: ignore
        instance = get_object_or_404(
            orm.MolecularTherapeuticRecommendation,
            id=recommendationId,
            molecular_tumor_board__id=tumorBoardId,
        )
        return payload.model_dump_django(instance=instance)

    @route.delete(
        path="/{tumorBoardId}/therapeutic-recommendations/{recommendationId}",
        response={204: None, 404: None, **COMMON_HTTP_ERRORS},
        permissions=[perms.CanManageCases],
        operation_id="deleteMolecularTherapeuticRecommendation",
    )
    def delete_molecular_tumor_board_therapeutic_recommendation(
        self, tumorBoardId: str, recommendationId: str
    ):
        instance = get_object_or_404(
            orm.MolecularTherapeuticRecommendation,
            id=recommendationId,
            molecular_tumor_board__id=tumorBoardId,
        )
        instance.delete()
        return 204, None

    @route.get(
        path="/{tumorBoardId}/therapeutic-recommendations/{recommendationId}/history/events",
        response={200: Paginated[HistoryEvent], 404: None, **COMMON_HTTP_ERRORS},
        permissions=[perms.CanViewCases],
        operation_id="getAllMolecularTherapeuticRecommendationHistoryEvents",
    )
    @paginate()
    @ordering()
    def get_all_molecular_tumor_board_therapeutic_history_events(
        self, tumorBoardId: str, recommendationId: str
    ):
        instance = get_object_or_404(
            orm.MolecularTherapeuticRecommendation,
            id=recommendationId,
            molecular_tumor_board__id=tumorBoardId,
        )
        return pghistory.models.Events.objects.tracks(instance).all()  # type: ignore

    @route.get(
        path="/{tumorBoardId}/therapeutic-recommendations/{recommendationId}/history/events/{eventId}",
        response={200: HistoryEvent, 404: None, **COMMON_HTTP_ERRORS},
        permissions=[perms.CanViewCases],
        operation_id="getMolecularTherapeuticRecommendationHistoryEventById",
    )
    def get_molecular_tumor_board_therapeutic_history_event_by_id(
        self, tumorBoardId: str, recommendationId: str, eventId: str
    ):
        instance = get_object_or_404(
            orm.MolecularTherapeuticRecommendation,
            id=recommendationId,
            molecular_tumor_board__id=tumorBoardId,
        )
        return get_object_or_404(
            pghistory.models.Events.objects.tracks(instance), pgh_id=eventId  # type: ignore
        )

    @route.put(
        path="/{tumorBoardId}/therapeutic-recommendations/{recommendationId}/history/events/{eventId}/reversion",
        response={201: ModifiedResourceSchema, 404: None, **COMMON_HTTP_ERRORS},
        permissions=[perms.CanManageCases],
        operation_id="revertMolecularTherapeuticRecommendationToHistoryEvent",
    )
    def revert_molecular_tumor_board_therapeutic_to_history_event(
        self, tumorBoardId: str, recommendationId: str, eventId: str
    ):
        instance = get_object_or_404(
            orm.MolecularTherapeuticRecommendation,
            id=recommendationId,
            molecular_tumor_board__id=tumorBoardId,
        )
        return 201, get_object_or_404(instance.events, pgh_id=eventId).revert()
