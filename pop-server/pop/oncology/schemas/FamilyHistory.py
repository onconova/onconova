from pop.oncology.models import FamilyHistory
from pop.core.schemas import CREATE_IGNORED_FIELDS, create_schema, GetMixin, CreateMixin, ConfigDict
from ninja import Schema


FamilyHistoryBase: Schema = create_schema(
    FamilyHistory, 
    exclude=(*CREATE_IGNORED_FIELDS,),
)

class FamilyHistorySchema(FamilyHistoryBase, GetMixin):
    model_config = ConfigDict(title='FamilyHistory')
    
class FamilyHistoryCreateSchema(FamilyHistoryBase, CreateMixin):
    model_config = ConfigDict(title='FamilyHistoryCreate')