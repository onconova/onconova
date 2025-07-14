import pghistory
import hashlib
import json
from enum import Enum
from typing import Any
from datetime import datetime
from ninja_extra.pagination import paginate
from ninja_extra.ordering import ordering
from ninja_extra import api_controller, ControllerBase, route, status
from ninja_extra.exceptions import APIException

from django.conf import settings
from django.db import transaction
from django.shortcuts import get_object_or_404

from pop.core.auth import permissions as perms
from pop.core.utils import find_uuid_across_models
from pop.core.auth.token import XSessionTokenAuth
from pop.core.schemas import ModifiedResource as ModifiedResourceSchema
import pop.oncology.schemas as oncology_schemas
from pop.oncology.models import PatientCase
from pop.interoperability.schemas import PatientCaseBundle, ExportMetadata
from pop.interoperability.parsers import BundleParser


class ConflictingClinicalIdentifierException(APIException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    default_detail = "Unprocessable. Clinical identifier conflicts with existing case"


class ConflictingCaseException(APIException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    default_detail = "Unprocessable. Unresolved import case conflict."


class ConflictResolution(str, Enum):
    OVERWRITE = "overwrite"
    REASSIGN = "reassign"


@api_controller(
    "interoperability",
    auth=[XSessionTokenAuth()],
    tags=["Interoperability"],
)
class InteroperabilityController(ControllerBase):

    @route.get(
        path="resources/{resourceId}",
        response={
            200: Any,
            404: None,
        },
        permissions=[perms.CanManageCases, perms.CanExportData],
        operation_id="exportResource",
    )
    def export_resource(self, resourceId: str):
        instance = find_uuid_across_models(resourceId)
        if not instance:
            return 404, None
        schema = next(
            (
                schema
                for schema in oncology_schemas.ONCOLOGY_SCHEMAS
                if getattr(schema, "__orm_model__", None) == instance._meta.model
            )
        )
        export_data = schema.model_validate(instance).model_dump(mode="json")
        metadata = ExportMetadata(
            exportedAt=datetime.now(),
            exportedBy=self.context.request.user.username,
            exportVersion=settings.VERSION,
            checksum=hashlib.md5(
                json.dumps(export_data, sort_keys=True).encode("utf-8")
            ).hexdigest(),
        ).model_dump(mode="json")
        pghistory.create_event(instance, label="export")
        return {**metadata, **export_data}

    @route.get(
        path="resources/{resourceId}/description",
        response={
            200: str,
            404: None,
        },
        permissions=[perms.CanViewCases],
        operation_id="resolveResourceId",
    )
    def resolve_resource_id(self, resourceId: str):
        instance = find_uuid_across_models(resourceId)
        if not instance:
            return 404, None
        return instance.description

    @route.get(
        path="/bundles/{caseId}",
        response={
            200: PatientCaseBundle,
        },
        permissions=[perms.CanExportData],
        operation_id="exportPatientCaseBundle",
    )
    def export_case_bundle(self, caseId: str):
        exported_case = get_object_or_404(PatientCase, id=caseId)
        pghistory.create_event(exported_case, label="export")
        return exported_case

    @route.post(
        path="/bundles",
        response={201: ModifiedResourceSchema, 422: None},
        permissions=[perms.CanManageCases],
        operation_id="importPatientCaseBundle",
    )
    def import_case_bundle(
        self, bundle: PatientCaseBundle, conflict: ConflictResolution = None
    ):
        
        conflicting_case = PatientCase.objects.filter(
            pseudoidentifier=bundle.pseudoidentifier
        ).first()
        with transaction.atomic():
            if conflicting_case:
                if not conflict:
                    raise ConflictingCaseException()
                if conflict == ConflictResolution.OVERWRITE:
                    caseId = conflicting_case.id
                    conflicting_case.delete()
                    conflicting_case = PatientCase(pk=caseId)
                elif conflict == ConflictResolution.REASSIGN:
                    bundle.pseudoidentifier = ""
                    conflicting_case = None
            if not conflicting_case:
                if PatientCase.objects.filter(
                    clinical_identifier=bundle.clinicalIdentifier,
                    clinical_center=bundle.clinicalCenter,
                ).exists():
                    raise ConflictingClinicalIdentifierException()
            imported_case = BundleParser(bundle).import_bundle(case=conflicting_case)
            pghistory.create_event(imported_case, label="import")
        return 201, imported_case
