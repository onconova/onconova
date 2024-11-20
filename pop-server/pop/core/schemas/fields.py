


from typing import Dict, List, Tuple, Optional

from django.db.models.fields import Field as DjangoField
from django.db.models import ManyToManyField

from ninja.orm.fields import TYPES as BASE_TYPES, title_if_lower, create_m2m_link_type
from ninja.schema import Schema 
from ninja.openapi.schema import OpenAPISchema
from pydantic.fields import FieldInfo
from pydantic_core import PydanticUndefined

from pop.terminology.models import CodedConcept as CodedConceptModel

def to_camel_toe(string):
    return ''.join([
        word if n==0 else word.capitalize() 
            for n,word in enumerate(string.split('_'))
    ])

class Reference(Schema):
    type: str = None
    id: str = None
    url: Optional[str] = None

class CodedConcept(Schema):  
    code: str
    system: str
    display: Optional[str] = None
    version: Optional[str] = None
    synonyms: Optional[List[str]] = None
    properties: Optional[Dict] = None

TYPES = {
    **BASE_TYPES,
    # POP fields
    "CodedConceptField": CodedConcept,
}


def get_schema_field(field: DjangoField, *, depth: int = 0, optional: bool = False) -> Tuple:
    "Returns pydantic field from django's model field"
    alias = None
    serialization_alias = None
    default = ...
    default_factory = None
    description = None
    title = None
    max_length = None
    nullable = False
    python_type = None
    json_schema_extra = None 
    examples = []
    # Handle relation fields
    if field.is_relation:
        if depth > 0:
            return get_related_field_schema(field, depth=depth)
        related_model = field.related_model 
        # if isinstance(related_model, str):
        #     app_label, related_model_name = related_model.split('.')
        #     related_model = django_apps.get_model(app_label=app_label, model_name=related_model_name)

        alias = getattr(field, "name", None) and field.name
        if issubclass(related_model, CodedConceptModel):
            json_schema_extra = {'x-terminology', CodedConceptModel.__name__}
            internal_type = 'CodedConceptField'      
            alias = alias.rstrip('_id')
        else:
            internal_type = related_model._meta.get_field('id').get_internal_type()
        
        serialization_alias = to_camel_toe(alias)
        
        if not field.concrete and field.auto_created or field.null or optional:
            default = None
            nullable = True

        related_type = TYPES.get(internal_type, int)

        if field.one_to_many or field.many_to_many:
            m2m_type = create_m2m_link_type(related_type)
            python_type = List[m2m_type]  # type: ignore
            default=[]
        else:
            python_type = related_type

    # Handle all other fields 
    else:
        _f_name, _f_path, _f_pos, field_options = field.deconstruct()
        blank = field_options.get("blank", False)
        null = field_options.get("null", False)
        max_length = field_options.get("max_length")

        internal_type = field.get_internal_type()
        python_type = TYPES[internal_type]

        if field.primary_key or blank or null or optional:
            default = None
            nullable = True

        if field.has_default():
            if callable(field.default):
                default_factory = field.default
            else:
                default = field.default

    if default_factory:
        default = PydanticUndefined

    if nullable:
        python_type = Optional[python_type] 

    description = field.help_text or None
    if field.verbose_name:
        title = title_if_lower(field.verbose_name)
    
    return (
        python_type,
        FieldInfo(
            default=default,
            alias=serialization_alias,
            validation_alias=serialization_alias,
            serialization_alias=serialization_alias,
            default_factory=default_factory,
            title=title,
            examples=examples,
            description=description,
            max_length=max_length,
            json_schema_extra=json_schema_extra,
        ),
    )

def get_related_field_schema(field: DjangoField, *, depth: int) -> Tuple[OpenAPISchema]:
    from pop.core.schemas.factory import create_schema

    model = field.related_model
    schema = create_schema(model, depth=depth - 1)
    default = ...
    if not field.concrete and field.auto_created or field.null:
        default = None
    if isinstance(field, ManyToManyField):
        schema = List[schema]  # type: ignore

    return (
        schema,
        FieldInfo(
            default=default,
            description=field.help_text,
            title=title_if_lower(field.verbose_name),
        ),
    )