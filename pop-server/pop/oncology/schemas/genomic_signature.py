from ninja import Schema
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
    category: GenomicSignatureTypes
    config = SchemaConfig(
        model=orm.GenomicSignature,
        anonymization=AnonymizationConfig(fields=["date"], key="caseId"),
    )


class TumorMutationalBurdenSchema(ModelGetSchema):
    category: Literal[GenomicSignatureTypes.TUMOR_MUTATIONAL_BURDEN] = GenomicSignatureTypes.TUMOR_MUTATIONAL_BURDEN  # type: ignore
    config = SchemaConfig(
        model=orm.TumorMutationalBurden,
        exclude=["genomic_signature"],
        anonymization=AnonymizationConfig(fields=["date"], key="caseId"),
    )


class TumorMutationalBurdenCreateSchema(ModelCreateSchema):
    category: Literal[GenomicSignatureTypes.TUMOR_MUTATIONAL_BURDEN] = GenomicSignatureTypes.TUMOR_MUTATIONAL_BURDEN  # type: ignore
    config = SchemaConfig(
        model=orm.TumorMutationalBurden, exclude=["genomic_signature"]
    )


class MicrosatelliteInstabilitySchema(ModelGetSchema):
    category: Literal[GenomicSignatureTypes.MICROSATELLITE_INSTABILITY] = GenomicSignatureTypes.MICROSATELLITE_INSTABILITY  # type: ignore
    config = SchemaConfig(
        model=orm.MicrosatelliteInstability,
        exclude=["genomic_signature"],
        anonymization=AnonymizationConfig(fields=["date"], key="caseId"),
    )


class MicrosatelliteInstabilityCreateSchema(ModelCreateSchema):
    category: Literal[GenomicSignatureTypes.MICROSATELLITE_INSTABILITY] = GenomicSignatureTypes.MICROSATELLITE_INSTABILITY  # type: ignore
    config = SchemaConfig(
        model=orm.MicrosatelliteInstability, exclude=["genomic_signature"]
    )


class LossOfHeterozygositySchema(ModelGetSchema):
    category: Literal[GenomicSignatureTypes.LOSS_OF_HETEROZYGOSITY] = GenomicSignatureTypes.LOSS_OF_HETEROZYGOSITY  # type: ignore
    config = SchemaConfig(
        model=orm.LossOfHeterozygosity,
        exclude=["genomic_signature"],
        anonymization=AnonymizationConfig(fields=["date"], key="caseId"),
    )


class LossOfHeterozygosityCreateSchema(ModelCreateSchema):
    category: Literal[GenomicSignatureTypes.LOSS_OF_HETEROZYGOSITY] = GenomicSignatureTypes.LOSS_OF_HETEROZYGOSITY  # type: ignore
    config = SchemaConfig(model=orm.LossOfHeterozygosity, exclude=["genomic_signature"])


class HomologousRecombinationDeficiencySchema(ModelGetSchema):
    category: Literal[GenomicSignatureTypes.HOMOLOGOUS_RECOMBINATION_DEFICIENCY] = GenomicSignatureTypes.HOMOLOGOUS_RECOMBINATION_DEFICIENCY  # type: ignore
    config = SchemaConfig(
        model=orm.HomologousRecombinationDeficiency,
        exclude=["genomic_signature"],
        anonymization=AnonymizationConfig(fields=["date"], key="caseId"),
    )


class HomologousRecombinationDeficiencyCreateSchema(ModelCreateSchema):
    category: Literal[GenomicSignatureTypes.HOMOLOGOUS_RECOMBINATION_DEFICIENCY] = GenomicSignatureTypes.HOMOLOGOUS_RECOMBINATION_DEFICIENCY  # type: ignore
    config = SchemaConfig(
        model=orm.HomologousRecombinationDeficiency, exclude=["genomic_signature"]
    )


class TumorNeoantigenBurdenSchema(ModelGetSchema):
    category: Literal[GenomicSignatureTypes.TUMOR_NEOANTIGEN_BURDEN] = GenomicSignatureTypes.TUMOR_NEOANTIGEN_BURDEN  # type: ignore
    config = SchemaConfig(
        model=orm.TumorNeoantigenBurden,
        exclude=["genomic_signature"],
        anonymization=AnonymizationConfig(fields=["date"], key="caseId"),
    )


class TumorNeoantigenBurdenCreateSchema(ModelCreateSchema):
    category: Literal[GenomicSignatureTypes.TUMOR_NEOANTIGEN_BURDEN] = GenomicSignatureTypes.TUMOR_NEOANTIGEN_BURDEN  # type: ignore
    config = SchemaConfig(
        model=orm.TumorNeoantigenBurden, exclude=["genomic_signature"]
    )


class AneuploidScoreSchema(ModelGetSchema):
    category: Literal[GenomicSignatureTypes.ANEUPLOID_SCORE] = GenomicSignatureTypes.ANEUPLOID_SCORE  # type: ignore
    config = SchemaConfig(
        model=orm.AneuploidScore,
        exclude=["genomic_signature"],
        anonymization=AnonymizationConfig(fields=["date"], key="caseId"),
    )


class AneuploidScoreCreateSchema(ModelCreateSchema):
    category: Literal[GenomicSignatureTypes.ANEUPLOID_SCORE] = GenomicSignatureTypes.ANEUPLOID_SCORE  # type: ignore
    config = SchemaConfig(model=orm.AneuploidScore, exclude=["genomic_signature"])
