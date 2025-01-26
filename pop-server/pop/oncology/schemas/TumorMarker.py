from pop.oncology.models import TumorMarker
from pop.core.schemas import ModelSchema, CREATE_IGNORED_FIELDS
from pydantic import Field
from typing import Union 

class TumorMarkerSchema(ModelSchema):
    description: str = Field(description='Human-readable description of the tumor marker') 

    class Meta:
        name = 'TumorMarker'
        model = TumorMarker
        fields = '__all__'

class TumorMarkerCreateSchema(ModelSchema):
    
    class Meta:
        name = 'TumorMarkerCreate'
        model = TumorMarker
        exclude = (
            *CREATE_IGNORED_FIELDS,
        )
