import pghistory 

from ninja import Query
from ninja_jwt.authentication import JWTAuth
from ninja_extra.pagination import paginate
from ninja_extra import api_controller, ControllerBase, route

from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404

from typing import List, Union, TypeAlias 
from typing_extensions import TypeAliasType

from pop.core import permissions as perms
from pop.core.utils import revert_multitable_model
from pop.core.security import XSessionTokenAuth
from pop.core.schemas import ModifiedResourceSchema, Paginated, HistoryEvent
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
    auth=[XSessionTokenAuth()], 
    tags=['Genomic Signatures'],  
)
class GenomicSignatureController(ControllerBase):

    @route.get(
        path='', 
        response={
            200: Paginated[AnyResponseSchemas],
        },
        exclude_none=True,
        permissions=[perms.CanViewCases],
        operation_id='getGenomicSignatures',
    )
    @paginate()
    def get_all_genomic_signatures_matching_the_query(self, query: Query[GenomicSignatureFilters]): # type: ignore
        queryset = GenomicSignature.objects.all().order_by('-date')
        return [cast_to_model_schema(genomic_signature.get_discriminated_genomic_signature(), RESPONSE_SCHEMAS) for genomic_signature in query.filter(queryset)]


    @route.post(
        path='', 
        response={
            201: ModifiedResourceSchema,
            401: None, 403: None,
        },
        permissions=[perms.CanManageCases],
        operation_id='createGenomicSignature',
    )
    def create_genomic_signature(self, payload: AnyPayloadSchemas): # type: ignore
        return 201, payload.model_dump_django()
        
    @route.get(
        path='/{genomicSignatureId}', 
        response={
            200: AnyResponseSchemas, 
            404: None
        },
        exclude_none=True,
        permissions=[perms.CanViewCases],
        operation_id='getGenomicSignatureById',
        )
    def get_genomic_signature_by_id(self, genomicSignatureId: str): 
        instance = get_object_or_404(GenomicSignature, id=genomicSignatureId)
        return cast_to_model_schema(instance.get_discriminated_genomic_signature(), RESPONSE_SCHEMAS)


    @route.put(
        path='/{genomicSignatureId}', 
       response={
            200: ModifiedResourceSchema,
            404: None, 401: None, 403: None,
        },
        permissions=[perms.CanManageCases],
        operation_id='updateGenomicSignatureById',
    )
    def update_genomic_signature(self, genomicSignatureId: str, payload: AnyPayloadSchemas): # type: ignore
        instance = get_object_or_404(GenomicSignature, id=genomicSignatureId).get_discriminated_genomic_signature()
        print('PAYLOAD', payload.get_orm_model())
        return payload.model_dump_django(instance=instance)
        

    @route.delete(
        path='/{genomicSignatureId}', 
        response={
            204: None, 
            404: None, 401: None, 403: None,
        },
        permissions=[perms.CanManageCases],
        operation_id='deleteGenomicSignatureById',
    )
    def delete_genomic_signature(self, genomicSignatureId: str):
        instance = get_object_or_404(GenomicSignature, id=genomicSignatureId)
        instance.delete()
        return 204, None
    
    @route.get(
        path='/{genomicSignatureId}/history/events', 
        response={
            200: Paginated[HistoryEvent],
            404: None, 401: None, 403: None,
        },
        permissions=[perms.CanViewCases],
        operation_id='getAllGenomicSignatureHistoryEvents',
    )
    @paginate()
    def get_all_genomic_signature_history_events(self, genomicSignatureId: str):
        instance = get_object_or_404(GenomicSignature, id=genomicSignatureId)
        return pghistory.models.Events.objects.tracks(instance).all()

    @route.get(
        path='/{genomicSignatureId}/history/events/{eventId}', 
        response={
            200: HistoryEvent,
            404: None, 401: None, 403: None,
        },
        permissions=[perms.CanViewCases],
        operation_id='getGenomicSignatureHistoryEventById',
    )
    def get_genomic_signature_history_event_by_id(self, genomicSignatureId: str, eventId: str):
        instance = get_object_or_404(GenomicSignature, id=genomicSignatureId)
        event = instance.parent_events.filter(pgh_id=eventId).first()
        if not event and hasattr(instance, 'events'):
            event = instance.events.filter(pgh_id=eventId).first()
        if not event:
            return 404, None
        return get_object_or_404(pghistory.models.Events.objects.tracks(instance), pgh_id=eventId)

    @route.put(
        path='/{genomicSignatureId}/history/events/{eventId}/reversion', 
        response={
            201: ModifiedResourceSchema,
            404: None, 401: None, 403: None,
        },
        permissions=[perms.CanManageCases],
        operation_id='revertGenomicSignatureToHistoryEvent',
    )
    def revert_genomic_signature_to_history_event(self, genomicSignatureId: str, eventId: str):
        instance = get_object_or_404(GenomicSignature, id=genomicSignatureId)
        instance = instance.get_discriminated_genomic_signature()
        try:
            return 201, revert_multitable_model(instance, eventId)
        except ObjectDoesNotExist:
            return 404, None


