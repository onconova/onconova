from ninja import Schema
from typing import Literal
from pop.core.schemas import CREATE_IGNORED_FIELDS, create_schema, GetMixin, CreateMixin, ConfigDict
from pop.oncology.models import (
    GenomicSignatureTypes,
    TumorMutationalBurden,
    MicrosatelliteInstability,
    LossOfHeterozygosity,
    HomologousRecombinationDeficiency,
    TumorNeoantigenBurden,
    AneuploidScore,
)

TumorMutationalBurdenBase: Schema = create_schema(
    TumorMutationalBurden, 
    exclude=(*CREATE_IGNORED_FIELDS, 'genomic_signature'),
)

class TumorMutationalBurdenSchema(TumorMutationalBurdenBase, GetMixin):
    category: Literal[GenomicSignatureTypes.TUMOR_MUTATIONAL_BURDEN] = GenomicSignatureTypes.TUMOR_MUTATIONAL_BURDEN # type: ignore
    model_config = ConfigDict(title='TumorMutationalBurden')

class TumorMutationalBurdenCreateSchema(TumorMutationalBurdenBase, CreateMixin):
    category: Literal[GenomicSignatureTypes.TUMOR_MUTATIONAL_BURDEN] = GenomicSignatureTypes.TUMOR_MUTATIONAL_BURDEN # type: ignore    
    model_config = ConfigDict(title='TumorMutationalBurdenCreate')



MicrosatelliteInstabilityBase: Schema = create_schema(
    MicrosatelliteInstability, 
    exclude=(*CREATE_IGNORED_FIELDS, 'genomic_signature'),
)

class MicrosatelliteInstabilitySchema(MicrosatelliteInstabilityBase, GetMixin):
    category: Literal[GenomicSignatureTypes.MICROSATELLITE_INSTABILITY] = GenomicSignatureTypes.MICROSATELLITE_INSTABILITY # type: ignore
    model_config = ConfigDict(title='MicrosatelliteInstability')

class MicrosatelliteInstabilityCreateSchema(MicrosatelliteInstabilityBase, CreateMixin):
    category: Literal[GenomicSignatureTypes.MICROSATELLITE_INSTABILITY] = GenomicSignatureTypes.MICROSATELLITE_INSTABILITY # type: ignore    
    model_config = ConfigDict(title='MicrosatelliteInstabilityCreate')



LossOfHeterozygosityBase: Schema = create_schema(
    LossOfHeterozygosity, 
    exclude=(*CREATE_IGNORED_FIELDS, 'genomic_signature'),
)

class LossOfHeterozygositySchema(LossOfHeterozygosityBase, GetMixin):
    category: Literal[GenomicSignatureTypes.LOSS_OF_HETEROZYGOSITY] = GenomicSignatureTypes.LOSS_OF_HETEROZYGOSITY # type: ignore
    model_config = ConfigDict(title='LossOfHeterozygosity')

class LossOfHeterozygosityCreateSchema(LossOfHeterozygosityBase, CreateMixin):
    category: Literal[GenomicSignatureTypes.LOSS_OF_HETEROZYGOSITY] = GenomicSignatureTypes.LOSS_OF_HETEROZYGOSITY # type: ignore    
    model_config = ConfigDict(title='LossOfHeterozygosityCreate')



HomologousRecombinationDeficiencyBase: Schema = create_schema(
    HomologousRecombinationDeficiency, 
    exclude=(*CREATE_IGNORED_FIELDS, 'genomic_signature'),
)

class HomologousRecombinationDeficiencySchema(HomologousRecombinationDeficiencyBase, GetMixin):
    category: Literal[GenomicSignatureTypes.HOMOLOGOUS_RECOMBINATION_DEFICIENCY] = GenomicSignatureTypes.HOMOLOGOUS_RECOMBINATION_DEFICIENCY # type: ignore
    model_config = ConfigDict(title='HomologousRecombinationDeficiency')

class HomologousRecombinationDeficiencyCreateSchema(HomologousRecombinationDeficiencyBase, CreateMixin):
    category: Literal[GenomicSignatureTypes.HOMOLOGOUS_RECOMBINATION_DEFICIENCY] = GenomicSignatureTypes.HOMOLOGOUS_RECOMBINATION_DEFICIENCY # type: ignore    
    model_config = ConfigDict(title='HomologousRecombinationDeficiencyCreate')



TumorNeoantigenBurdenBase: Schema = create_schema(
    TumorNeoantigenBurden, 
    exclude=(*CREATE_IGNORED_FIELDS, 'genomic_signature'),
)

class TumorNeoantigenBurdenSchema(TumorNeoantigenBurdenBase, GetMixin):
    category: Literal[GenomicSignatureTypes.TUMOR_NEOANTIGEN_BURDEN] = GenomicSignatureTypes.TUMOR_NEOANTIGEN_BURDEN # type: ignore
    model_config = ConfigDict(title='TumorNeoantigenBurden')

class TumorNeoantigenBurdenCreateSchema(TumorNeoantigenBurdenBase, CreateMixin):
    category: Literal[GenomicSignatureTypes.TUMOR_NEOANTIGEN_BURDEN] = GenomicSignatureTypes.TUMOR_NEOANTIGEN_BURDEN # type: ignore    
    model_config = ConfigDict(title='TumorNeoantigenBurdenCreate')



AneuploidScoreBase: Schema = create_schema(
    AneuploidScore, 
    exclude=(*CREATE_IGNORED_FIELDS, 'genomic_signature'),
)

class AneuploidScoreSchema(AneuploidScoreBase, GetMixin):
    category: Literal[GenomicSignatureTypes.ANEUPLOID_SCORE] = GenomicSignatureTypes.ANEUPLOID_SCORE # type: ignore
    model_config = ConfigDict(title='AneuploidScore')

class AneuploidScoreCreateSchema(AneuploidScoreBase, CreateMixin):
    category: Literal[GenomicSignatureTypes.ANEUPLOID_SCORE] = GenomicSignatureTypes.ANEUPLOID_SCORE # type: ignore    
    model_config = ConfigDict(title='AneuploidScoreCreate')



