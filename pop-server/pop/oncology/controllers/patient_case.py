from enum import Enum
from typing import Optional

import pghistory.models
from django.conf import settings
from django.db.models import Exists, OuterRef, Q
from django.shortcuts import get_object_or_404
from ninja import Query
from ninja_extra import ControllerBase, api_controller, route
from ninja_extra.ordering import ordering
from ninja_extra.pagination import paginate
from pop.core.anonymization import anonymize
from pop.core.auth import permissions as perms
from pop.core.auth.token import XSessionTokenAuth
from pop.core.history.schemas import HistoryEvent
from pop.core.schemas import ModifiedResource as ModifiedResourceSchema
from pop.core.schemas import Paginated
from pop.oncology.models import NeoplasticEntity, PatientCase, PatientCaseDataCompletion
from pop.oncology.schemas import (
    PatientCaseCreateSchema,
    PatientCaseDataCompletionStatusSchema,
)
from pop.oncology.schemas import PatientCaseFilters as PatientCaseFiltersBase
from pop.oncology.schemas import PatientCaseSchema


class PatientCaseIdentifier(str, Enum):
    ID = "id"
    PSEUDO = "pseudoidentifier"
    CLINICAL = "clinicalIdentifier"


class PatientCaseFilters(PatientCaseFiltersBase):
    primarySite: Optional[str] = None
    morphology: Optional[str] = None

    def filter_primarySite(self, value: bool) -> Q:
        return (
            Exists(
                NeoplasticEntity.objects.filter(
                    case_id=OuterRef("pk"),
                    topography_group__code=value,
                    relationship="primary",
                )
            )
            if value
            else Q()
        )

    def filter_morphology(self, value: bool) -> Q:
        return (
            Exists(
                NeoplasticEntity.objects.filter(
                    case_id=OuterRef("pk"),
                    morphology__code=value,
                    relationship="primary",
                )
            )
            if value
            else Q()
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
    @ordering()
    @anonymize()
    def get_all_patient_cases_matching_the_query(
        self,
        query: Query[PatientCaseFilters],
        anonymized: bool = True,
        idSearch: Optional[str] = None,
    ):  # type: ignore
        queryset = PatientCase.objects.all()
        if idSearch:
            id_query = Q(pseudoidentifier__icontains=idSearch) | Q(
                id__icontains=idSearch
            )
            if perms.CanManageCases.check_user_permission(
                self, self.context.request.user
            ):
                id_query = id_query | Q(clinical_identifier__icontains=idSearch)
            queryset = queryset.filter(id_query)
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
        response={
            200: PatientCaseSchema,
            404: None,
            401: None,
            403: None,
        },
        permissions=[perms.CanViewCases],
        operation_id="getPatientCaseById",
    )
    @anonymize()
    def get_patient_case_by_id(
        self,
        caseId: str,
        anonymized: bool = True,
        type: PatientCaseIdentifier = PatientCaseIdentifier.ID,
        clinicalCenter: str = None,
    ):
        if type == PatientCaseIdentifier.ID:
            return get_object_or_404(PatientCase, id=caseId.strip())
        elif type == PatientCaseIdentifier.PSEUDO:
            return get_object_or_404(PatientCase, pseudoidentifier=caseId.strip())
        elif type == PatientCaseIdentifier.CLINICAL:
            if not perms.CanManageCases.check_user_permission(
                self, self.context.request.user
            ):
                return 403, None
            if not clinicalCenter:
                raise ValueError(
                    "Clinical center must also be provided along the clinical identifier."
                )
            return get_object_or_404(
                PatientCase,
                clinical_identifier=caseId.strip(),
                clinical_center=clinicalCenter.strip(),
            )

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
    @ordering()
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
        return 201, PatientCaseDataCompletion.objects.create(
            case=get_object_or_404(PatientCase, id=caseId), category=category
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
