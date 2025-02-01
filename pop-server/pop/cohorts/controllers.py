from typing import List

from django.db.models import Q, Value, Case, When, F, Func, IntegerField, CharField
from django.db.models.expressions import RawSQL

from ninja import Field, Schema, Query
from ninja_extra import route, api_controller
from ninja_jwt.authentication import JWTAuth
from ninja_extra.pagination import paginate
from ninja_extra import api_controller, ControllerBase, route
from django.shortcuts import get_object_or_404
from pop.cohorts.schemas import CohortSchema, CohortCreateSchema, CohortFilters
from pop.cohorts.models import Cohort
from pop.oncology.schemas import PatientCaseSchema

from collections import defaultdict

from pop.core.schemas import CodedConceptSchema, Paginated, ModifiedResourceSchema
from pop.core.measures import MeasureSchema
from pop.oncology import models as oncological_models
from pop.oncology import schemas as oncological_schemas

from .schemas import CohortRuleType, CohortBuilderField, CohortBuilderConfig, CohortBuilderEntity, CohortStatisticsSchema
from pydantic import AliasChoices, BaseModel as PydanticBaseModel
from django.db.models import Model as DjangoModel

from pop.core.utils import is_list, is_optional, is_literal, is_enum, to_camel_case, camel_to_snake

from typing import get_args, List, Tuple, Optional
import enum 
import warnings
from uuid import UUID
from datetime import date, datetime
from pop.core.schemas import filters as schema_filters
from pop.terminology.models import CodedConcept as CodedConceptModel
from pop.core.schemas.fields import DJANGO_TO_PYDANTIC_TYPES, FILTERS_MAP


TYPES_MAP = {
    str: CohortRuleType.STRING,
    date: CohortRuleType.DATE,
    datetime: CohortRuleType.DATE,
    int: CohortRuleType.NUMBER,
    float: CohortRuleType.NUMBER,
    bool: CohortRuleType.BOOLEAN,
    CodedConceptSchema: CohortRuleType.CODED_CONCEPT,
    MeasureSchema: CohortRuleType.MEASURE,
    enum.Enum: CohortRuleType.ENUM,
}

@api_controller(
    "/cohorts", 
    auth=[JWTAuth()], 
    tags=["Cohorts"]
)
class CohortsController(ControllerBase):


    @route.get(
        path='', 
        response={
            200: Paginated[CohortSchema],
        },
        operation_id='getCohorts',
    )
    @paginate()
    def get_all_cohorts_matching_the_query(self, query: Query[CohortFilters]): # type: ignore
        queryset = Cohort.objects.all().order_by('-created_at')
        return query.filter(queryset)

    @route.post(
        path='', 
        response={
            201: ModifiedResourceSchema
        },
        operation_id='createCohort',
    )
    def create_cohort(self, payload: CohortCreateSchema): # type: ignore
        cohort = payload.model_dump_django(user=self.context.request.user)
        cohort.update_cohort_cases()
        return cohort
        

    @route.get(
        path='/{cohortId}', 
        response={
            200: CohortSchema,
            404: None,
        },
        operation_id='getCohortById',
    )
    def get_cohort_by_id(self, cohortId: str):
        return get_object_or_404(Cohort, id=cohortId)
        

    @route.delete(
        path='/{cohortId}', 
        response={
            204: None, 
            404: None,
        },
        operation_id='deleteCohortById',
    )
    def delete_cohort(self, cohortId: str):
        get_object_or_404(Cohort, id=cohortId).delete()
        return 204, None
    
    
    @route.put(
        path='/{cohortId}', 
       response={
            200: ModifiedResourceSchema,
            404: None,
        },
        operation_id='updateCohort',
    )
    def update_cohort(self, cohortId: str, payload: CohortCreateSchema): # type: ignore
        cohort = get_object_or_404(Cohort, id=cohortId)
        cohort = payload.model_dump_django(instance=cohort, user=self.context.request.user)
        cohort.update_cohort_cases()
        return cohort



    @route.get(
        path='/{cohortId}/statistics', 
        response={
            200: CohortStatisticsSchema,
            404: None,
        },
        operation_id='getCohortStatistics',
    )
    def get_cohort_statistics(self, cohortId: str):
        cohort = get_object_or_404(Cohort, id=cohortId)
        return CohortStatisticsSchema(
            ageAverage = cohort.age_average,
            ageStdDev = cohort.age_stddev,
            dataCompletionAverage = cohort.data_completion_average,
            dataCompletionStdDev = cohort.data_completion_stddev,
        )


    @route.get(
        path='/{cohortId}/cases', 
        response={
            200: Paginated[PatientCaseSchema],
            404: None,
        },
        operation_id='getCohortCases',
    )
    @paginate()
    def get_cohort_cases(self, cohortId: str):
        return get_object_or_404(Cohort, id=cohortId).cases.all()


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
        operation_id='getCohortBuilderConfig',
    )
    def get_cohort_builder_configuration(self):
        fields = {}
        entities = {}
        for model in oncological_models.__all__:
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