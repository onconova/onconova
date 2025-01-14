from pop.oncology.models import Vitals
from pop.core.schemas import CREATE_IGNORED_FIELDS, create_schema, GetMixin, CreateMixin, ConfigDict
from ninja import Schema

VitalsBase: Schema = create_schema(
    Vitals, 
    exclude=(*CREATE_IGNORED_FIELDS,),
)

class VitalsSchema(VitalsBase, GetMixin):
    model_config = ConfigDict(title='Vitals')
    
class VitalsCreateSchema(VitalsBase, CreateMixin):
    model_config = ConfigDict(title='VitalsCreate')