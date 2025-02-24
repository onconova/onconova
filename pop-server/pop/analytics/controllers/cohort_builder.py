import enum 
from datetime import date, datetime
from typing import get_args, List

from django.db.models import Model as DjangoModel

from ninja_extra import route, api_controller
from ninja_jwt.authentication import JWTAuth
from ninja_extra import api_controller, ControllerBase, route

from pop.core import permissions as perms
from pop.core.utils import is_list, is_optional, is_literal, is_enum
from pop.core.schemas import CodedConceptSchema
from pop.core import filters as schema_filters
from pop.core.schemas.factory.fields import FILTERS_MAP
from pop.core.measures import Measure
from pop.oncology import models as oncological_models
from pop.oncology import schemas as oncological_schemas

from pop.analytics.schemas.cohort_builder import (
    CohortRuleType, CohortBuilderField, 
    CohortBuilderConfig, CohortBuilderEntity,
)


TYPES_MAP = {
    str: CohortRuleType.STRING,
    date: CohortRuleType.DATE,
    datetime: CohortRuleType.DATE,
    int: CohortRuleType.NUMBER,
    float: CohortRuleType.NUMBER,
    bool: CohortRuleType.BOOLEAN,
    CodedConceptSchema: CohortRuleType.CODED_CONCEPT,
    Measure: CohortRuleType.MEASURE,
    enum.Enum: CohortRuleType.ENUM,
}

@api_controller(
    "/cohort-builder", 
    auth=[JWTAuth()], 
    tags=["Cohorts"]
)
class CohortBuilderController(ControllerBase):

    @route.get(
        path='/config', 
        response={
            200: CohortBuilderConfig
        },
        permissions=[perms.CanViewCohorts],
        operation_id='getCohortBuilderConfig',
    )
    def get_cohort_builder_configuration(self):
        fields = {}
        entities = {}
        for model in oncological_models.MODELS:
            schema = getattr(oncological_schemas, f'{model.__name__}Schema', None)
            if not schema or not issubclass(model, DjangoModel):  
                continue
            entity = model.__name__
            entities[entity] = CohortBuilderEntity(name=model._meta.verbose_name.title())

            for field_name, fieldinfo in schema.model_fields.items():
                if field_name in ['id', 'createdAt', 'updatedAt', 'updatedBy', 'createdBy','description']:
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
                    options = [{'name': e.name, 'value': e.value} for e in annotation]
                    annotation = enum.Enum
                    print('SET', options)

                field_type = TYPES_MAP.get(annotation)
                if not field_type:
                    continue
                
                unique_key = f'{entity}.{fieldinfo.alias or field_name}'
                fields[unique_key] = CohortBuilderField(
                    name=str(fieldinfo.title or field_name), 
                    type=field_type, 
                    options = options,
                    entity=entity, 
                    operators=[
                        filter.__name__ for filter in filters
                    ]
                )
                terminology = ''
                if annotation is CodedConceptSchema and fieldinfo.json_schema_extra:
                    terminology = fieldinfo.json_schema_extra.get('x-terminology')
                    fields[unique_key].options = [{'name': 'terminology', 'value': terminology}]
                

        return CohortBuilderConfig(
            entities = entities,
            fields = fields
        )

