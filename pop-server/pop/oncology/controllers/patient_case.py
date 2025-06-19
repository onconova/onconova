import pghistory.models

from ninja import Query
from ninja_extra.pagination import paginate
from ninja_extra import api_controller, ControllerBase, route

from django.shortcuts import get_object_or_404
from django.conf import settings

from pop.core.auth import permissions as perms
from pop.core.schemas import ModifiedResource as ModifiedResourceSchema, Paginated
from pop.core.history.schemas import HistoryEvent
from pop.core.auth.token import XSessionTokenAuth
from pop.core.anonymization import anonymize
from pop.oncology.models import PatientCase, PatientCaseDataCompletion
from pop.oncology.schemas import (
    PatientCaseSchema,
    PatientCaseCreateSchema,
    PatientCaseFilters,
    PatientCaseDataCompletionStatusSchema,
)


@api_controller(
    "patient-cases",
    auth=[XSessionTokenAuth()],
    tags=["Patient Cases"],
)
class PatientCaseController(ControllerBase):

    @route.get(
        path="",
        response={200: Paginated[PatientCaseSchema]},
        permissions=[perms.CanViewCases],
        operation_id="getPatientCases",
    )
    @paginate()
    @anonymize()
    def get_all_patient_cases_matching_the_query(self, query: Query[PatientCaseFilters], anonymized: bool = True):  # type: ignore
        queryset = PatientCase.objects.all().order_by("-created_at")
        return query.filter(queryset)

    @route.post(
        path="",
        response={
            201: ModifiedResourceSchema,
            401: None,
            403: None,
        },
        permissions=[perms.CanManageCases],
        operation_id="createPatientCase",
    )
    def create_patient_case(self, payload: PatientCaseCreateSchema):
        return 201, payload.model_dump_django()

    @route.get(
        path="/{caseId}",
        response={200: PatientCaseSchema, 404: None},
        permissions=[perms.CanViewCases],
        operation_id="getPatientCaseById",
    )
    @anonymize()
    def get_patient_case_by_id(self, caseId: str, anonymized: bool = True):
        return get_object_or_404(PatientCase, id=caseId)

    @route.get(
        path="/pseudo/{pseudoidentifier}",
        response={200: PatientCaseSchema, 404: None},
        permissions=[perms.CanViewCases],
        operation_id="getPatientCaseByPseudoidentifier",
    )
    @anonymize()
    def get_patient_case_by_pseudoidentifier(
        self, pseudoidentifier: str, anonymized: bool = True
    ):
        return get_object_or_404(PatientCase, pseudoidentifier=pseudoidentifier.strip())

    @route.put(
        path="/{caseId}",
        response={
            200: ModifiedResourceSchema,
            404: None,
            401: None,
            403: None,
        },
        permissions=[perms.CanManageCases],
        operation_id="updatePatientCaseById",
    )
    def update_patient_case(self, caseId: str, payload: PatientCaseCreateSchema):  # type: ignore
        instance = get_object_or_404(PatientCase, id=caseId)
        return PatientCaseCreateSchema.model_validate(payload).model_dump_django(
            instance=instance
        )

    @route.delete(
        path="/{caseId}",
        response={
            204: None,
            404: None,
            401: None,
            403: None,
        },
        permissions=[perms.CanManageCases],
        operation_id="deletePatientCaseById",
    )
    def delete_patient_case(self, caseId: str):
        instance = get_object_or_404(PatientCase, id=caseId)
        instance.delete()
        return 204, None

    @route.get(
        path="/{caseId}/history/events",
        response={
            200: Paginated[HistoryEvent.bind_schema(PatientCaseCreateSchema)],
            404: None,
            401: None,
            403: None,
        },
        permissions=[perms.CanViewCases],
        operation_id="getAllPatientCaseHistoryEvents",
    )
    @paginate()
    def get_all_patient_case_history_events(self, caseId: str):
        instance = get_object_or_404(PatientCase, id=caseId)
        return pghistory.models.Events.objects.tracks(instance).all()

    @route.get(
        path="/{caseId}/history/events/{eventId}",
        response={
            200: HistoryEvent.bind_schema(PatientCaseCreateSchema),
            404: None,
            401: None,
            403: None,
        },
        permissions=[perms.CanViewCases],
        operation_id="getPatientCaseHistoryEventById",
    )
    def get_patient_case_history_event_by_id(self, caseId: str, eventId: str):
        instance = get_object_or_404(PatientCase, id=caseId)
        return get_object_or_404(
            pghistory.models.Events.objects.tracks(instance), pgh_id=eventId
        )

    @route.put(
        path="/{caseId}/history/events/{eventId}/reversion",
        response={
            201: ModifiedResourceSchema,
            404: None,
            401: None,
            403: None,
        },
        permissions=[perms.CanManageCases],
        operation_id="revertPatientCaseToHistoryEvent",
    )
    def revert_patient_case_to_history_event(self, caseId: str, eventId: str):
        instance = get_object_or_404(PatientCase, id=caseId)
        return 201, get_object_or_404(instance.events, pgh_id=eventId).revert()

    @route.get(
        path="/{caseId}/data-completion/{category}",
        response={
            200: PatientCaseDataCompletionStatusSchema,
            404: None,
            401: None,
            403: None,
        },
        permissions=[perms.CanViewCases],
        operation_id="getPatientCaseDataCompletionStatus",
    )
    def get_patient_case_data_completion_status(
        self, caseId: str, category: PatientCaseDataCompletion.PatientCaseDataCategories
    ):
        category_completion = PatientCaseDataCompletion.objects.filter(
            case__id=caseId, category=category
        ).first()
        return PatientCaseDataCompletionStatusSchema(
            status=category_completion is not None,
            username=category_completion.created_by if category_completion else None,
            timestamp=category_completion.created_at if category_completion else None,
        )

    @route.post(
        path="/{caseId}/data-completion/{category}",
        response={
            201: ModifiedResourceSchema,
            404: None,
            401: None,
            403: None,
        },
        permissions=[perms.CanManageCases],
        operation_id="createPatientCaseDataCompletion",
    )
    def create_patient_case_data_completion(
        self, caseId: str, category: PatientCaseDataCompletion.PatientCaseDataCategories
    ):
        return PatientCaseDataCompletion.objects.create(
            case=get_object_or_404(PatientCase, id=caseId),
            category=category,
            created_by=self.context.request.user,
        )

    @route.delete(
        path="/{caseId}/data-completion/{category}",
        response={
            204: None,
            404: None,
            401: None,
            403: None,
        },
        permissions=[perms.CanManageCases],
        operation_id="deletePatientCaseDataCompletion",
    )
    def delete_patient_case_data_completion(
        self, caseId: str, category: PatientCaseDataCompletion.PatientCaseDataCategories
    ):
        instance = get_object_or_404(
            PatientCaseDataCompletion, case__id=caseId, category=category
        )
        instance.delete()
        return 204, None


@api_controller(
    "others",
    auth=[XSessionTokenAuth()],
    tags=["Patient Cases"],
)
class OthersController(ControllerBase):
    @route.get(
        path="/default-clinical-center",
        response={
            200: str,
            501: None,
        },
        operation_id="getDefaultClinicalCenter",
    )
    def get_default_clinical_center(self):  # type: ignore
        clinical_center = getattr(settings, "HOST_ORGANIZATION", None)
        if clinical_center:
            return 200, clinical_center
        else:
            return 501, None

    @route.get(
        path="/clinical-centers",
        response={
            200: list[str],
            501: None,
        },
        operation_id="getClinicalCenters",
    )
    def get_clinical_centers(self, query: str = ""):
        queryset = PatientCase.objects.all()
        if query:
            queryset = queryset.filter(clinical_center__icontains=query)
        return queryset.values_list("clinical_center", flat=True).distinct()
