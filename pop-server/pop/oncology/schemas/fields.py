from typing import Dict, List, Tuple, Optional

from django.db.models.fields import Field as DjangoField
from django.db.models import ManyToManyField

from ninja.orm.fields import TYPES as BASE_TYPES, title_if_lower, create_m2m_link_type
from ninja.schema import Schema 

from pydantic.fields import FieldInfo
from pydantic_core import PydanticUndefined

from pop.terminology.models import CodedConcept as CodedConceptModel


class Reference(Schema):
    type: str = None
    id: str = None
    url: Optional[str] = None

class CodedConceptSchema(Schema):  
    code: str
    system: str
    display: Optional[str] = None
    version: Optional[str] = None
    synonyms: Optional[List[str]] = None
    properties: Optional[Dict] = None


DJANGO_TO_PYDANTIC_TYPES = {
    **BASE_TYPES,
    # POP fields
    "CodedConceptField": CodedConceptSchema,
}


def get_schema_field(field: DjangoField, *, depth: int = 0, optional: bool = False) -> Tuple[type, FieldInfo]:
    """
    Returns a pydantic field from a django model field.

    This function takes a django model field and returns a tuple containing the
    python type for the field and a pydantic FieldInfo object. The python type
    is determined by the field's internal type and whether or not the field is
    a relation field. The FieldInfo object contains additional information about
    the field such as its default value, alias, title, description, and json
    schema extras.
    """
    field_name = getattr(field, "name", None) and field.name
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
            from pop.oncology.schemas.factory import create_schema
            model = field.related_model
            schema = create_schema(model, depth=depth - 1)
            default = ...
            if not field.concrete and field.auto_created or field.null:
                default = None
            if isinstance(field, ManyToManyField):
                schema = List[schema]
            python_type = schema
        else:
            related_model = field.related_model 
            if issubclass(related_model, CodedConceptModel):
                json_schema_extra = {'x-terminology', CodedConceptModel.__name__}
                internal_type = 'CodedConceptField'    
            else:
                internal_type = related_model._meta.get_field('id').get_internal_type()
                field_name += '_id'
            if not field.concrete and field.auto_created or field.null or optional:
                default = None
                nullable = True

            related_type = DJANGO_TO_PYDANTIC_TYPES.get(internal_type, int)

            if field.one_to_many or field.many_to_many:
                m2m_type = create_m2m_link_type(related_type)
                python_type = List[m2m_type]  # type: ignore
                default=[]
            else:
                python_type = related_type

    else:
        # Handle non-relation fields
        _f_name, _f_path, _f_pos, field_options = field.deconstruct()
        blank = field_options.get("blank", False)
        null = field_options.get("null", False)
        max_length = field_options.get("max_length")

        internal_type = field.get_internal_type()
        python_type = DJANGO_TO_PYDANTIC_TYPES[internal_type]

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

    return field_name, (
        python_type,
        FieldInfo(
            default=default,
            default_factory=default_factory,
            alias=to_camel_case(field_name),
            validation_alias=to_camel_case(field_name),
            serialization_alias=to_camel_case(field_name),
            title=title,
            examples=examples,
            description=description,
            max_length=max_length,
            json_schema_extra=json_schema_extra,
        ),
    )

def to_camel_case(string: str) -> str:
    """
    Convert a string from snake_case to camelCase.

    Args:
        string (str): The string to convert.

    Returns:
        str: The converted string.
    """
    return ''.join([
        word if n==0 else word.capitalize()
            for n,word in enumerate(string.split('_'))
    ])

