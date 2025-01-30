from enum import Enum

from ninja import Query
from ninja.schema import Schema, Field
from ninja_jwt.authentication import JWTAuth
from ninja_extra.pagination import paginate
from ninja_extra import api_controller, ControllerBase, route

from django.shortcuts import get_object_or_404

from pop.core.schemas import ModifiedResourceSchema, Paginated, ModelFilterSchema
from pop.oncology.models import PatientCase, PatientCaseDataCompletion
from pop.oncology.schemas import (
    PatientCaseSchema, PatientCaseCreateSchema, PatientCaseFilters,
    PatientCaseDataCompletionStatusSchema, 
    PatientCaseBundleSchema, PatientCaseBundleCreateSchema
)

@api_controller(
    'patient-cases', 
    auth=[JWTAuth()], 
    tags=['Patient Cases'],  
)
class PatientCaseController(ControllerBase):

    @route.get(
        path='', 
        response={
            200: Paginated[PatientCaseSchema]
        },
        operation_id='getPatientCases',
    )
    @paginate()
    def get_all_patient_cases_matching_the_query(self, query: Query[PatientCaseFilters]):  # type: ignore
        queryset = PatientCase.objects.all().order_by('-created_at')
        return query.filter(queryset)

    @route.post(
        path='', 
        response={
            201: ModifiedResourceSchema
        },
        operation_id='createPatientCase',
    )
    def create_patient_case(self, payload: PatientCaseCreateSchema):
        return PatientCaseCreateSchema.model_validate(payload).model_dump_django(user=self.context.request.user)

    @route.get(
        path='/{caseId}', 
        response={
            200: PatientCaseSchema, 
            404: None
        },
        operation_id='getPatientCaseById',
        )
    def get_patient_case_by_id(self, caseId: str): 
        return get_object_or_404(PatientCase, id=caseId)

    @route.get(
        path='/pseudo/{pseudoidentifier}', 
        response={
            200: PatientCaseSchema, 
            404: None
        },
        operation_id='getPatientCaseByPseudoidentifier',
        )
    def get_patient_case_by_pseudoidentifier(self, pseudoidentifier: str): 
        return get_object_or_404(PatientCase, pseudoidentifier=pseudoidentifier.strip())
        
    @route.put(
        path='/{caseId}', 
       response={
            200: ModifiedResourceSchema,
            404: None,
        },
        operation_id='updatePatientCaseById',
    )
    def update_patient_case(self, caseId: str, payload: PatientCaseCreateSchema): # type: ignore
        instance = get_object_or_404(PatientCase, id=caseId)
        return PatientCaseCreateSchema\
                    .model_validate(payload)\
                    .model_dump_django(instance=instance, user=self.context.request.user)
       
    @route.delete(
        path='/{caseId}', 
        response={
            204: None, 
            404: None,
        },
        operation_id='deletePatientCaseById',
    )
    def delete_patient_case(self, caseId: str):
        instance = get_object_or_404(PatientCase, id=caseId)
        instance.delete()
        return 204, None
    

    @route.get(
        path='/{caseId}/data-completion/{category}', 
        response={
            200: PatientCaseDataCompletionStatusSchema,
        },
        operation_id='getPatientCaseDataCompletionStatus',
    )
    def get_patient_case_data_completion_status(self, caseId: str, category: PatientCaseDataCompletion.PatientCaseDataCategories):
        category_completion = PatientCaseDataCompletion.objects.filter(case__id=caseId, category=category).first()
        return PatientCaseDataCompletionStatusSchema(
                status=category_completion is not None,
                username=category_completion.created_by.username if category_completion else None,
                timestamp=category_completion.created_at if category_completion else None,
        )
        
    @route.post(
        path='/{caseId}/data-completion/{category}', 
        response={
            201: ModifiedResourceSchema,
        },
        operation_id='createPatientCaseDataCompletion',
    )
    def create_patient_case_data_completion(self, caseId: str, category: PatientCaseDataCompletion.PatientCaseDataCategories):
        return PatientCaseDataCompletion.objects.create(case=get_object_or_404(PatientCase,id=caseId), category=category, created_by=self.context.request.user)
        
    @route.delete(
        path='/{caseId}/data-completion/{category}', 
        response={
            204: None, 
            404: None,
        },
        operation_id='deletePatientCaseDataCompletion',
    )
    def delete_patient_case_data_completion(self, caseId: str, category: PatientCaseDataCompletion.PatientCaseDataCategories):
        instance = get_object_or_404(PatientCaseDataCompletion, case__id=caseId, category=category)
        instance.delete()
        return 204, None



    @route.get(
        path='/bundle/{caseId}', 
        response={
            200: PatientCaseBundleSchema,
        },
        operation_id='getPatientCaseBundleById',
    )
    def get_patient_case_bundle_by_id(self, caseId: str):
        from pop.oncology.schemas import NeoplasticEntitySchema
        case = get_object_or_404(PatientCase, id=caseId)
        response = PatientCaseBundleSchema.model_validate(case)
        response.neoplasticEntities = [NeoplasticEntitySchema.model_validate(entry) for entry in case.neoplastic_entities.all()],
        return 200, response 

    @route.post(
        path='/bundle', 
        response={
            201: ModifiedResourceSchema,
        },
        operation_id='createPatientCaseBundleById',
    )
    def create_patient_case_bundle(self, payload: PatientCaseBundleCreateSchema):
        return PatientCaseCreateSchema.model_validate(payload).model_dump_django(user=self.context.request.user)
 