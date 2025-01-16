from pop.oncology.models import Vitals
from pop.core.schemas import CREATE_IGNORED_FIELDS, create_schema, GetMixin, CreateMixin, ConfigDict, MeasureSchema
from ninja import Schema, Field

VitalsBase: Schema = create_schema(
    Vitals, 
    exclude=(*CREATE_IGNORED_FIELDS, 'body_mass_index'),
)

class VitalsSchema(VitalsBase, GetMixin):
    body_mass_index: MeasureSchema = Field(description='Bodymass index of the patient')
    model_config = ConfigDict(title='Vitals')
    
class VitalsCreateSchema(VitalsBase, CreateMixin):
    model_config = ConfigDict(title='VitalsCreate')