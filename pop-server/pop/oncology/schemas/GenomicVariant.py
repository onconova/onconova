from pop.oncology.models import GenomicVariant
from pop.core.schemas import CREATE_IGNORED_FIELDS, create_schema, GetMixin, CreateMixin, ConfigDict
from ninja import Schema

GenomicVariantBase: Schema = create_schema(
    GenomicVariant, 
    exclude=(*CREATE_IGNORED_FIELDS,),
)

class GenomicVariantSchema(GenomicVariantBase, GetMixin):
    model_config = ConfigDict(title='GenomicVariant')

class GenomicVariantCreateSchema(GenomicVariantBase, CreateMixin):
    model_config = ConfigDict(title='GenomicVariantCreate',)
