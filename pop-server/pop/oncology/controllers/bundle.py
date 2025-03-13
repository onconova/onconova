
from ninja import Query
from ninja.schema import Schema, Field
from ninja_jwt.authentication import JWTAuth
from ninja_extra.pagination import paginate
from ninja_extra import api_controller, ControllerBase, route

from django.shortcuts import get_object_or_404

from pop.core import permissions as perms
from pop.core.schemas import ModifiedResourceSchema, Paginated
from pop.oncology.models import PatientCase
from pop.oncology.schemas.bundle import PatientCaseBundle
from pop.interoperability.parsers import BundleParser

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
        },
        permissions=[perms.CanManageCases, perms.CanExportData],
        operation_id='importPatientCaseBundle',
    )
    def import_case_bundle(self, payload: PatientCaseBundle):
        return BundleParser(payload).import_bundle()
