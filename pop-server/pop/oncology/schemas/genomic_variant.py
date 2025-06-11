from pop.oncology import models as orm
from pop.oncology.models.genomic_variant import HGVSRegex
from pop.core.schemas import Range as RangeSchema
from pop.core.serialization.metaclasses import ModelGetSchema, ModelCreateSchema, SchemaConfig
from pop.core.anonymization import AnonymizationConfig
from pydantic import AliasChoices, Field
from typing import Optional, List

class GenomicVariantSchema(ModelGetSchema):
    isPathogenic: Optional[bool] = Field(
        default=None,
        title='Is Pathogenic',
        description='Whether the genomic variant is considered pathogenic in a clinical setting',
        alias='is_pathogenic',
        validation_alias=AliasChoices('isPathogenic','is_pathogenic'),        
    )
    isVUS: Optional[bool] = Field(
        default=None,
        title='Is VUS',
        description='Whether the genomic variant is considered a variant of unknown signifiance (VUS)',
        alias='is_vus',
        validation_alias=AliasChoices('isVUS','is_vus'),        
    )
    dnaHgvs: Optional[str] = Field(
        default=None,
        title='DNA HGVS',
        description='DNA HGVS expression (g-coordinate expression, HGVS version >=21.1)',
        pattern=HGVSRegex.DNA_HGVS,
        alias='dna_hgvs',
        validation_alias=AliasChoices('dnaHgvs','dna_hgvs'),        
    )
    dnaReferenceSequence: Optional[str] = Field(
        default=None,
        title='DNA HGVS RefSeq',
        description='DNA reference sequence identifier used as dna HGVS reference.',
        pattern=fr"{HGVSRegex.RNA_REFSEQ}|{HGVSRegex.GENOMIC_REFSEQ}",
        alias='dna_reference_sequence',
        validation_alias=AliasChoices('dnaReferenceSequence','dna_reference_sequence'),        
    )
    dnaChangePosition: Optional[int] = Field(
        default=None,
        title='DNA change position',
        description='DNA-level single-nucleotide position where the variant was found.',
        alias='dna_change_position',
        validation_alias=AliasChoices('dnaChangePosition','dna_change_position'),        
    )
    dnaChangePositionRange: Optional[RangeSchema] = Field(
        default=None,
        title='DNA change range',
        description='DNA-level single-nucleotide position where the variant was found.',
        alias='dna_change_position_range',
        validation_alias=AliasChoices('dnaChangePositionRange','dna_change_position_range'),        
    )
    dnaChangeType: Optional[orm.GenomicVariant.DNAChangeType] = Field(
        default=None,
        title='DNA change type',
        description='DNA variant type of variant.',
        alias='dna_change_type',
        validation_alias=AliasChoices('dnaChangeType','dna_change_type'),        
    )
    rnaHgvs: Optional[str] = Field(
        default=None,
        title='RNA HGVS',
        description='RNA HGVS expression (g-coordinate expression, HGVS version >=21.1)',
        pattern=HGVSRegex.RNA_HGVS,
        alias='dna_hgvs',
        validation_alias=AliasChoices('rnaHgvs','rna_hgvs'),        
    )
    rnaReferenceSequence: Optional[str] = Field(
        default=None,
        title='RNA HGVS RefSeq',
        description='RNA reference sequence identifier used as rna HGVS reference.',
        pattern=HGVSRegex.RNA_REFSEQ,
        alias='rna_reference_sequence',
        validation_alias=AliasChoices('rnaReferenceSequence','rna_reference_sequence'),        
    )
    rnaChangePosition: Optional[str] = Field(
        default=None,
        title='RNA change position',
        description='RNA-level nucleotide position/range where the variant was found.',
        pattern=HGVSRegex.NUCLEOTIDE_POSITION_OR_RANGE,
        alias='rna_change_position',
        validation_alias=AliasChoices('rnaChangePosition','rna_change_position'),        
    )
    rnaChangeType: Optional[orm.GenomicVariant.RNAChangeType] = Field(
        default=None,
        title='RNA change type',
        description='RNA variant type of variant.',
        alias='rna_change_type',
        validation_alias=AliasChoices('rnaChangeType','rna_change_type'),        
    )
    proteinHgvs: Optional[str] = Field(
        default=None,
        title='Protein HGVS',
        description='Protein HGVS expression (g-coordinate expression, HGVS version >=21.1)',
        pattern=HGVSRegex.PROTEIN_HGVS,
        alias='dna_hgvs',
        validation_alias=AliasChoices('proteinHgvs','protein_hgvs'),        
    )
    proteinReferenceSequence: Optional[str] = Field(
        default=None,
        title='Protein HGVS RefSeq',
        description='Protein reference sequence identifier used as protein HGVS reference.',
        pattern=HGVSRegex.PROTEIN_REFSEQ,
        alias='protein_reference_sequence',
        validation_alias=AliasChoices('proteinReferenceSequence','protein_reference_sequence'),        
    )
    proteinChangeType: Optional[orm.GenomicVariant.ProteinChangeType] = Field(
        default=None,
        title='Protein change type',
        description='Protein variant type of variant.',
        alias='protein_change_type',
        validation_alias=AliasChoices('proteinChangeType','protein_change_type'),        
    )
    nucleotidesLength: Optional[int] = Field(
        default=None,
        title='Variant length',
        description='Length of the variant in nucleotides',
        alias='nucleotides_length',
        validation_alias=AliasChoices('nucleotidesLength','nucleotides_length'),        
    )
    regions: Optional[List[str]] = Field(
        default=None,
        title='Gene regions',
        description='Gene regions (exons, introns, UTRs) affected by the variant. Estimated from MANE reference sequences.',
        alias='regions',
    )
    config = SchemaConfig(model=orm.GenomicVariant, exclude=('is_vus', 'is_pathogenic'), anonymization=AnonymizationConfig(fields=['date'], key='caseId'))


class GenomicVariantCreateSchema(ModelCreateSchema):
    dnaHgvs: Optional[str] = Field(
        default=None,
        title='DNA HGVS',
        description='DNA HGVS expression (g-coordinate expression, HGVS version >=21.1)',
        pattern=HGVSRegex.DNA_HGVS,
        alias='dna_hgvs',
        validation_alias=AliasChoices('dnaHgvs','dna_hgvs'),        
    )
    rnaHgvs: Optional[str] = Field(
        default=None,
        title='RNA HGVS',
        description='RNA HGVS expression (g-coordinate expression, HGVS version >=21.1)',
        pattern=HGVSRegex.RNA_HGVS,
        alias='dna_hgvs',
        validation_alias=AliasChoices('rnaHgvs','rna_hgvs'),        
    )
    proteinHgvs: Optional[str] = Field(
        default=None,
        title='Protein HGVS',
        description='Protein HGVS expression (g-coordinate expression, HGVS version >=21.1)',
        pattern=HGVSRegex.PROTEIN_HGVS,
        alias='dna_hgvs',
        validation_alias=AliasChoices('proteinHgvs','protein_hgvs'),        
    )
    config = SchemaConfig(model=orm.GenomicVariant, exclude=('is_vus', 'is_pathogenic'))
