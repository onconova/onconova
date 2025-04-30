from datetime import date, datetime
from typing import Optional, List, Dict, Union, Any
from uuid import UUID
from enum import Enum
from ninja import Schema
from psycopg.types.range import Range as PostgresRange
from pydantic import Field, model_validator, AliasChoices
from ninja_extra.schemas import NinjaPaginationResponseSchema


class Paginated(NinjaPaginationResponseSchema):
    pass
    
class ModifiedResource(Schema):
    id: UUID = Field(description='Unique identifier of the modified resource')
    description: Optional[str] = Field(None, description='A human-readable description of the modified resource')

class CodedConcept(Schema):  
    code: str = Field(description='Unique code within a coding system that identifies a concept')
    system: str = Field(description='The canonical URL of the code system defining the concept')
    display: Optional[str] = Field(default=None, description='Human readable description of the concept')
    version: Optional[str] = Field(default=None, description='Release version of the code system, if available')
    synonyms: Optional[List[str]] = Field(default=None, description='List of synonyms or alternative representations of the concept')
    properties: Optional[Dict] = Field(default=None, description='Other properties associated to the concept by the code system or otherwise')

class Range(Schema):  
    start: Optional[Union[int, float]] = Field(description='The lower bound of the range')
    end: Optional[Union[int, float]] = Field(default=None, description='The upper bound of the range, if not exists, assumed to be unbounded')

    @model_validator(mode='before')
    def validate_data(cls, obj):
        range = obj._obj
        if isinstance(range, tuple):
            return {'start': range[0], 'end': range[1],}
        elif isinstance(range, PostgresRange):
            return {'start': range.lower, 'end': range.upper,}
        else:
            return obj
    
class Period(Schema):  
    start: Optional[date] = Field(default=None, description='The start date of the time period')
    end: Optional[date] = Field(default=None, description='The end date of the time period')

    @model_validator(mode='before')
    def validate_data(cls, obj):
        period = obj._obj
        if isinstance(period, tuple):
            return {'start': period[0], 'end': period[1],}
        elif isinstance(period, PostgresRange):
            return {'start': period.lower, 'end': period.upper,}
        else:
            return obj


class HistoryEventCategory(str, Enum):
    CREATE = 'create'
    UPDATE = 'update'
    DELETE = 'delete'
    EXPORT = 'export'
    IMPORT = 'import'
    DOWNLOAD = 'download'

class HistoryEvent(Schema):

    id: Any = Field(
        title='Event ID',
        description='The unique identifier of the history event',
        alias='pgh_id',
        validation_alias=AliasChoices('id','pgh_id'),
    )
    category: HistoryEventCategory = Field(
        title='Category',
        description='The type of history event',
        alias='pgh_label',
        validation_alias=AliasChoices('category','pgh_label'),
    )
    timestamp: datetime = Field(
        title='Timestamp',
        description='Timestamp of the history event',
        alias='pgh_created_at',
        validation_alias=AliasChoices('timestamp','pgh_created_at'),
    )
    user: Optional[str] = Field(
        default=None,
        title='User',
        description='Username of the user that triggered the event, if applicable',
    )
    url: Optional[str] = Field(
        default=None,
        title='Endpoint',
        description='Endpoint URL through which the event was triggered, if applicable',
    )
    snapshot: Dict = Field(
        title='Data snapshopt',
        description='Data snapshopt at the time of the event',
    )
    differential: Optional[Dict] = Field(
        title='Data differential',
        description='Data changes introduced by the event, if applicable',
    )
    context: Optional[Dict] = Field(
        title='Context',
        description='Context sorrounding the event',
        alias='pgh_context',
        validation_alias=AliasChoices('context','pgh_context'),
    )

    @staticmethod
    def resolve_user(obj):
        return obj.pgh_context['username']

    @staticmethod 
    def resolve_category(obj):
        return {
            'create': HistoryEventCategory.CREATE,
            'update': HistoryEventCategory.UPDATE,
            'delete': HistoryEventCategory.DELETE,
            'export': HistoryEventCategory.EXPORT,
            'import': HistoryEventCategory.IMPORT,
            'download': HistoryEventCategory.DOWNLOAD,
        }.get(obj.pgh_label)
    
    @staticmethod 
    def resolve_snapshot(obj):
        return obj.pgh_data

    @staticmethod 
    def resolve_differential(obj):
        return obj.pgh_diff

    @staticmethod
    def bind_schema(schema: Schema):
        class HistoryEventWithSchema(HistoryEvent):
            @staticmethod
            def resolve_snapshot(obj):
                # Create a new instance of the model based on snapshot data to automatically resolve foreign keys
                instance = schema.get_orm_model()(**{key: val for key, val in obj.pgh_data.items() })
                # Cast to model schema
                return schema.model_validate(instance).model_dump(exclude_unset=True) | {'id': instance.id}
            
            @staticmethod 
            def resolve_differential(obj):
                if obj.pgh_diff:
                    return schema.model_construct(**obj.pgh_diff).model_dump(exclude_defaults=True)
        return HistoryEventWithSchema
