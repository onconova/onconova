from pop.oncology import models as orm
from pop.core.schemas.factory import ModelGetSchema, ModelCreateSchema, SchemaConfig

class GenomicVariantSchema(ModelGetSchema):
    config = SchemaConfig(model=orm.GenomicVariant, exclude=('is_vus', 'is_pathogenic'))

class GenomicVariantCreateSchema(ModelCreateSchema):
    config = SchemaConfig(model=orm.GenomicVariant, exclude=('is_vus', 'is_pathogenic'))
