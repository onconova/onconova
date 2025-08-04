from ninja import Field
from typing import Literal

from pop.oncology import models as orm
from pop.oncology.models.genomic_signature import GenomicSignatureTypes
from pop.core.serialization.metaclasses import (
    ModelGetSchema,
    ModelCreateSchema,
    SchemaConfig,
)
from pop.core.anonymization import AnonymizationConfig


class GenomicSignatureSchema(ModelGetSchema):
    category: GenomicSignatureTypes = Field(title="Category", description="Genomic signature discriminator category")
    config = SchemaConfig(
        model=orm.GenomicSignature,
        anonymization=AnonymizationConfig(fields=["date"], key="caseId"),
    )


class TumorMutationalBurdenSchema(ModelGetSchema):
    category: Literal[GenomicSignatureTypes.TUMOR_MUTATIONAL_BURDEN] = Field(default=GenomicSignatureTypes.TUMOR_MUTATIONAL_BURDEN, title="Category", description="Genomic signature discriminator category")
    config = SchemaConfig(
        model=orm.TumorMutationalBurden,
        exclude=["genomic_signature"],
        anonymization=AnonymizationConfig(fields=["date"], key="caseId"),
    )


class TumorMutationalBurdenCreateSchema(ModelCreateSchema):
    category: Literal[GenomicSignatureTypes.TUMOR_MUTATIONAL_BURDEN] = Field(GenomicSignatureTypes.TUMOR_MUTATIONAL_BURDEN, title="Category", description="Genomic signature discriminator category")
    config = SchemaConfig(
        model=orm.TumorMutationalBurden, exclude=["genomic_signature"]
    )


class MicrosatelliteInstabilitySchema(ModelGetSchema):
    category: Literal[GenomicSignatureTypes.MICROSATELLITE_INSTABILITY] = Field(GenomicSignatureTypes.MICROSATELLITE_INSTABILITY, title="Category", description="Genomic signature discriminator category")
    config = SchemaConfig(
        model=orm.MicrosatelliteInstability,
        exclude=["genomic_signature"],
        anonymization=AnonymizationConfig(fields=["date"], key="caseId"),
    )


class MicrosatelliteInstabilityCreateSchema(ModelCreateSchema):
    category: Literal[GenomicSignatureTypes.MICROSATELLITE_INSTABILITY] = Field(GenomicSignatureTypes.MICROSATELLITE_INSTABILITY, title="Category", description="Genomic signature discriminator category")
    config = SchemaConfig(
        model=orm.MicrosatelliteInstability, exclude=["genomic_signature"]
    )


class LossOfHeterozygositySchema(ModelGetSchema):
    category: Literal[GenomicSignatureTypes.LOSS_OF_HETEROZYGOSITY] = Field(GenomicSignatureTypes.LOSS_OF_HETEROZYGOSITY, title="Category", description="Genomic signature discriminator category")
    config = SchemaConfig(
        model=orm.LossOfHeterozygosity,
        exclude=["genomic_signature"],
        anonymization=AnonymizationConfig(fields=["date"], key="caseId"),
    )


class LossOfHeterozygosityCreateSchema(ModelCreateSchema):
    category: Literal[GenomicSignatureTypes.LOSS_OF_HETEROZYGOSITY] = Field(GenomicSignatureTypes.LOSS_OF_HETEROZYGOSITY, title="Category", description="Genomic signature discriminator category")
    config = SchemaConfig(model=orm.LossOfHeterozygosity, exclude=["genomic_signature"])


class HomologousRecombinationDeficiencySchema(ModelGetSchema):
    category: Literal[GenomicSignatureTypes.HOMOLOGOUS_RECOMBINATION_DEFICIENCY] = Field(GenomicSignatureTypes.HOMOLOGOUS_RECOMBINATION_DEFICIENCY, title="Category", description="Genomic signature discriminator category")
    config = SchemaConfig(
        model=orm.HomologousRecombinationDeficiency,
        exclude=["genomic_signature"],
        anonymization=AnonymizationConfig(fields=["date"], key="caseId"),
    )


class HomologousRecombinationDeficiencyCreateSchema(ModelCreateSchema):
    category: Literal[GenomicSignatureTypes.HOMOLOGOUS_RECOMBINATION_DEFICIENCY] = Field(GenomicSignatureTypes.HOMOLOGOUS_RECOMBINATION_DEFICIENCY, title="Category", description="Genomic signature discriminator category")
    config = SchemaConfig(
        model=orm.HomologousRecombinationDeficiency, exclude=["genomic_signature"]
    )


class TumorNeoantigenBurdenSchema(ModelGetSchema):
    category: Literal[GenomicSignatureTypes.TUMOR_NEOANTIGEN_BURDEN] = Field(GenomicSignatureTypes.TUMOR_NEOANTIGEN_BURDEN, title="Category", description="Genomic signature discriminator category")
    config = SchemaConfig(
        model=orm.TumorNeoantigenBurden,
        exclude=["genomic_signature"],
        anonymization=AnonymizationConfig(fields=["date"], key="caseId"),
    )


class TumorNeoantigenBurdenCreateSchema(ModelCreateSchema):
    category: Literal[GenomicSignatureTypes.TUMOR_NEOANTIGEN_BURDEN] = Field(GenomicSignatureTypes.TUMOR_NEOANTIGEN_BURDEN, title="Category", description="Genomic signature discriminator category")
    config = SchemaConfig(
        model=orm.TumorNeoantigenBurden, exclude=["genomic_signature"]
    )


class AneuploidScoreSchema(ModelGetSchema):
    category: Literal[GenomicSignatureTypes.ANEUPLOID_SCORE] = Field(GenomicSignatureTypes.ANEUPLOID_SCORE, title="Category", description="Genomic signature discriminator category")
    config = SchemaConfig(
        model=orm.AneuploidScore,
        exclude=["genomic_signature"],
        anonymization=AnonymizationConfig(fields=["date"], key="caseId"),
    )


class AneuploidScoreCreateSchema(ModelCreateSchema):
    category: Literal[GenomicSignatureTypes.ANEUPLOID_SCORE] = Field(GenomicSignatureTypes.ANEUPLOID_SCORE, title="Category", description="Genomic signature discriminator category")
    config = SchemaConfig(model=orm.AneuploidScore, exclude=["genomic_signature"])
