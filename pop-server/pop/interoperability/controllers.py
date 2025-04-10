import pghistory 
import hashlib 
import json 
from enum import Enum 
from typing import Any
from datetime import datetime
from ninja_jwt.authentication import JWTAuth
from ninja_extra.pagination import paginate
from ninja_extra import api_controller, ControllerBase, route, status
from ninja_extra.exceptions import APIException

from django.conf import settings
from django.shortcuts import get_object_or_404

from pop.core import permissions as perms
from pop.core.schemas import ModifiedResourceSchema
from pop.oncology.models import PatientCase
import pop.oncology.schemas as sc
from pop.interoperability.schemas import PatientCaseBundle, ExportMetadata
from pop.interoperability.parsers import BundleParser

class ConflictingClinicalIdentifierException(APIException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    default_detail = 'Unprocessable. Clinical identifier conflicts with existing case'

class ConflictingCaseException(APIException):
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    default_detail = 'Unprocessable. Unresolved import case conflict.'
    
class ConflictResolution(str, Enum):
    OVERWRITE = 'overwrite'
    REASSIGN = 'reassign'


@api_controller(
    'interoperability', 
    auth=[JWTAuth()], 
    tags=['Interoperability'],  
)
class InteroperabilityController(ControllerBase):
    @route.get(
        path='resources/{resource}/{resourceId}', 
        response={
            200: Any,
        },
        permissions=[perms.CanManageCases, perms.CanExportData],
        operation_id='exportResource',
    )
    def export_resource(self, resource: str, resourceId: str):
        resource_schema = getattr(sc, f'{resource.strip()}Schema')
        instance = get_object_or_404(resource_schema.__orm_model__, pk=resourceId)
        export_data = resource_schema.model_validate(instance).model_dump(mode='json')
        metadata = ExportMetadata(
            exported_at=datetime.now(),
            exported_by=self.context.request.user.username,
            export_version=settings.VERSION,
            checksum=hashlib.md5(json.dumps(export_data, sort_keys=True).encode('utf-8')).hexdigest()
        ).model_dump(mode='json')
        pghistory.create_event(instance, label="export")
        return {**metadata, **export_data}
    
    @route.get(
        path='/bundles/{caseId}', 
        response={
            200: PatientCaseBundle,
        },
        permissions=[perms.CanExportData],
        operation_id='exportPatientCaseBundle',
    )
    def export_case_bundle(self, caseId: str):
        exported_case = get_object_or_404(PatientCase, id=caseId)
        pghistory.create_event(exported_case, label="export")
        return exported_case 

    @route.post(
        path='/bundles', 
        response={
            201: ModifiedResourceSchema,
            422: None
        },
        permissions=[perms.CanManageCases, perms.CanExportData],
        operation_id='importPatientCaseBundle',
    )
    def import_case_bundle(self, payload: PatientCaseBundle, conflict: ConflictResolution = None):
        conflicting_case = PatientCase.objects.filter(pseudoidentifier=payload.pseudoidentifier).first()
        if conflicting_case:    
            if not conflict:
                raise ConflictingCaseException()
            if conflict==ConflictResolution.OVERWRITE:
                conflicting_case.delete()
            elif conflict==ConflictResolution.REASSIGN:
                payload.pseudoidentifier = ''      
        if PatientCase.objects.filter(clinical_identifier=payload.clinicalIdentifier, clinical_center=payload.clinicalCenter).exists():
            raise ConflictingClinicalIdentifierException()
        imported_case = BundleParser(payload).import_bundle()
        pghistory.create_event(imported_case, label="import")
        return 201, imported_case
