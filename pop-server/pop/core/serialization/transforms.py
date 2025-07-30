from django.db.models import F
from pop.core.auth.schemas import UserSchema
from pop.core.measures.schemas import Measure
from pop.core.schemas import CodedConcept as CodedConceptSchema


class DjangoTransform:
    name: str = ""
    lookup: str = ""
    description: str = ""
    value_type: type

    @staticmethod
    def generate_annotation_expression(field_path, *args):
        raise NotImplementedError


class GetCodedConceptDisplay(DjangoTransform):
    name = "display"
    description = "Get the human-readable representation of the coded concept"
    value_type = CodedConceptSchema

    @staticmethod
    def generate_annotation_expression(field_path, *args):
        return F(f"{field_path}__display")


class GetCodedConceptCode(DjangoTransform):
    name = "code"
    description = "Get the machine-readable representation of the coded concept"
    value_type = CodedConceptSchema

    @staticmethod
    def generate_annotation_expression(field_path, *args):
        return F(f"{field_path}__code")


class GetCodedConceptSystem(DjangoTransform):
    name = "system"
    description = (
        "Get canonical URL of the coding system used to represent the coded concept"
    )
    value_type = CodedConceptSchema

    @staticmethod
    def generate_annotation_expression(field_path, *args):
        return F(f"{field_path}__system")


class GetUserUsername(DjangoTransform):
    name = "username"
    description = "Get username of an user"
    value_type = UserSchema

    @staticmethod
    def generate_annotation_expression(field_path, *args):
        return F(f"{field_path}__username")
