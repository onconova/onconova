from pop.oncology.models import TreatmentResponse
from pop.core.schemas import CREATE_IGNORED_FIELDS, create_schema, GetMixin, CreateMixin, ConfigDict
from ninja import Schema

TreatmentResponseBase: Schema = create_schema(
    TreatmentResponse, 
    exclude=(*CREATE_IGNORED_FIELDS,),
)

class TreatmentResponseSchema(TreatmentResponseBase, GetMixin):
    model_config = ConfigDict(title='TreatmentResponse')

class TreatmentResponseCreateSchema(TreatmentResponseBase, CreateMixin):
    model_config = ConfigDict(title='TreatmentResponseCreate',)
