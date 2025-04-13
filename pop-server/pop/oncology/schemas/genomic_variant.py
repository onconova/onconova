from pop.oncology import models as orm
from pop.oncology.models.genomic_variant import HGVSRegex
from pop.core.schemas.factory import ModelGetSchema, ModelCreateSchema, SchemaConfig
from pydantic import AliasChoices, Field
from typing import Optional

class GenomicVariantSchema(ModelGetSchema):
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
    dnaChangePosition: Optional[str] = Field(
        default=None,
        title='DNA change position',
        description='DNA-level nucleotide position/range where the variant was found.',
        pattern=HGVSRegex.NUCLEOTIDE_POSITION_OR_RANGE,
        alias='dna_change_position',
        validation_alias=AliasChoices('dnaChangePosition','dna_change_position'),        
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
    proteinChangePosition: Optional[str] = Field(
        default=None,
        title='Protein change position',
        description='Protein-level aminoacid position/range where the variant was found.',
        pattern=HGVSRegex.AMINOACID_POSITION_OR_RANGE,
        alias='protein_change_position',
        validation_alias=AliasChoices('proteinChangePosition','protein_change_position'),        
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
    config = SchemaConfig(model=orm.GenomicVariant, GenomicVariantexclude=('is_vus', 'is_pathogenic'))



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
