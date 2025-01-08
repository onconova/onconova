from pop.oncology.models import Radiotherapy, RadiotherapyDosage, RadiotherapySetting
from pop.core.schemas import CREATE_IGNORED_FIELDS, create_schema, GetMixin, CreateMixin
from ninja import Schema
from pydantic import Field, ConfigDict
from typing import List 

RadiotherapyDosageBase: Schema = create_schema(
    RadiotherapyDosage, exclude=(*CREATE_IGNORED_FIELDS, 'radiotherapy'),
)

RadiotherapySettingBase: Schema = create_schema(
    RadiotherapySetting, exclude=(*CREATE_IGNORED_FIELDS, 'radiotherapy'),
)

RadiotherapyBase: Schema = create_schema(
    Radiotherapy, exclude=(*CREATE_IGNORED_FIELDS,),
)

class RadiotherapyDosageSchema(RadiotherapyDosageBase, GetMixin):
    model_config = ConfigDict(title='RadiotherapyDosage')

class RadiotherapyDosageCreateSchema(RadiotherapyDosageBase, CreateMixin):
    model_config = ConfigDict(title='RadiotherapyDosageCreate')

class RadiotherapySettingSchema(RadiotherapySettingBase, GetMixin):
    model_config = ConfigDict(title='RadiotherapySetting')

class RadiotherapySettingCreateSchema(RadiotherapySettingBase, CreateMixin):
    model_config = ConfigDict(title='RadiotherapySettingCreate')

class RadiotherapySchema(RadiotherapyBase, GetMixin):
    model_config = ConfigDict(title='Radiotherapy')
    dosages: List[RadiotherapyDosageSchema] = Field(description='Radiation doses administered during the radiotherapy')
    settings: List[RadiotherapySettingSchema] = Field(description='Settings of the radiotherapy irradiation procedure')

class RadiotherapyCreateSchema(RadiotherapyBase, CreateMixin):
    model_config = ConfigDict(title='RadiotherapyCreate')