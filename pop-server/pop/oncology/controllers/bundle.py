
from enum import Enum 
from ninja_jwt.authentication import JWTAuth
from ninja_extra.pagination import paginate
from ninja_extra import api_controller, ControllerBase, route, status
from ninja_extra.exceptions import APIException

from django.shortcuts import get_object_or_404

from pop.core import permissions as perms
from pop.core.schemas import ModifiedResourceSchema, Paginated
from pop.oncology.models import PatientCase
from pop.oncology.schemas.bundle import PatientCaseBundle
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
    'patient-cases/bundles', 
    auth=[JWTAuth()], 
    tags=['Patient Cases'],  
)
class BundleController(ControllerBase):
    @route.get(
        path='/export/{caseId}', 
        response={
            200: PatientCaseBundle,
        },
        permissions=[perms.CanExportData],
        operation_id='exportPatientCaseBundle',
    )
    def export_case_bundle(self, caseId: str):
        case = get_object_or_404(PatientCase, id=caseId)
        return case 

    @route.post(
        path='/import', 
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
        return 201, BundleParser(payload).import_bundle()
