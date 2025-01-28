from ninja import Query
from ninja.schema import Schema, Field
from ninja_jwt.authentication import JWTAuth
from ninja_extra.pagination import paginate
from ninja_extra import api_controller, ControllerBase, route

from pop.core.schemas import ResourceIdSchema, Paginated
from pop.oncology.models import GenomicVariant

from django.shortcuts import get_object_or_404

from pop.oncology.schemas import GenomicVariantSchema, GenomicVariantCreateSchema, GenomicVariantFilters


@api_controller(
    'genomic-variants/', 
    auth=[JWTAuth()], 
    tags=['Genomic Variants'],  
)
class GenomicVariantController(ControllerBase):

    @route.get(
        path='/', 
        response={
            200: Paginated[GenomicVariantSchema],
        },
        operation_id='getGenomicVariants',
    )
    @paginate()
    def get_all_genomic_variants_matching_the_query(self, query: Query[GenomicVariantFilters]): # type: ignore
        queryset = GenomicVariant.objects.all().order_by('-date')
        return [GenomicVariantSchema.model_validate(instance) for instance in query.apply_filters(queryset)]

    @route.post(
        path='/', 
        response={
            201: ResourceIdSchema
        },
        operation_id='createGenomicVariant',
    )
    def create_genomic_variant(self, payload: GenomicVariantCreateSchema): # type: ignore
        instance = GenomicVariantCreateSchema\
                    .model_validate(payload)\
                    .model_dump_django(user=self.context.request.user)
        return 201, ResourceIdSchema(id=instance.id)

    @route.get(
        path='/{genomicVariantId}', 
        response={
            200: GenomicVariantSchema,
            404: None,
        },
        operation_id='getGenomicVariantById',
    )
    def get_genomic_variant_by_id(self, genomicVariantId: str):
        instance = get_object_or_404(GenomicVariant, id=genomicVariantId)
        return 200, GenomicVariantSchema.model_validate(instance)

    @route.put(
        path='/{genomicVariantId}', 
        response={
            204: None, 
            404: None
        },
        operation_id='updateGenomicVariant',
    )
    def update_genomic_variant(self, genomicVariantId: str, payload: GenomicVariantCreateSchema): # type: ignore
        instance = get_object_or_404(GenomicVariant, id=genomicVariantId)
        instance = GenomicVariantCreateSchema\
                    .model_validate(payload.model_dump(exclude_unset=True))\
                    .model_dump_django(instance=instance, user=self.context.request.user)
        return 204, None

    @route.delete(
        path='/{genomicVariantId}', 
        response={
            204: None, 
            404: None,
        },
        operation_id='deleteGenomicVariant',
    )
    def delete_genomic_variant(self, genomicVariantId: str):
        instance = get_object_or_404(GenomicVariant, id=genomicVariantId)
        instance.delete()
        return 204, None
    