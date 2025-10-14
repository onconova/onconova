from typing import List, Literal
from pydantic import Field
from uuid import UUID
from datetime import date as date_aliased

from onconova.core.schemas import BaseSchema, MetadataAnonymizationMixin, CodedConcept
from onconova.core.types import Nullable
from onconova.oncology.models import genomic_signature as orm


class GenomicSignatureCreate(BaseSchema):
    
    __orm_model__ = orm.GenomicSignature
    
    category: orm.GenomicSignatureTypes = Field(
        title="Category", 
        description="Genomic signature discriminator category"
    )
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
        description="Indicates the case of the patient who's lifestyle is assesed",
        title='Patient case',
    )
    date: date_aliased = Field(
        ...,
        description="Clinically-relevant date at which the patient's genomic signature was assessed.",
        title='Assessment date',
    )
    
class GenomicSignature(GenomicSignatureCreate, MetadataAnonymizationMixin):
    
    __anonymization_fields__ = ("date",)
    __anonymization_key__ = "caseId"
    

class TumorMutationalBurdenCreate(GenomicSignatureCreate):
    
    __orm_model__ = orm.TumorMutationalBurden 
    
    category: Literal[orm.GenomicSignatureTypes.TUMOR_MUTATIONAL_BURDEN] = Field(
        default=orm.GenomicSignatureTypes.TUMOR_MUTATIONAL_BURDEN,
        title="Category",
        description="Genomic signature discriminator category",
    )
    value: float = Field(
        ...,
        description='The actual tumor mutational burden (TMB) value in mutations/Mb',
        title='Value',
    )
    status: Nullable[orm.TumorMutationalBurdenStatusChoices] = Field(
        None,
        description='Cclassification of the tumor mutational burden (TMB) status',
        title='Status',
    )

class TumorMutationalBurden(TumorMutationalBurdenCreate, MetadataAnonymizationMixin):

    __anonymization_fields__ = ("date",)
    __anonymization_key__ = "caseId"



class MicrosatelliteInstabilityCreate(GenomicSignatureCreate):
    
    __orm_model__ = orm.MicrosatelliteInstability 
    
    category: Literal[orm.GenomicSignatureTypes.MICROSATELLITE_INSTABILITY] = Field(
        orm.GenomicSignatureTypes.MICROSATELLITE_INSTABILITY,
        title="Category",
        description="Genomic signature discriminator category",
    )
    value: CodedConcept = Field(
        ...,
        description='Microsatellite instability (MSI) classification',
        title='Value',
        json_schema_extra={'x-terminology': 'MicrosatelliteInstabilityState'},
    )

class MicrosatelliteInstability(MicrosatelliteInstabilityCreate, MetadataAnonymizationMixin):

    __anonymization_fields__ = ("date",)
    __anonymization_key__ = "caseId"



class LossOfHeterozygosityCreate(GenomicSignatureCreate):
    
    __orm_model__ = orm.LossOfHeterozygosity
    
    category: Literal[orm.GenomicSignatureTypes.LOSS_OF_HETEROZYGOSITY] = Field(
        orm.GenomicSignatureTypes.LOSS_OF_HETEROZYGOSITY,
        title="Category",
        description="Genomic signature discriminator category",
    )
    value: float = Field(
        ...,
        description='Loss of heterozygosity (LOH) as a percentage',
        title='Value',
    )

class LossOfHeterozygosity(LossOfHeterozygosityCreate, MetadataAnonymizationMixin):
    __anonymization_fields__ = ("date",)
    __anonymization_key__ = "caseId"



class HomologousRecombinationDeficiencyCreate(GenomicSignatureCreate):
    
    __orm_model__ = orm.HomologousRecombinationDeficiency 
    
    category: Literal[orm.GenomicSignatureTypes.HOMOLOGOUS_RECOMBINATION_DEFICIENCY] = (
        Field(
            orm.GenomicSignatureTypes.HOMOLOGOUS_RECOMBINATION_DEFICIENCY,
            title="Category",
            description="Genomic signature discriminator category",
        )
    )
    value: Nullable[float] = Field(
        None,
        description='Homologous recombination deficiency (HRD) score value',
        title='Value',
    )
    interpretation: Nullable[orm.HomologousRecombinationDeficiencyInterpretationChoices] = (
        Field(
            None,
            description='Homologous recombination deficiency (HRD) interpretation',
            title='Interpretation',
        )
    )

class HomologousRecombinationDeficiency(HomologousRecombinationDeficiencyCreate, MetadataAnonymizationMixin):
    
    __anonymization_fields__ = ("date",)
    __anonymization_key__ = "caseId"



class TumorNeoantigenBurdenCreate(GenomicSignatureCreate):
    
    __orm_model__ = orm.TumorNeoantigenBurden 
    
    category: Literal[orm.GenomicSignatureTypes.TUMOR_NEOANTIGEN_BURDEN] = Field(
        orm.GenomicSignatureTypes.TUMOR_NEOANTIGEN_BURDEN,
        title="Category",
        description="Genomic signature discriminator category",
    )
    value: float = Field(
        ...,
        description='The actual tumor neoantigen burden (TNB) value in neoantigens/Mb',
        title='Value',
    )
    
class TumorNeoantigenBurden(TumorNeoantigenBurdenCreate, MetadataAnonymizationMixin):

    __anonymization_fields__ = ("date",)
    __anonymization_key__ = "caseId"



class AneuploidScoreCreate(GenomicSignatureCreate):
    
    __orm_model__ = orm.AneuploidScore
    
    category: Literal[orm.GenomicSignatureTypes.ANEUPLOID_SCORE] = Field(
        orm.GenomicSignatureTypes.ANEUPLOID_SCORE,
        title="Category",
        description="Genomic signature discriminator category",
    )
    value: int = Field(
        ...,
        description='The actual aneuploid score (AS) value in total altered arms',
        title='Value',
    )


class AneuploidScore(AneuploidScoreCreate, MetadataAnonymizationMixin):
    
    __anonymization_fields__ = ("date",)
    __anonymization_key__ = "caseId"

