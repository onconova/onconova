from ninja import Query
from ninja.schema import Schema, Field
from ninja_jwt.authentication import JWTAuth
from ninja_extra.pagination import paginate
from ninja_extra import api_controller, ControllerBase, route

from django.shortcuts import get_object_or_404

from typing import List, Union, TypeAlias 
from typing_extensions import TypeAliasType

from pop.core.schemas import ModifiedResourceSchema, Paginated
from pop.oncology.models import GenomicSignature, GenomicSignatureTypes
from pop.oncology.schemas import (
    GenomicSignatureFilters,
    TumorMutationalBurdenSchema, TumorMutationalBurdenCreateSchema,
    MicrosatelliteInstabilitySchema, MicrosatelliteInstabilityCreateSchema,
    LossOfHeterozygositySchema, LossOfHeterozygosityCreateSchema,
    HomologousRecombinationDeficiencySchema, HomologousRecombinationDeficiencyCreateSchema,
    TumorNeoantigenBurdenSchema, TumorNeoantigenBurdenCreateSchema,
    AneuploidScoreSchema, AneuploidScoreCreateSchema,
)

RESPONSE_SCHEMAS = (
    MicrosatelliteInstabilitySchema,
    TumorMutationalBurdenSchema, 
    LossOfHeterozygositySchema, 
    HomologousRecombinationDeficiencySchema, 
    TumorNeoantigenBurdenSchema, 
    AneuploidScoreSchema, 
)

PAYLOAD_SCHEMAS = (
    TumorMutationalBurdenCreateSchema, 
    MicrosatelliteInstabilityCreateSchema,
    LossOfHeterozygosityCreateSchema,
    HomologousRecombinationDeficiencyCreateSchema,
    TumorNeoantigenBurdenCreateSchema,
    AneuploidScoreCreateSchema,
)

AnyResponseSchemas = TypeAliasType('AnyGenomicSignature', Union[RESPONSE_SCHEMAS]) # type: ignore# type: ignore
AnyPayloadSchemas = Union[PAYLOAD_SCHEMAS]

def cast_to_model_schema(model_instance, schemas, payload=None):
    return next((
        schema.model_validate(payload or model_instance)
            for schema in schemas 
                if (payload or model_instance).genomic_signature_type == schema.model_fields['category'].default
    ))
    
@api_controller(
    'genomic-signatures', 
    auth=[JWTAuth()], 
    tags=['Genomic Signatures'],  
)
class GenomicSignatureController(ControllerBase):

    @route.get(
        path='', 
        response={
            200: Paginated[AnyResponseSchemas],
        },
        exclude_none=True,
        operation_id='getGenomicSignatures',
    )
    @paginate()
    def get_all_genomic_signatures_matching_the_query(self, query: Query[GenomicSignatureFilters]): # type: ignore
        queryset = GenomicSignature.objects.all().order_by('-date')
        return [cast_to_model_schema(staging.get_discriminated_genomic_signature(), RESPONSE_SCHEMAS) for staging in query.filter(queryset)]


    @route.post(
        path='', 
        response={
            201: ModifiedResourceSchema,
        },
        operation_id='createGenomicSignature',
    )
    def create_genomic_signature(self, payload: AnyPayloadSchemas): # type: ignore
        return payload.model_dump_django(user=self.context.request.user)
        
    @route.get(
        path='/{genomicSignatureId}', 
        response={
            200: AnyResponseSchemas, 
            404: None
        },
        exclude_none=True,
        operation_id='getGenomicSignatureById',
        )
    def get_genomic_signature_by_id(self, genomicSignatureId: str): 
        instance = get_object_or_404(GenomicSignature, id=genomicSignatureId)
        return cast_to_model_schema(instance.get_discriminated_genomic_signature(), RESPONSE_SCHEMAS)


    @route.put(
        path='/{genomicSignatureId}', 
       response={
            200: ModifiedResourceSchema,
            404: None,
        },
        operation_id='updateGenomicSignatureById',
    )
    def update_genomic_signature(self, genomicSignatureId: str, payload: AnyPayloadSchemas): # type: ignore
        instance = get_object_or_404(GenomicSignature, id=genomicSignatureId).get_discriminated_genomic_signature()
        return payload.model_dump_django(instance=instance, user=self.context.request.user)
        
        
    @route.delete(
        path='/{genomicSignatureId}', 
        response={
            204: None, 
            404: None,
        },
        operation_id='deleteGenomicSignatureById',
    )
    def delete_genomic_signature(self, genomicSignatureId: str):
        instance = get_object_or_404(GenomicSignature, id=genomicSignatureId)
        instance.delete()
        return 204, None
    

