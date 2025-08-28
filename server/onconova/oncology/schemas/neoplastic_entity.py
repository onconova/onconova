from pydantic import AliasChoices, Field

from onconova.core.anonymization import AnonymizationConfig
from onconova.core.schemas import CodedConcept as CodedConceptSchema
from onconova.core.serialization.metaclasses import (
    ModelCreateSchema,
    ModelGetSchema,
    SchemaConfig,
)
from onconova.core.types import Nullable
from onconova.oncology import models as orm


class NeoplasticEntitySchema(ModelGetSchema):

    topographyGroup: Nullable[CodedConceptSchema] = Field(
        None,
        title="Topographical group",
        alias="topography_group",
        description="Broad anatomical location of the neoplastic entity",
        validation_alias=AliasChoices("topographyGroup", "topography_group"),
        json_schema_extra={
            "x-terminology": "CancerTopographyGroup",
        },
    )
    config = SchemaConfig(
        model=orm.NeoplasticEntity,
        anonymization=AnonymizationConfig(fields=["assertionDate"], key="caseId"),
    )


class NeoplasticEntityCreateSchema(ModelCreateSchema):
    config = SchemaConfig(model=orm.NeoplasticEntity)
    config = SchemaConfig(model=orm.NeoplasticEntity)
