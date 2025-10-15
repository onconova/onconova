from typing import List

import pghistory
from django.db import transaction
from django.shortcuts import get_object_or_404
from ninja import Query
from ninja_extra import ControllerBase, api_controller, route
from ninja_extra.ordering import ordering
from ninja_extra.pagination import paginate

from onconova.core.anonymization import anonymize
from onconova.core.auth import permissions as perms
from onconova.core.auth.token import XSessionTokenAuth
from onconova.core.history.schemas import HistoryEvent
from onconova.core.schemas import ModifiedResource as ModifiedResourceSchema
from onconova.core.schemas import Paginated
from onconova.core.utils import COMMON_HTTP_ERRORS
from onconova.oncology import (
    models as orm,
    schemas as scm,
)


@api_controller(
    "systemic-therapies",
    auth=[XSessionTokenAuth()],
    tags=["Systemic Therapies"],
)
class SystemicTherapyController(ControllerBase):

    @route.get(
        path="",
        response={
            200: Paginated[scm.SystemicTherapy],
            **COMMON_HTTP_ERRORS,
        },
        permissions=[perms.CanViewCases],
        operation_id="getSystemicTherapies",
    )
    @paginate()
    @ordering()
    @anonymize()
    def get_all_systemic_therapies_matching_the_query(self, query: Query[scm.SystemicTherapyFilters]):  # type: ignore
        queryset = orm.SystemicTherapy.objects.all().order_by("-period")
        return query.filter(queryset)

    @route.post(
        path="",
        response={201: ModifiedResourceSchema, **COMMON_HTTP_ERRORS},
        permissions=[perms.CanManageCases],
        operation_id="createSystemicTherapy",
    )
    def create_systemic_therapy(self, payload: scm.SystemicTherapyCreate):
        return 201, payload.model_dump_django().assign_therapy_line()

    @route.get(
        path="/{systemicTherapyId}",
        response={200: scm.SystemicTherapy, 404: None, **COMMON_HTTP_ERRORS},
        permissions=[perms.CanViewCases],
        operation_id="getSystemicTherapyById",
    )
    @anonymize()
    def get_systemic_therapy_by_id(self, systemicTherapyId: str):
        return get_object_or_404(orm.SystemicTherapy, id=systemicTherapyId)

    @route.delete(
        path="/{systemicTherapyId}",
        response={204: None, 404: None, **COMMON_HTTP_ERRORS},
        permissions=[perms.CanManageCases],
        operation_id="deleteSystemicTherapyById",
    )
    def delete_systemic_therapy(self, systemicTherapyId: str):
        instance = get_object_or_404(orm.SystemicTherapy, id=systemicTherapyId)
        case = instance.case
        instance.delete()
        orm.TherapyLine.assign_therapy_lines(case)
        return 204, None

    @route.put(
        path="/{systemicTherapyId}",
        response={200: ModifiedResourceSchema, 404: None, **COMMON_HTTP_ERRORS},
        permissions=[perms.CanManageCases],
        operation_id="updateSystemicTherapy",
    )
    def update_systemic_therapy(self, systemicTherapyId: str, payload: scm.SystemicTherapyCreate):
        instance = get_object_or_404(orm.SystemicTherapy, id=systemicTherapyId)
        return payload.model_dump_django(instance=instance).assign_therapy_line()

    @route.get(
        path="/{systemicTherapyId}/history/events",
        response={
            200: Paginated[HistoryEvent.bind_schema(scm.SystemicTherapyCreate)],
            404: None,
            **COMMON_HTTP_ERRORS,
        },
        permissions=[perms.CanViewCases],
        operation_id="getAllSystemicTherapyHistoryEvents",
    )
    @paginate()
    @ordering()
    def get_all_systemic_therapy_history_events(self, systemicTherapyId: str):
        instance = get_object_or_404(orm.SystemicTherapy, id=systemicTherapyId)
        return pghistory.models.Events.objects.tracks(instance).all()  # type: ignore

    @route.get(
        path="/{systemicTherapyId}/history/events/{eventId}",
        response={
            200: HistoryEvent.bind_schema(scm.SystemicTherapyCreate),
            404: None,
            **COMMON_HTTP_ERRORS,
        },
        permissions=[perms.CanViewCases],
        operation_id="getSystemicTherapyHistoryEventById",
    )
    def get_systemic_therapy_history_event_by_id(
        self, systemicTherapyId: str, eventId: str
    ):
        instance = get_object_or_404(orm.SystemicTherapy, id=systemicTherapyId)
        return get_object_or_404(
            pghistory.models.Events.objects.tracks(instance), pgh_id=eventId  # type: ignore
        )

    @route.put(
        path="/{systemicTherapyId}/history/events/{eventId}/reversion",
        response={201: ModifiedResourceSchema, 404: None, **COMMON_HTTP_ERRORS},
        permissions=[perms.CanManageCases],
        operation_id="revertSystemicTherapyToHistoryEvent",
    )
    def revert_systemic_therapy_to_history_event(
        self, systemicTherapyId: str, eventId: str
    ):
        instance = get_object_or_404(orm.SystemicTherapy, id=systemicTherapyId)
        return 201, get_object_or_404(instance.events, pgh_id=eventId).revert()

    @route.get(
        path="/{systemicTherapyId}/medications",
        response={
            200: List[scm.SystemicTherapyMedication],
            404: None,
            **COMMON_HTTP_ERRORS,
        },
        permissions=[perms.CanViewCases],
        operation_id="getSystemicTherapyMedications",
    )
    def get_systemic_therapy_medications_matching_the_query(self, systemicTherapyId: str):  # type: ignore
        return get_object_or_404(
            orm.SystemicTherapy, id=systemicTherapyId
        ).medications.all()  # type: ignore

    @route.get(
        path="/{systemicTherapyId}/medications/{medicationId}",
        response={
            200: scm.SystemicTherapyMedication,
            404: None,
            **COMMON_HTTP_ERRORS,
        },
        permissions=[perms.CanViewCases],
        operation_id="getSystemicTherapyMedicationById",
    )
    def get_systemic_therapy_medication_by_id(self, systemicTherapyId: str, medicationId: str):  # type: ignore
        return get_object_or_404(
            orm.SystemicTherapyMedication,
            id=medicationId,
            systemic_therapy__id=systemicTherapyId,
        )

    @route.post(
        path="/{systemicTherapyId}/medications",
        response={201: ModifiedResourceSchema, **COMMON_HTTP_ERRORS},
        permissions=[perms.CanManageCases],
        operation_id="createSystemicTherapyMedication",
    )
    def create_systemic_therapy_medication(self, systemicTherapyId: str, payload: scm.SystemicTherapyMedicationCreate):  
        instance = orm.SystemicTherapyMedication(
            systemic_therapy=get_object_or_404(orm.SystemicTherapy, id=systemicTherapyId)
        )
        return 201, payload.model_dump_django(instance=instance, create=True)

    @route.put(
        path="/{systemicTherapyId}/medications/{medicationId}",
        response={200: ModifiedResourceSchema, 404: None, **COMMON_HTTP_ERRORS},
        permissions=[perms.CanManageCases],
        operation_id="updateSystemicTherapyMedication",
    )
    def update_systemic_therapy_medication(self, systemicTherapyId: str, medicationId: str, payload: scm.SystemicTherapyMedicationCreate):  
        instance = get_object_or_404(
            orm.SystemicTherapyMedication,
            id=medicationId,
            systemic_therapy__id=systemicTherapyId,
        )
        return payload.model_dump_django(instance=instance)

    @route.delete(
        path="/{systemicTherapyId}/medications/{medicationId}",
        response={204: None, 404: None, **COMMON_HTTP_ERRORS},
        permissions=[perms.CanManageCases],
        operation_id="deleteSystemicTherapyMedication",
    )
    def delete_systemic_therapy_medication(
        self, systemicTherapyId: str, medicationId: str
    ):
        instance = get_object_or_404(
            orm.SystemicTherapyMedication,
            id=medicationId,
            systemic_therapy__id=systemicTherapyId,
        )
        case = instance.systemic_therapy.case
        instance.delete()
        orm.TherapyLine.assign_therapy_lines(case)
        return 204, None

    @route.get(
        path="/{systemicTherapyId}/medications/{medicationId}/history/events",
        response={
            200: Paginated[
                HistoryEvent.bind_schema(scm.SystemicTherapyMedicationCreate)
            ],
            404: None,
            **COMMON_HTTP_ERRORS,
        },
        permissions=[perms.CanViewCases],
        operation_id="getAllSystemicTherapyMedicationHistoryEvents",
    )
    @paginate()
    @ordering()
    def get_all_systemic_therapy_medication_history_events(
        self, systemicTherapyId: str, medicationId: str
    ):
        instance = get_object_or_404(
            orm.SystemicTherapyMedication,
            id=medicationId,
            systemic_therapy__id=systemicTherapyId,
        )
        return pghistory.models.Events.objects.tracks(instance).all()  # type: ignore

    @route.get(
        path="/{systemicTherapyId}/medications/{medicationId}/history/events/{eventId}",
        response={
            200: HistoryEvent.bind_schema(scm.SystemicTherapyMedicationCreate),
            404: None,
            **COMMON_HTTP_ERRORS,
        },
        permissions=[perms.CanViewCases],
        operation_id="getSystemicTherapyMedicationHistoryEventById",
    )
    def get_systemic_therapy_medication_history_event_by_id(
        self, systemicTherapyId: str, medicationId: str, eventId: str
    ):
        instance = get_object_or_404(
            orm.SystemicTherapyMedication,
            id=medicationId,
            systemic_therapy__id=systemicTherapyId,
        )
        return get_object_or_404(
            pghistory.models.Events.objects.tracks(instance), pgh_id=eventId  # type: ignore
        )

    @route.put(
        path="/{systemicTherapyId}/medications/{medicationId}/history/events/{eventId}/reversion",
        response={201: ModifiedResourceSchema, 404: None, **COMMON_HTTP_ERRORS},
        permissions=[perms.CanManageCases],
        operation_id="revertSystemicTherapyMedicationToHistoryEvent",
    )
    def revert_systemic_therapy_medication_to_history_event(
        self, systemicTherapyId: str, medicationId: str, eventId: str
    ):
        instance = get_object_or_404(
            orm.SystemicTherapyMedication,
            id=medicationId,
            systemic_therapy__id=systemicTherapyId,
        )
        return 201, get_object_or_404(instance.events, pgh_id=eventId).revert()
