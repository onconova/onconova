from pop.oncology.models import Lifestyle
from pop.core.schemas import CREATE_IGNORED_FIELDS, create_schema, GetMixin, CreateMixin, ConfigDict
from ninja import Schema

LifestyleBase: Schema = create_schema(
    Lifestyle, 
    exclude=(*CREATE_IGNORED_FIELDS,),
)

class LifestyleSchema(LifestyleBase, GetMixin):
    model_config = ConfigDict(title='Lifestyle')

class LifestyleCreateSchema(LifestyleBase, CreateMixin):
    model_config = ConfigDict(title='LifestyleCreate',)
