from typing import Dict, List, Tuple, Optional

from django.db.models.fields import Field as DjangoField
from django.db.models import ManyToManyField
from django.contrib.auth import get_user_model


from ninja.orm.fields import TYPES as BASE_TYPES, title_if_lower, create_m2m_link_type
from ninja.schema import Schema 

from pydantic import AliasChoices
from pydantic.fields import FieldInfo
from pydantic_core import PydanticUndefined

from pop.terminology.models import CodedConcept as CodedConceptModel
from pop.core.schemas import CodedConceptSchema, UserSchema

UserModel = get_user_model()

DJANGO_TO_PYDANTIC_TYPES = {
    **BASE_TYPES,
    # POP fields
}


def get_schema_field(
        field: DjangoField, 
        *, 
        expand: bool = False, 
        optional: bool = False
    ) -> Tuple[type, FieldInfo]:
    """
    Returns a pydantic field from a django model field.

    This function takes a django model field and returns a tuple containing the
    python type for the field and a pydantic FieldInfo object. The python type
    is determined by the field's internal type and whether or not the field is
    a relation field. The FieldInfo object contains additional information about
    the field such as its default value, alias, title, description, and json
    schema extras.

    Args:
        field (DjangoField): The django model field to convert.
        expand (bool, optional): Whether to expand the relation field. Defaults to False.
        optional (bool, optional): Whether the field is optional. Defaults to False.

    Returns:
        Tuple[type, FieldInfo]: A tuple containing the python type for the field and a pydantic FieldInfo object.
    """
    django_field_name = getattr(field, "name", None) and field.name
    default = ...
    default_factory = None
    description = None
    title = None
    max_length = None
    nullable = False
    python_type = None
    related_type = None
    examples = []    
    json_schema_extra = dict(
        orm_name = django_field_name,    
        is_coded_concept = False,
        is_relation = bool(field.is_relation),
        many_to_many = bool(field.many_to_many),
        one_to_many = bool(field.one_to_many),
        expanded = expand,
    )
    
    # Handle relation fields
    if field.is_relation:
        if expand:
            from pop.core.schemas import create_schema
            model = field.related_model
            schema = create_schema(model)
            if not field.concrete and field.auto_created or field.null:
                default = None
            if field.one_to_many or field.many_to_many:
                schema = List[schema]
                default=[]

            python_type = schema
        else:
            related_model = field.related_model 
            if issubclass(related_model, CodedConceptModel):
                json_schema_extra['is_coded_concept'] = True
                json_schema_extra['terminology'] = related_model.__name__
                related_type = CodedConceptSchema   
            else:
                internal_type = related_model._meta.get_field('id').get_internal_type()
                django_field_name += '_id'

            if not field.concrete and field.auto_created or field.null or optional:
                default = None
                nullable = True

            if not related_type:
                related_type = DJANGO_TO_PYDANTIC_TYPES.get(internal_type, int)

            if field.one_to_many or field.many_to_many:
                python_type = List[related_type] 
                django_field_name += 's'
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

    schema_field_name = to_camel_case(django_field_name)

    return schema_field_name, (
        python_type,
        FieldInfo(
            default=default,
            default_factory=default_factory,
            alias=django_field_name,
            validation_alias=AliasChoices(schema_field_name, django_field_name),
            serialization_alias=schema_field_name,
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

