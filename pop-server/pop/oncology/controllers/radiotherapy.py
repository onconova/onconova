import pghistory
from typing import List

from ninja import Query
from ninja_extra.pagination import paginate
from ninja_extra.ordering import ordering
from ninja_extra import api_controller, ControllerBase, route

from pop.core.auth import permissions as perms
from pop.core.auth.token import XSessionTokenAuth
from pop.core.anonymization import anonymize
from pop.core.schemas import ModifiedResource as ModifiedResourceSchema, Paginated
from pop.core.history.schemas import HistoryEvent
from pop.oncology.models import (
    Radiotherapy,
    RadiotherapyDosage,
    RadiotherapySetting,
    TherapyLine,
)

from django.shortcuts import get_object_or_404
from django.db import transaction

from pop.oncology.schemas import (
    RadiotherapyFilters,
    RadiotherapySchema,
    RadiotherapyCreateSchema,
    RadiotherapyDosageSchema,
    RadiotherapyDosageCreateSchema,
    RadiotherapySettingSchema,
    RadiotherapySettingCreateSchema,
)


@api_controller(
    "radiotherapies",
    auth=[XSessionTokenAuth()],
    tags=["Radiotherapies"],
)
class RadiotherapyController(ControllerBase):

    @route.get(
        path="",
        response={
            200: Paginated[RadiotherapySchema],
        },
        permissions=[perms.CanViewCases],
        operation_id="getRadiotherapies",
    )
    @paginate()
    @ordering()
    @anonymize()
    def get_all_radiotherapies_matching_the_query(self, query: Query[RadiotherapyFilters], anonymized: bool = True):  # type: ignore
        queryset = Radiotherapy.objects.all().order_by("-period")
        return query.filter(queryset)

    @route.post(
        path="",
        response={
            201: ModifiedResourceSchema,
            401: None,
            403: None,
        },
        permissions=[perms.CanManageCases],
        operation_id="createRadiotherapy",
    )
    def create_radiotherapy(self, payload: RadiotherapyCreateSchema):  # type: ignore
        return 201, payload.model_dump_django().assign_therapy_line()

    @route.get(
        path="/{radiotherapyId}",
        response={
            200: RadiotherapySchema,
            404: None,
            401: None,
            403: None,
        },
        permissions=[perms.CanViewCases],
        operation_id="getRadiotherapyById",
    )
    @anonymize()
    def get_radiotherapy_by_id(self, radiotherapyId: str, anonymized: bool = True):
        return get_object_or_404(Radiotherapy, id=radiotherapyId)

    @route.delete(
        path="/{radiotherapyId}",
        response={
            204: None,
            404: None,
            401: None,
            403: None,
        },
        permissions=[perms.CanManageCases],
        operation_id="deleteRadiotherapyById",
    )
    def delete_radiotherapy(self, radiotherapyId: str):
        instance = get_object_or_404(Radiotherapy, id=radiotherapyId)
        case = instance.case
        instance.delete()
        TherapyLine.assign_therapy_lines(case)
        return 204, None

    @route.put(
        path="/{radiotherapyId}",
        response={
            200: ModifiedResourceSchema,
            404: None,
            401: None,
            403: None,
        },
        permissions=[perms.CanManageCases],
        operation_id="updateRadiotherapy",
    )
    def update_radiotherapy(self, radiotherapyId: str, payload: RadiotherapyCreateSchema):  # type: ignore
        instance = get_object_or_404(Radiotherapy, id=radiotherapyId)
        return payload.model_dump_django(instance=instance).assign_therapy_line()

    @route.get(
        path="/{radiotherapyId}/history/events",
        response={
            200: Paginated[HistoryEvent.bind_schema(RadiotherapyCreateSchema)],
            404: None,
            401: None,
            403: None,
        },
        permissions=[perms.CanViewCases],
        operation_id="getAllRadiotherapyHistoryEvents",
    )
    @paginate()
    @ordering()
    def get_all_radiotherapy_history_events(self, radiotherapyId: str):
        instance = get_object_or_404(Radiotherapy, id=radiotherapyId)
        return pghistory.models.Events.objects.tracks(instance).all()

    @route.get(
        path="/{radiotherapyId}/history/events/{eventId}",
        response={
            200: HistoryEvent.bind_schema(RadiotherapyCreateSchema),
            404: None,
            401: None,
            403: None,
        },
        permissions=[perms.CanViewCases],
        operation_id="getRadiotherapyHistoryEventById",
    )
    def get_radiotherapy_history_event_by_id(self, radiotherapyId: str, eventId: str):
        instance = get_object_or_404(Radiotherapy, id=radiotherapyId)
        return get_object_or_404(
            pghistory.models.Events.objects.tracks(instance), pgh_id=eventId
        )

    @route.put(
        path="/{radiotherapyId}/history/events/{eventId}/reversion",
        response={
            201: ModifiedResourceSchema,
            404: None,
            401: None,
            403: None,
        },
        permissions=[perms.CanManageCases],
        operation_id="revertRadiotherapyToHistoryEvent",
    )
    def revert_radiotherapy_to_history_event(self, radiotherapyId: str, eventId: str):
        instance = get_object_or_404(Radiotherapy, id=radiotherapyId)
        return 201, get_object_or_404(instance.events, pgh_id=eventId).revert()

    @route.get(
        path="/{radiotherapyId}/dosages",
        response={
            200: List[RadiotherapyDosageSchema],
            404: None,
            401: None,
            403: None,
        },
        permissions=[perms.CanViewCases],
        operation_id="getRadiotherapyDosages",
    )
    def get_radiotherapy_dosages_matching_the_query(self, radiotherapyId: str):  # type: ignore
        return get_object_or_404(Radiotherapy, id=radiotherapyId).dosages.all()

    @route.get(
        path="/{radiotherapyId}/dosages/{dosageId}",
        response={
            200: RadiotherapyDosageSchema,
            404: None,
            401: None,
            403: None,
        },
        permissions=[perms.CanViewCases],
        operation_id="getRadiotherapyDosageById",
    )
    def get_radiotherapy_dosage_by_id(self, radiotherapyId: str, dosageId: str):  # type: ignore
        return get_object_or_404(
            RadiotherapyDosage, id=dosageId, radiotherapy__id=radiotherapyId
        )

    @route.post(
        path="/{radiotherapyId}/dosages",
        response={
            201: ModifiedResourceSchema,
            401: None,
            403: None,
        },
        permissions=[perms.CanManageCases],
        operation_id="createRadiotherapyDosage",
    )
    def create_radiotherapy_dosage(self, radiotherapyId: str, payload: RadiotherapyDosageCreateSchema):  # type: ignore
        instance = RadiotherapyDosage(
            radiotherapy=get_object_or_404(Radiotherapy, id=radiotherapyId)
        )
        return 201, payload.model_dump_django(instance=instance, create=True)

    @route.put(
        path="/{radiotherapyId}/dosages/{dosageId}",
        response={
            200: ModifiedResourceSchema,
            404: None,
            401: None,
            403: None,
        },
        permissions=[perms.CanManageCases],
        operation_id="updateRadiotherapyDosage",
    )
    def update_radiotherapy_dosage(self, radiotherapyId: str, dosageId: str, payload: RadiotherapyDosageCreateSchema):  # type: ignore
        instance = get_object_or_404(
            RadiotherapyDosage, id=dosageId, radiotherapy__id=radiotherapyId
        )
        return payload.model_dump_django(instance=instance)

    @route.delete(
        path="/{radiotherapyId}/dosages/{dosageId}",
        response={
            204: None,
            404: None,
            401: None,
            403: None,
        },
        permissions=[perms.CanManageCases],
        operation_id="deleteRadiotherapyDosage",
    )
    def delete_radiotherapy_dosage(self, radiotherapyId: str, dosageId: str):
        get_object_or_404(
            RadiotherapyDosage, id=dosageId, radiotherapy__id=radiotherapyId
        ).delete()
        return 204, None

    @route.get(
        path="/{radiotherapyId}/dosages/{dosageId}/history/events",
        response={
            200: Paginated[HistoryEvent.bind_schema(RadiotherapyDosageCreateSchema)],
            404: None,
            401: None,
            403: None,
        },
        permissions=[perms.CanViewCases],
        operation_id="getAllRadiotherapyDosageHistoryEvents",
    )
    @paginate()
    @ordering()
    def get_all_radiotherapy_dosage_history_events(
        self, radiotherapyId: str, dosageId: str
    ):
        instance = get_object_or_404(
            RadiotherapyDosage, id=dosageId, radiotherapy__id=radiotherapyId
        )
        return pghistory.models.Events.objects.tracks(instance).all()

    @route.get(
        path="/{radiotherapyId}/dosages/{dosageId}/history/events/{eventId}",
        response={
            200: HistoryEvent.bind_schema(RadiotherapyDosageCreateSchema),
            404: None,
            401: None,
            403: None,
        },
        permissions=[perms.CanViewCases],
        operation_id="getRadiotherapyDosageHistoryEventById",
    )
    def get_radiotherapy_dosage_history_event_by_id(
        self, radiotherapyId: str, dosageId: str, eventId: str
    ):
        instance = get_object_or_404(
            RadiotherapyDosage, id=dosageId, radiotherapy__id=radiotherapyId
        )
        return get_object_or_404(
            pghistory.models.Events.objects.tracks(instance), pgh_id=eventId
        )

    @route.put(
        path="/{radiotherapyId}/dosages/{dosageId}/history/events/{eventId}/reversion",
        response={
            201: ModifiedResourceSchema,
            404: None,
            401: None,
            403: None,
        },
        permissions=[perms.CanManageCases],
        operation_id="revertRadiotherapyDosageToHistoryEvent",
    )
    def revert_radiotherapy_dosage_to_history_event(
        self, radiotherapyId: str, dosageId: str, eventId: str
    ):
        instance = get_object_or_404(
            RadiotherapyDosage, id=dosageId, radiotherapy__id=radiotherapyId
        )
        return 201, get_object_or_404(instance.events, pgh_id=eventId).revert()

    @route.get(
        path="/{radiotherapyId}/settings",
        response={
            200: List[RadiotherapySettingSchema],
            404: None,
            401: None,
            403: None,
        },
        permissions=[perms.CanViewCases],
        operation_id="getRadiotherapySettings",
    )
    def get_radiotherapy_settings_matching_the_query(self, radiotherapyId: str):  # type: ignore
        return get_object_or_404(Radiotherapy, id=radiotherapyId).settings.all()

    @route.get(
        path="/{radiotherapyId}/settings/{settingId}",
        response={
            200: RadiotherapySettingSchema,
            404: None,
            401: None,
            403: None,
        },
        permissions=[perms.CanViewCases],
        operation_id="getRadiotherapySettingById",
    )
    def get_radiotherapy_setting_by_id(self, radiotherapyId: str, settingId: str):  # type: ignore
        return get_object_or_404(
            RadiotherapySetting, id=settingId, radiotherapy__id=radiotherapyId
        )

    @route.post(
        path="/{radiotherapyId}/settings",
        response={
            201: ModifiedResourceSchema,
            401: None,
            403: None,
        },
        permissions=[perms.CanManageCases],
        operation_id="createRadiotherapySetting",
    )
    def create_radiotherapy_setting(self, radiotherapyId: str, payload: RadiotherapySettingCreateSchema):  # type: ignore
        instance = RadiotherapySetting(
            radiotherapy=get_object_or_404(Radiotherapy, id=radiotherapyId)
        )
        return 201, payload.model_dump_django(instance=instance, create=True)

    @route.put(
        path="/{radiotherapyId}/settings/{settingId}",
        response={
            200: ModifiedResourceSchema,
            404: None,
            401: None,
            403: None,
        },
        permissions=[perms.CanManageCases],
        operation_id="updateRadiotherapySetting",
    )
    def update_radiotherapy_setting(self, radiotherapyId: str, settingId: str, payload: RadiotherapySettingCreateSchema):  # type: ignore
        instance = get_object_or_404(
            RadiotherapySetting, id=settingId, radiotherapy__id=radiotherapyId
        )
        return payload.model_dump_django(instance=instance)

    @route.delete(
        path="/{radiotherapyId}/settings/{settingId}",
        response={
            204: None,
            404: None,
            401: None,
            403: None,
        },
        permissions=[perms.CanManageCases],
        operation_id="deleteRadiotherapySetting",
    )
    def delete_radiotherapy_setting(self, radiotherapyId: str, settingId: str):
        get_object_or_404(
            RadiotherapySetting, id=settingId, radiotherapy__id=radiotherapyId
        ).delete()
        return 204, None

    @route.get(
        path="/{radiotherapyId}/settings/{settingId}/history/events",
        response={
            200: Paginated[HistoryEvent.bind_schema(RadiotherapySettingCreateSchema)],
            404: None,
            401: None,
            403: None,
        },
        permissions=[perms.CanViewCases],
        operation_id="getAllRadiotherapySettingHistoryEvents",
    )
    @paginate()
    @ordering()
    def get_all_radiotherapy_setting_history_events(
        self, radiotherapyId: str, settingId: str
    ):
        instance = get_object_or_404(
            RadiotherapySetting, id=settingId, radiotherapy__id=radiotherapyId
        )
        return pghistory.models.Events.objects.tracks(instance).all()

    @route.get(
        path="/{radiotherapyId}/settings/{settingId}/history/events/{eventId}",
        response={
            200: HistoryEvent.bind_schema(RadiotherapySettingCreateSchema),
            404: None,
            401: None,
            403: None,
        },
        permissions=[perms.CanViewCases],
        operation_id="getRadiotherapySettingHistoryEventById",
    )
    def get_radiotherapy_setting_history_event_by_id(
        self, radiotherapyId: str, settingId: str, eventId: str
    ):
        instance = get_object_or_404(
            RadiotherapySetting, id=settingId, radiotherapy__id=radiotherapyId
        )
        return get_object_or_404(
            pghistory.models.Events.objects.tracks(instance), pgh_id=eventId
        )

    @route.put(
        path="/{radiotherapyId}/settings/{settingId}/history/events/{eventId}/reversion",
        response={
            201: ModifiedResourceSchema,
            404: None,
            401: None,
            403: None,
        },
        permissions=[perms.CanManageCases],
        operation_id="revertRadiotherapySettingToHistoryEvent",
    )
    def revert_radiotherapy_setting_to_history_event(
        self, radiotherapyId: str, settingId: str, eventId: str
    ):
        instance = get_object_or_404(
            RadiotherapySetting, id=settingId, radiotherapy__id=radiotherapyId
        )
        return 201, get_object_or_404(instance.events, pgh_id=eventId).revert()
