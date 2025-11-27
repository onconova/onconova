from typing import List, Literal
from pydantic import Field
from datetime import date as date_aliased

from onconova.core.schemas import BaseSchema, MetadataAnonymizationMixin, MetadataMixin, CodedConcept
from onconova.core.types import Nullable, UUID
from onconova.oncology.models import tumor_board as orm




class UnspecifiedTumorBoardCreate(BaseSchema):
    
    __orm_model__ = orm.UnspecifiedTumorBoard 
    
    category: Literal[orm.TumorBoardSpecialties.UNSPECIFIED] = Field(
        default=orm.TumorBoardSpecialties.UNSPECIFIED,
        title="Category",
        description="Tumor board discriminator category",
    )
    externalSource: Nullable[str] = Field(
        default=None,
        description='The digital source of the data, relevant for automated data',
        title='External data source',
    )
    externalSourceId: Nullable[str] = Field(
        default=None,
        description='The data identifier at the digital source of the data, relevant for automated data',
        title='External data source Id',
    )
    caseId: UUID = Field(
        ...,
        description='Indicates the case of the patient which was discussed at the tumor board',
        title='Patient case',
    )
    date: date_aliased = Field(
        ...,
        description='Date at which the tumor board took place and/or when the board provided a recommendation.',
        title='Date',
    )
    relatedEntitiesIds: Nullable[List[UUID]] = Field(
        default=None,
        description='References to the neoplastic entities that were the focus of the tumor board.',
        title='Related neoplastic entities',
    )
    recommendations: Nullable[List[CodedConcept]] = Field(
        default=None,
        description="Recommendation(s) provided by the board regarding the patient's care",
        title='Recommendations',
        json_schema_extra={'x-terminology': 'TumorBoardRecommendation'},
    )


class UnspecifiedTumorBoard(UnspecifiedTumorBoardCreate, MetadataAnonymizationMixin):
    
    category: Literal[orm.TumorBoardSpecialties.UNSPECIFIED] = Field(
        default=orm.TumorBoardSpecialties.UNSPECIFIED,
        title="Category",
        description="Tumor board discriminator category",
    )
    __anonymization_fields__ = ("date",)
    __anonymization_key__ = "caseId"
    
    

class MolecularTherapeuticRecommendationCreate(BaseSchema):
    
    __orm_model__ = orm.MolecularTherapeuticRecommendation 
    
    externalSource: Nullable[str] = Field(
        default=None,
        description='The digital source of the data, relevant for automated data',
        title='External data source',
    )
    externalSourceId: Nullable[str] = Field(
        default=None,
        description='The data identifier at the digital source of the data, relevant for automated data',
        title='External data source Id',
    )
    expectedEffect: Nullable[CodedConcept] = Field(
        default=None,
        description='Classification of the expected effect of the drug',
        title='Expected medication action',
        json_schema_extra={'x-terminology': 'ExpectedDrugAction'},
    )
    clinicalTrial: Nullable[str] = Field(
        default=None,
        description='Clinical trial (NCT-Iddentifier) recommended by the board for enrollment',
        title='Recommended clinical trial',
        max_length=15,
    )
    offLabelUse: Nullable[bool] = Field(
        default=None,
        description='Whether the medication(s) recommended were off-label',
        title='Off-label use',
    )
    withinSoc: Nullable[bool] = Field(
        default=None,
        description='Whether the medication(s) recommended were within standard of care',
        title='Within SOC',
    )
    drugs: Nullable[List[CodedConcept]] = Field(
        default=None,
        description='Drugs(s) being recommended',
        title='Drug(s)',
        json_schema_extra={'x-terminology': 'AntineoplasticAgent'},
    )
    supportingGenomicVariantsIds: Nullable[List[UUID]] = Field(
        default=None,
        description='Genomic variants that support the recommendation',
        title='Supporting genomic variants',
    )
    supportingGenomicSignaturesIds: Nullable[List[UUID]] = Field(
        default=None,
        description='Genomic signatures that support the recommendation',
        title='Supporting genomic signatures',
    )
    supportingTumorMarkersIds: Nullable[List[UUID]] = Field(
        default=None,
        description='Tumor markers that support the recommendation',
        title='Supporting tumor markers',
    )


class MolecularTherapeuticRecommendation(MolecularTherapeuticRecommendationCreate, MetadataMixin):
    pass


class MolecularTumorBoardCreate(BaseSchema):
    
    __orm_model__ = orm.MolecularTumorBoard 
    
    category: Literal[orm.TumorBoardSpecialties.MOLECULAR] = Field(
        default=orm.TumorBoardSpecialties.MOLECULAR,
        title="Category",
        description="Tumor board discriminator category",
    )
    externalSource: Nullable[str] = Field(
        default=None,
        description='The digital source of the data, relevant for automated data',
        title='External data source',
    )
    externalSourceId: Nullable[str] = Field(
        default=None,
        description='The data identifier at the digital source of the data, relevant for automated data',
        title='External data source Id',
    )
    caseId: UUID = Field(
        ...,
        description='Indicates the case of the patient which was discussed at the tumor board',
        title='Patient case',
    )
    date: date_aliased = Field(
        ...,
        description='Date at which the tumor board took place and/or when the board provided a recommendation.',
        title='Date',
    )
    relatedEntitiesIds: Nullable[List[UUID]] = Field(
        default=None,
        description='References to the neoplastic entities that were the focus of the tumor board.',
        title='Related neoplastic entities',
    )
    recommendations: Nullable[List[CodedConcept]] = Field(
        default=None,
        description="Recommendation(s) provided by the board regarding the patient's care",
        title='Recommendations',
        json_schema_extra={'x-terminology': 'TumorBoardRecommendation'},
    )
    conductedMolecularComparison: Nullable[bool] = Field(
        default=None,
        description='Indicates whether a molecular comparison was conducted during the molecular tumor board',
        title='Conducted molecular comparison?',
    )
    molecularComparisonMatchId: Nullable[UUID] = Field(
        default=None,
        description='The neoplastic entity that was matched during the molecular comparison',
        title='Molecular comparison match',
    )
    conductedCupCharacterization: Nullable[bool] = Field(
        default=None,
        description='Whether there was a cancer of unknown primary (CUP) characterization during the molecular tumor board.',
        title='Conducted CUP characterization?',
    )
    characterizedCup: Nullable[bool] = Field(
        default=None,
        description='Whether the cancer of unknown primary (CUP) characterization was successful.',
        title='Successful CUP characterization?',
    )
    reviewedReports: List[str] = Field(
        default_factory=list,
        description='List of genomic reports reviewed during the board meeting.',
        title='Reviewed Reports',
    )

class MolecularTumorBoard(MolecularTumorBoardCreate, MetadataAnonymizationMixin):
    
    therapeuticRecommendations: List[MolecularTherapeuticRecommendation] = Field(
        title="Therapeutic Recommendations",
        description="Therapeutic recommendations of the molecular tumor board",
    )
    __anonymization_fields__ = ("date",)
    __anonymization_key__ = "caseId"
    