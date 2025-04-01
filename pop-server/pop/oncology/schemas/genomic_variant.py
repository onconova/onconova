from pop.oncology import models as orm
from pop.oncology.models.genomic_variant import HGVSRegex
from pop.core.schemas.factory import ModelGetSchema, ModelCreateSchema, SchemaConfig
from pydantic import AliasChoices, Field

class GenomicVariantSchema(ModelGetSchema):
    genomicHgvs: str = Field(
        default=None,
        title='Genomic HGVS',
        description='Genomic HGVS expression (g-coordinate expression, HGVS version >=21.1)',
        pattern=HGVSRegex.GENOMIC_HGVS,
        alias='genomic_hgvs',
        validation_alias=AliasChoices('genomicHgvs','genomic_hgvs'),        
    )
    genomicReferenceSequence: str = Field(
        default=None,
        title='Genomic HGVS RefSeq',
        description='Genomic reference sequence identifier used as genomic HGVS reference.',
        pattern=HGVSRegex.GENOMIC_REFSEQ,
        alias='genomic_reference_sequence',
        validation_alias=AliasChoices('genomicReferenceSequence','genomic_reference_sequence'),        
    )
    genomicChangePosition: str = Field(
        default=None,
        title='Genomic change position',
        description='Genomic-level nucleotide position/range where the variant was found.',
        pattern=HGVSRegex.NUCLEOTIDE_POSITION_OR_RANGE,
        alias='genomic_change_position',
        validation_alias=AliasChoices('genomicChangePosition','genomic_change_position'),        
    )
    genomicChangeType: orm.GenomicVariant.DNAChangeType = Field(
        default=None,
        title='Genomic change type',
        description='Genomic variant type of variant.',
        alias='genomic_change_type',
        validation_alias=AliasChoices('genomicChangeType','genomic_change_type'),        
    )
    dnaHgvs: str = Field(
        default=None,
        title='DNA HGVS',
        description='DNA HGVS expression (g-coordinate expression, HGVS version >=21.1)',
        pattern=HGVSRegex.DNA_HGVS,
        alias='dna_hgvs',
        validation_alias=AliasChoices('dnaHgvs','dna_hgvs'),        
    )
    dnaReferenceSequence: str = Field(
        default=None,
        title='DNA HGVS RefSeq',
        description='DNA reference sequence identifier used as dna HGVS reference.',
        pattern=HGVSRegex.RNA_REFSEQ,
        alias='dna_reference_sequence',
        validation_alias=AliasChoices('dnaReferenceSequence','dna_reference_sequence'),        
    )
    dnaChangePosition: str = Field(
        default=None,
        title='DNA change position',
        description='DNA-level nucleotide position/range where the variant was found.',
        pattern=HGVSRegex.NUCLEOTIDE_POSITION_OR_RANGE,
        alias='dna_change_position',
        validation_alias=AliasChoices('dnaChangePosition','dna_change_position'),        
    )
    dnaChangeType: orm.GenomicVariant.DNAChangeType = Field(
        default=None,
        title='DNA change type',
        description='DNA variant type of variant.',
        alias='dna_change_type',
        validation_alias=AliasChoices('dnaChangeType','dna_change_type'),        
    )
    rnaHgvs: str = Field(
        default=None,
        title='RNA HGVS',
        description='RNA HGVS expression (g-coordinate expression, HGVS version >=21.1)',
        pattern=HGVSRegex.RNA_HGVS,
        alias='dna_hgvs',
        validation_alias=AliasChoices('rnaHgvs','rna_hgvs'),        
    )
    rnaReferenceSequence: str = Field(
        default=None,
        title='RNA HGVS RefSeq',
        description='RNA reference sequence identifier used as rna HGVS reference.',
        pattern=HGVSRegex.RNA_REFSEQ,
        alias='rna_reference_sequence',
        validation_alias=AliasChoices('rnaReferenceSequence','rna_reference_sequence'),        
    )
    rnaChangePosition: str = Field(
        default=None,
        title='RNA change position',
        description='RNA-level nucleotide position/range where the variant was found.',
        pattern=HGVSRegex.NUCLEOTIDE_POSITION_OR_RANGE,
        alias='rna_change_position',
        validation_alias=AliasChoices('rnaChangePosition','rna_change_position'),        
    )
    rnaChangeType: orm.GenomicVariant.RNAChangeType = Field(
        default=None,
        title='RNA change type',
        description='RNA variant type of variant.',
        alias='rna_change_type',
        validation_alias=AliasChoices('rnaChangeType','rna_change_type'),        
    )
    proteinHgvs: str = Field(
        default=None,
        title='Protein HGVS',
        description='Protein HGVS expression (g-coordinate expression, HGVS version >=21.1)',
        pattern=HGVSRegex.PROTEIN_HGVS,
        alias='dna_hgvs',
        validation_alias=AliasChoices('proteinHgvs','protein_hgvs'),        
    )
    proteinReferenceSequence: str = Field(
        default=None,
        title='Protein HGVS RefSeq',
        description='Protein reference sequence identifier used as protein HGVS reference.',
        pattern=HGVSRegex.PROTEIN_HGVS,
        alias='protein_reference_sequence',
        validation_alias=AliasChoices('proteinReferenceSequence','protein_reference_sequence'),        
    )
    proteinChangePosition: str = Field(
        default=None,
        title='Protein change position',
        description='Protein-level aminoacid position/range where the variant was found.',
        pattern=HGVSRegex.AMINOACID_POSITION_OR_RANGE,
        alias='protein_change_position',
        validation_alias=AliasChoices('proteinChangePosition','protein_change_position'),        
    )
    proteinChangeType: orm.GenomicVariant.ProteinChangeType = Field(
        default=None,
        title='Protein change type',
        description='Protein variant type of variant.',
        alias='protein_change_type',
        validation_alias=AliasChoices('proteinChangeType','protein_change_type'),        
    )
    nucleotidesLength: int = Field(
        default=None,
        title='Variant length',
        description='Length of the variant in nucleotides',
        alias='nucleotides_length',
        validation_alias=AliasChoices('nucleotidesLength','nucleotides_length'),        
    )
    config = SchemaConfig(model=orm.GenomicVariant, GenomicVariantexclude=('is_vus', 'is_pathogenic'))

class GenomicVariantCreateSchema(ModelCreateSchema):
    genomicHgvs: str = Field(
        default=None,
        title='Genomic HGVS',
        description='Genomic HGVS expression (g-coordinate expression, HGVS version >=21.1)',
        pattern=HGVSRegex.GENOMIC_HGVS,
        alias='genomic_hgvs',
        validation_alias=AliasChoices('genomicHgvs','genomic_hgvs'),        
    )
    dnaHgvs: str = Field(
        default=None,
        title='DNA HGVS',
        description='DNA HGVS expression (g-coordinate expression, HGVS version >=21.1)',
        pattern=HGVSRegex.DNA_HGVS,
        alias='dna_hgvs',
        validation_alias=AliasChoices('dnaHgvs','dna_hgvs'),        
    )
    rnaHgvs: str = Field(
        default=None,
        title='RNA HGVS',
        description='RNA HGVS expression (g-coordinate expression, HGVS version >=21.1)',
        pattern=HGVSRegex.RNA_HGVS,
        alias='dna_hgvs',
        validation_alias=AliasChoices('rnaHgvs','rna_hgvs'),        
    )
    proteinHgvs: str = Field(
        default=None,
        title='Protein HGVS',
        description='Protein HGVS expression (g-coordinate expression, HGVS version >=21.1)',
        pattern=HGVSRegex.PROTEIN_HGVS,
        alias='dna_hgvs',
        validation_alias=AliasChoices('proteinHgvs','protein_hgvs'),        
    )
    config = SchemaConfig(model=orm.GenomicVariant, exclude=('is_vus', 'is_pathogenic'))
