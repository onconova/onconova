import pghistory
from ninja import Query
from ninja.schema import Schema, Field
from ninja_jwt.authentication import JWTAuth
from ninja_extra.pagination import paginate
from ninja_extra import api_controller, ControllerBase, route

from pop.core import permissions as perms
from pop.core.security import XSessionTokenAuth
from pop.core.anonymization import anonymize
from pop.core.schemas import ModifiedResourceSchema, Paginated, HistoryEvent
from pop.oncology.models import GenomicVariant

from django.shortcuts import get_object_or_404

from pop.oncology.schemas import GenomicVariantSchema, GenomicVariantCreateSchema, GenomicVariantFilters


@api_controller(
    'genomic-variants', 
    auth=[XSessionTokenAuth()], 
    tags=['Genomic Variants'],  
)
class GenomicVariantController(ControllerBase):

    @route.get(
        path='', 
        response={
            200: Paginated[GenomicVariantSchema],
        },
        permissions=[perms.CanViewCases],
        operation_id='getGenomicVariants',
    )
    @paginate()
    @anonymize()
    def get_all_genomic_variants_matching_the_query(self, query: Query[GenomicVariantFilters], anonymized: bool = True): # type: ignore
        queryset = GenomicVariant.objects.all().order_by('-date')
        return query.filter(queryset)


    @route.post(
        path='', 
        response={
            201: ModifiedResourceSchema,
            401: None, 403: None,
        },
        permissions=[perms.CanManageCases],
        operation_id='createGenomicVariant',
    )
    def create_genomic_variant(self, payload: GenomicVariantCreateSchema): # type: ignore
        return 201, payload.model_dump_django()
        

    @route.get(
        path='/{genomicVariantId}', 
        response={
            200: GenomicVariantSchema,
            404: None, 401: None, 403: None,
        },
        permissions=[perms.CanViewCases],
        operation_id='getGenomicVariantById',
    )
    @anonymize()
    def get_genomic_variant_by_id(self, genomicVariantId: str, anonymized: bool = True):
        return get_object_or_404(GenomicVariant, id=genomicVariantId)
        

    @route.put(
        path='/{genomicVariantId}', 
       response={
            200: ModifiedResourceSchema,
            404: None, 401: None, 403: None,
        },
        permissions=[perms.CanManageCases],
        operation_id='updateGenomicVariant',
    )
    def update_genomic_variant(self, genomicVariantId: str, payload: GenomicVariantCreateSchema): # type: ignore
        instance = get_object_or_404(GenomicVariant, id=genomicVariantId)
        return payload.model_dump_django(instance=instance)
        
        
    @route.delete(
        path='/{genomicVariantId}', 
        response={
            204: None, 
            404: None, 401: None, 403: None,
        },
        permissions=[perms.CanManageCases],
        operation_id='deleteGenomicVariant',
    )
    def delete_genomic_variant(self, genomicVariantId: str):
        get_object_or_404(GenomicVariant, id=genomicVariantId).delete()
        return 204, None
    
    
    @route.get(
        path='/{genomicVariantId}/history/events', 
        response={
            200: Paginated[HistoryEvent.bind_schema(GenomicVariantCreateSchema)],
            404: None, 401: None, 403: None,
        },
        permissions=[perms.CanViewCases],
        operation_id='getAllGenomicVariantHistoryEvents',
    )
    @paginate()
    def get_all_genomic_variant_history_events(self, genomicVariantId: str):
        instance = get_object_or_404(GenomicVariant, id=genomicVariantId)
        return pghistory.models.Events.objects.tracks(instance).all()


    @route.get(
        path='/{genomicVariantId}/history/events/{eventId}', 
        response={
            200: HistoryEvent.bind_schema(GenomicVariantCreateSchema),
            404: None, 401: None, 403: None,
        },
        permissions=[perms.CanViewCases],
        operation_id='getGenomicVariantHistoryEventById',
    )
    def get_genomic_variant_history_event_by_id(self, genomicVariantId: str, eventId: str):
        instance = get_object_or_404(GenomicVariant, id=genomicVariantId)
        return get_object_or_404(pghistory.models.Events.objects.tracks(instance), pgh_id=eventId)


    @route.put(
        path='/{genomicVariantId}/history/events/{eventId}/reversion', 
        response={
            201: ModifiedResourceSchema,
            404: None, 401: None, 403: None,
        },
        permissions=[perms.CanManageCases],
        operation_id='revertGenomicVariantToHistoryEvent',
    )
    def revert_genomic_variant_to_history_event(self, genomicVariantId: str, eventId: str):
        instance = get_object_or_404(GenomicVariant, id=genomicVariantId)
        return 201, get_object_or_404(instance.events, pgh_id=eventId).revert()