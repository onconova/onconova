from pop.core.anonymization import AnonymizationConfig
from pop.core.schemas import CodedConcept as CodedConceptSchema
from pop.core.serialization.metaclasses import (
    ModelCreateSchema,
    ModelGetSchema,
    SchemaConfig,
)
from pop.core.types import Nullable
from pop.oncology import models as orm
from pydantic import AliasChoices, Field


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
