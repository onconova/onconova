from ninja import Query
from ninja.schema import Schema, Field
from ninja_jwt.authentication import JWTAuth
from ninja_extra.pagination import paginate
from ninja_extra import api_controller, ControllerBase, route

from django.shortcuts import get_object_or_404

from typing import List, Union, TypeAlias 
from typing_extensions import TypeAliasType

from pop.core.schemas import ResourceIdSchema, Paginated
from pop.oncology.models.TumorBoard import TumorBoard, TumorBoardSpecialties, MolecularTumorBoard, MolecularTherapeuticRecommendation
from pop.oncology.schemas import (
    UnspecifiedTumorBoardSchema, UnspecifiedTumorBoardCreateSchema,
    MolecularTumorBoardSchema, MolecularTumorBoardCreateSchema,
    MolecularTherapeuticRecommendationSchema, MolecularTherapeuticRecommendationCreateSchema
)

RESPONSE_SCHEMAS = (
    UnspecifiedTumorBoardSchema,
    MolecularTumorBoardSchema, 
)

PAYLOAD_SCHEMAS = (
    UnspecifiedTumorBoardCreateSchema, 
    MolecularTumorBoardCreateSchema,
)

AnyResponseSchemas = TypeAliasType('AnyTumorBoard', Union[RESPONSE_SCHEMAS]) # type: ignore# type: ignore
AnyPayloadSchemas = Union[PAYLOAD_SCHEMAS]

class QueryParameters(Schema):
    case__id: str = Field(None, alias='caseId')
    stagingDomain: List[TumorBoardSpecialties] = Field(None, alias='stagingDomain')

def cast_to_model_schema(model_instance, schemas, payload=None):
    return next((
        schema.model_validate(payload or model_instance)
            for schema in schemas 
                if (payload or model_instance).tumor_board_specialty == schema.model_fields['category'].default
    ))
    
@api_controller(
    'tumor-boards/', 
    auth=[JWTAuth()], 
    tags=['Tumor Boards'],  
)
class TumorBoardController(ControllerBase):

    @route.get(
        path='/', 
        response={
            200: Paginated[AnyResponseSchemas],
        },
        exclude_none=True,
        operation_id='getTumorBoards',
    )
    @paginate()
    def get_all_tumor_boards_matching_the_query(self, query: Query[QueryParameters]):
        queryset = TumorBoard.objects.all().order_by('-date')
        for (lookup, value) in query:
            if value is not None:
                queryset = queryset.filter(**{lookup: value})
        return [cast_to_model_schema(tumorboard.specialized_tumor_board, RESPONSE_SCHEMAS) for tumorboard in queryset]


    @route.post(
        path='/', 
        response={
            201: ResourceIdSchema,
        },
        operation_id='createTumorBoard',
    )
    def create_tumor_board(self, payload: AnyPayloadSchemas): # type: ignore
        instance = payload.model_dump_django(user=self.context.request.user)
        return 201, ResourceIdSchema(id=instance.id)

    @route.get(
        path='/{tumorBoardId}', 
        response={
            200: AnyResponseSchemas, 
            404: None
        },
        exclude_none=True,
        operation_id='getTumorBoardById',
        )
    def get_tumor_board_by_id(self, tumorBoardId: str): 
        instance = get_object_or_404(TumorBoard, id=tumorBoardId)
        return 200, cast_to_model_schema(instance.specialized_tumor_board, RESPONSE_SCHEMAS)


    @route.put(
        path='/{tumorBoardId}', 
        response={
            204: None, 
            404: None
        },
        operation_id='updateTumorBoardById',
    )
    def update_tumor_board(self, tumorBoardId: str, payload: AnyPayloadSchemas): # type: ignore
        instance = get_object_or_404(TumorBoard, id=tumorBoardId).specialized_tumor_board
        instance = payload.model_dump_django(instance=instance, user=self.context.request.user)
        return 204, None

    @route.delete(
        path='/{tumorBoardId}', 
        response={
            204: None, 
            404: None,
        },
        operation_id='deleteTumorBoardById',
    )
    def delete_tumor_board(self, tumorBoardId: str):
        instance = get_object_or_404(TumorBoard, id=tumorBoardId)
        instance.delete()
        return 204, None
    


@api_controller(
    'molecular-tumor-boards/', 
    auth=[JWTAuth()], 
    tags=['Tumor Boards'],  
)
class MolecularTherapeuticRecommendationController(ControllerBase):

    @route.get(
        path='/{tumorBoardId}/therapeutic-recommendations/', 
        response={
            200: List[MolecularTherapeuticRecommendationSchema],
            404: None,
        },
        operation_id='getMolecularTherapeuticRecommendations',
    )
    def get_molecular_tumor_board_therapeutic_recommendations_matching_the_query(self, tumorBoardId: str): # type: ignore
        queryset = get_object_or_404(MolecularTumorBoard, id=tumorBoardId).therapeutic_recommendations.all()
        return 200, [MolecularTherapeuticRecommendationSchema.model_validate(entry) for entry in queryset]


    @route.get(
        path='/{tumorBoardId}/therapeutic-recommendations/{recommendationId}', 
        response={
            200: MolecularTherapeuticRecommendationSchema, 
            404: None
        },
        exclude_none=True,
        operation_id='getMOlecularTherapeuticRecommendationById',
        )
    def get_molecular_tumor_board_therapeutic_recommendation_by_id(self, tumorBoardId: str, recommendationId: str): 
        instance = get_object_or_404(MolecularTherapeuticRecommendation, id=recommendationId, molecular_tumor_board__id=tumorBoardId)
        return 200, MolecularTherapeuticRecommendationSchema.model_validate(instance)

    @route.post(
        path='/{tumorBoardId}/therapeutic-recommendations/', 
        response={
            201: ResourceIdSchema,
        },
        operation_id='createMolecularTherapeuticRecommendation',
    )
    def create_molecular_tumor_board_therapeutic_recommendation(self, tumorBoardId: str, payload: MolecularTherapeuticRecommendationCreateSchema): # type: ignore
        instance = MolecularTherapeuticRecommendation(molecular_tumor_board=get_object_or_404(MolecularTumorBoard, id=tumorBoardId))
        instance = MolecularTherapeuticRecommendationCreateSchema\
                    .model_validate(payload)\
                    .model_dump_django(instance=instance, user=self.context.request.user, create=True)
        return 201, ResourceIdSchema(id=instance.id)

    @route.put(
        path='/{tumorBoardId}/therapeutic-recommendations/{recommendationId}', 
        response={
            204: ResourceIdSchema,
            404: None,
        },
        operation_id='updateMolecularTherapeuticRecommendation',
    )
    def update_molecular_tumor_board_therapeutic_recommendation(self, tumorBoardId: str, recommendationId: str, payload: MolecularTherapeuticRecommendationCreateSchema): # type: ignore
        instance = get_object_or_404(MolecularTherapeuticRecommendation, id=recommendationId, molecular_tumor_board__id=tumorBoardId)
        instance = MolecularTherapeuticRecommendationCreateSchema\
                    .model_validate(payload)\
                    .model_dump_django(instance=instance, user=self.context.request.user)
        return 204, ResourceIdSchema(id=instance.id)

    @route.delete(
        path='/{tumorBoardId}/therapeutic-recommendations/{recommendationId}', 
        response={
            204: None, 
            404: None,
        },
        operation_id='deleteMolecularTherapeuticRecommendation',
    )
    def delete_molecular_tumor_board_therapeutic_recommendation(self, tumorBoardId: str, recommendationId: str):
        instance = get_object_or_404(MolecularTherapeuticRecommendation, id=recommendationId, molecular_tumor_board__id=tumorBoardId)
        instance.delete()
        return 204, None
