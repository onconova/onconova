from typing import List

from django.db.models import Q, Value, Case, When, F, Func, IntegerField, CharField
from django.db.models.expressions import RawSQL

from ninja import Field, Schema, Query
from ninja_extra import route, api_controller
from ninja_jwt.authentication import JWTAuth
from ninja_extra.pagination import paginate
from ninja_extra import api_controller, ControllerBase, route
 
from collections import defaultdict

from pop.core.schemas import Paginated, CodedConceptSchema
from pop.oncology.models  import (
    NeoplasticEntity,
    TNMStaging,
)
from pop.oncology.schemas import (
    NeoplasticEntitySchema,
    StagingSchema,
)

from .schemas import CohortBuilderField, CohortBuilderConfig, CohortBuilderEntity
from pydantic import AliasChoices, BaseModel as PydanticBaseModel

from pop.core.utils import is_list, is_optional, is_literal, is_enum, to_camel_case, camel_to_snake


class TerminologyFilters(Schema):
    search_term: str = Field(None, alias='query')
    codes: List[str] = Field(None, alias='codes') # type: ignore

def get_matching_score_expression(query, score): 
    return Case(
        When(query, then=Value(score)),
        default=Value(0),
        output_field=IntegerField(),
    )


ONCOLOGICAL_MODELS = (
    NeoplasticEntity, TNMStaging,
)
ONCOLOGICAL_SCHEMAS = (
    NeoplasticEntitySchema,
    StagingSchema,
)

from typing import get_args, List, Tuple, Optional
import enum 
import warnings
from uuid import UUID
from datetime import date, datetime
from pop.core.schemas import filters as schema_filters
from pop.terminology.models import CodedConcept as CodedConceptModel
from pop.core.schemas.fields import DJANGO_TO_PYDANTIC_TYPES, FILTERS_MAP

TYPES_MAP = {
    str: 'string',
    date: 'date',
    datetime: 'date',
    int: 'number',
    float: 'number',
    bool: 'boolean',
    CodedConceptSchema: 'codedConcept'
}

@api_controller(
    "/cohorts", 
    # auth=[JWTAuth()], 
    tags=["Cohorts"]
)
class CohortsController(ControllerBase):
    @route.get(
        path='/builder/config', 
        response={
            200: CohortBuilderConfig
        },
        operation_id='getCohortBuilderConfig',
    )
    def get_cohort_builder_configuration(self):
        fields = {}
        entities = {}
        for schema, model in zip(ONCOLOGICAL_SCHEMAS, ONCOLOGICAL_MODELS):
            entity = model._meta.get_field('case')._related_name
            entities[entity] = CohortBuilderEntity(name=entity.replace('_',' ').capitalize())

            for field_name, fieldinfo in schema.model_fields.items():
                if field_name in ['id, createdAt', 'updatedAt', 'updatedBy', 'createdBy']:
                    continue

                annotation = fieldinfo.annotation

                # Check if field is optional
                if is_literal(annotation):
                    continue

                filters = [] 
                # Check if field is optional
                if is_optional(annotation):
                    filters += schema_filters.NULL_FILTERS
                    annotation = get_args(annotation)[0]

                # Add the filters for the corresponding type        
                filters += FILTERS_MAP.get(annotation, [])
                if field_name.endswith('Id') or field_name.endswith('Ids'):
                    continue
                            
                options = []
                if is_enum(annotation):
                    for filter in schema_filters.ENUM_FILTERS:
                        filter.value_type = List[annotation] if is_list(filter.value_type) else annotation
                        filters.append(filter)

                field_type = annotation
                
                fields[fieldinfo.alias or field_name] = CohortBuilderField(
                    name=str(fieldinfo.title or field_name), 
                    type=TYPES_MAP.get(field_type, str(field_type)), 
                    entity=entity, 
                    operators=[
                        filter.__name__ for filter in filters
                    ]
                )
                terminology = ''
                if annotation is CodedConceptSchema and fieldinfo.json_schema_extra:
                    terminology = fieldinfo.json_schema_extra.get('x-terminology')
                    print('terminology', terminology)
                    fields[fieldinfo.alias or field_name].options = [{'name': 'terminology', 'value': terminology}]

        return CohortBuilderConfig(
            entities = entities,
            fields = fields
        )

