import hashlib
import json
from datetime import datetime
from enum import Enum
from typing import Any

import pghistory
from django.conf import settings
from django.db import transaction
from django.shortcuts import get_object_or_404
from ninja_extra import ControllerBase, api_controller, route, status
from ninja_extra.exceptions import APIException

import onconova.oncology.schemas as oncology_schemas
from onconova.core.auth import permissions as perms
from onconova.core.auth.token import XSessionTokenAuth
from onconova.core.schemas import ModifiedResource as ModifiedResourceSchema
from onconova.core.utils import COMMON_HTTP_ERRORS, find_uuid_across_models
from onconova.interoperability.parsers import BundleParser
from onconova.interoperability.schemas import ExportMetadata, PatientCaseBundle
from onconova.oncology.models import PatientCase


class ConflictingClinicalIdentifierException(APIException):
    """
    Exception raised when a clinical identifier conflicts with an existing case.
    """
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    default_detail = "Unprocessable. Clinical identifier conflicts with existing case"


class ConflictingCaseException(APIException):
    """
    Exception raised when an unresolved import case conflict occurs.
    """
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    default_detail = "Unprocessable. Unresolved import case conflict."


class ConflictResolution(str, Enum):
    """
    Enum representing strategies for resolving conflicts during interoperability operations.

    Attributes:
        OVERWRITE: Overwrite existing data with new data.
        REASSIGN: Reassign ownership or association to resolve the conflict.
    """
    OVERWRITE = "overwrite"
    REASSIGN = "reassign"


@api_controller(
    "interoperability",
    auth=[XSessionTokenAuth()],
    tags=["Interoperability"],
)
class InteroperabilityController(ControllerBase):
    """
    API controller for interoperability operations related to resource and patient case management.
    """

    @route.get(
        path="resources/{resourceId}",
        response={
            200: Any,
            404: None,
            **COMMON_HTTP_ERRORS,
        },
        permissions=[perms.CanManageCases, perms.CanExportData],
        operation_id="exportResource",
    )
    def export_resource(self, resourceId: str):
        """
        Exports a resource identified by its UUID, serializing its data and associated metadata.

        Args:
            resourceId (str): The UUID of the resource to export.

        Returns:
            (dict): A dictionary containing both the resource's exported data and metadata if found.

        Notes:

            - Creates an export event for the resource using `pghistory.create_event`.
            - Computes a checksum of the exported data for integrity verification.

        """
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
            **COMMON_HTTP_ERRORS,
        },
        permissions=[perms.CanViewCases],
        operation_id="resolveResourceId",
    )
    def resolve_resource_id(self, resourceId: str):
        """
        Resolves a resource ID by searching across models for a matching UUID.

        Args:
            resourceId (str): The UUID of the resource to resolve.

        Returns:
            (str): If found, returns the description of the resource instance.
        """
        instance = find_uuid_across_models(resourceId)
        if not instance:
            return 404, None
        return instance.description

    @route.get(
        path="/bundles/{caseId}",
        response={
            200: PatientCaseBundle,
            **COMMON_HTTP_ERRORS,
        },
        permissions=[perms.CanExportData],
        operation_id="exportPatientCaseBundle",
    )
    def export_case_bundle(self, caseId: str):
        """
        Exports a patient case bundle by retrieving the PatientCase object with the given case ID,
        creates an export event for the case, and returns the exported case object.

        Args:
            caseId (str): The unique identifier of the patient case to export.

        Returns:
            (PatientCase): The exported patient case object.
        """
        exported_case = get_object_or_404(PatientCase, id=caseId)
        pghistory.create_event(exported_case, label="export")
        return exported_case

    @route.post(
        path="/bundles",
        response={
            201: ModifiedResourceSchema,
            422: None,
            **COMMON_HTTP_ERRORS,
        },
        permissions=[perms.CanManageCases],
        operation_id="importPatientCaseBundle",
    )
    def import_case_bundle(
        self, bundle: PatientCaseBundle, conflict: ConflictResolution = None
    ):
        """
        Imports a patient case bundle into the database, handling conflicts based on the specified resolution strategy.

        Args:
            bundle (PatientCaseBundle): The patient case bundle to import.
            conflict (ConflictResolution | None): Strategy for resolving conflicts with existing cases.

        Raises:
            ConflictingCaseException: If a case with the same pseudoidentifier exists and no conflict resolution is provided.
            ConflictingClinicalIdentifierException: If a case with the same clinical identifier and center exists.

        Returns:
            (tuple[int, PatientCase]): Returns the HTTP status code and the imported `PatientCase` instance.
        """

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
