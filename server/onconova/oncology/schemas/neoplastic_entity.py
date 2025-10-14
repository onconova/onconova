from pydantic import Field
from uuid import UUID
from datetime import date 

from onconova.core.schemas import BaseSchema, MetadataAnonymizationMixin, CodedConcept
from onconova.core.types import Nullable
from onconova.oncology.models import neoplastic_entity as orm

class NeoplasticEntityCreate(BaseSchema):
    
    __orm_model__ = orm.NeoplasticEntity
    
    externalSource: Nullable[str] = Field(
        None,
        description='The digital source of the data, relevant for automated data',
        title='External data source',
    )
    externalSourceId: Nullable[str] = Field(
        None,
        description='The data identifier at the digital source of the data, relevant for automated data',
        title='External data source Id',
    )
    caseId: UUID = Field(
        ...,
        description="Indicates the case of the patient who's neoplasm(s) are recorded",
        title='Patient case',
    )
    relationship: orm.NeoplasticEntityRelationshipChoices = Field(
        ...,
        description='Relationship linking secondary and recurrent tumors to their primary origin or for distinguishing between different phases of the disease.',
        title='Neoplastic relationship',
    )
    relatedPrimaryId: Nullable[UUID] = Field(
        None,
        description='Reference to the primary neoplasm of which the neoplasm(s) originated from.',
        title='Related primary neoplasm',
    )
    assertionDate: date = Field(
        ...,
        description='The date on which the existence of the neoplasm(s) was first asserted or acknowledged',
        title='Assertion date',
    )
    topography: CodedConcept = Field(
        ...,
        description='Anatomical location of the neoplasm(s)',
        title='Topography',
        json_schema_extra={'x-terminology': 'CancerTopography'},
    )
    morphology: CodedConcept = Field(
        ...,
        description='Describes the cell type of the tumor and its biologic activity, in other words, the characteristics of the tumor itself',
        title='Morphology',
        json_schema_extra={'x-terminology': 'CancerMorphology'},
    )
    differentitation: Nullable[CodedConcept] = Field(
        None,
        description='Morphologic differentitation characteristics of the neoplasm(s)',
        title='Differentiation',
        json_schema_extra={'x-terminology': 'HistologyDifferentiation'},
    )
    laterality: Nullable[CodedConcept] = Field(
        None,
        description='Laterality qualifier for the location of the neoplasm(s)',
        title='Laterality',
        json_schema_extra={'x-terminology': 'LateralityQualifier'},
    )

class NeoplasticEntity(NeoplasticEntityCreate, MetadataAnonymizationMixin):

    topographyGroup: Nullable[CodedConcept] = Field(
        None,
        title="Topographical group",
        description="Broad anatomical location of the neoplastic entity",
        json_schema_extra={"x-terminology": "CancerTopographyGroup",},
    )

    __anonymization_fields__ = ("assertionDate",)
    __anonymization_key__ = "caseId"