from typing import List
from pydantic import Field
from datetime import date as date_aliased

from onconova.core.schemas import BaseSchema, MetadataAnonymizationMixin, CodedConcept, Range
from onconova.core.types import Nullable, UUID
from onconova.oncology.models import genomic_variant as orm


class GenomicVariantCreate(BaseSchema):
    
    __orm_model__ = orm.GenomicVariant 
    
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
        description="Indicates the case of the patient who' genomic variant is described",
        title='Patient case',
    )
    date: date_aliased = Field(
        ...,
        description='Clinically-relevant date of the genomic variant (e.g. the specimen collection date).',
        title='Date',
    )
    genes: List[CodedConcept] = Field(
        ...,
        description='Gene(s) affected by this variant',
        title='Gene(s)',
        json_schema_extra={'x-terminology': 'Gene'},
    )
    dnaHgvs: Nullable[str] = Field(
        default=None,
        title="DNA HGVS",
        description="DNA HGVS expression (g-coordinate expression, HGVS version >=21.1)",
        pattern=orm.HGVSRegex.DNA_HGVS,
    )
    rnaHgvs: Nullable[str] = Field(
        default=None,
        title="RNA HGVS",
        description="RNA HGVS expression (g-coordinate expression, HGVS version >=21.1)",
        pattern=orm.HGVSRegex.RNA_HGVS,
    )
    proteinHgvs: Nullable[str] = Field(
        default=None,
        title="Protein HGVS",
        description="Protein HGVS expression (g-coordinate expression, HGVS version >=21.1)",
        pattern=orm.HGVSRegex.PROTEIN_HGVS,
    )
    assessmentDate: Nullable[date_aliased] = Field(
        None,
        description='Date at which the genomic variant was assessed and/or reported.',
        title='Assessment date',
    )
    genePanel: Nullable[str] = Field(
        None,
        description='Commercial or official name of the gene panel tested to identify the variant',
        title='Gene panel',
        max_length=200,
    )
    assessment: Nullable[orm.GenomicVariantAssessmentChoices] = Field(
        None,
        description='Classification of whether the variant is present or absent in the analysis results. Relevant for genomic studies that report presence and absence of variants.',
        title='Assessment',
    )
    confidence: Nullable[orm.GenomicVariantConfidenceChoices] = Field(
        None,
        description='Classification of the confidence for a true positive variant call based e.g. calling thresholds or phred-scaled confidence scores.',
        title='Confidence',
    )
    analysisMethod: Nullable[CodedConcept] = Field(
        None,
        description='Analysis method used to detect the variant',
        title='Analysis method',
        json_schema_extra={'x-terminology': 'StructuralVariantAnalysisMethod'},
    )
    clinicalRelevance: Nullable[orm.GenomicVariantClinicalRelevanceChoices] = Field(
        None,
        description='Classification of the clinical relevance or pathogenicity of the variant.',
        title='Clinical relevance',
    )
    genomeAssemblyVersion: Nullable[CodedConcept] = Field(
        None,
        description='The reference genome assembly versionused in this analysis.',
        title='Genome assembly version',
        json_schema_extra={'x-terminology': 'ReferenceGenomeBuild'},
    )
    molecularConsequence: Nullable[CodedConcept] = Field(
        None,
        description='The calculated or observed effect of a variant on its downstream transcript and, if applicable, ensuing protein sequence.',
        title='Molecular consequence',
        json_schema_extra={'x-terminology': 'MolecularConsequence'},
    )
    copyNumber: Nullable[int] = Field(
        None,
        description='Genomic structural variant copy number. It is a unit-less value. Note that a copy number of 1 can imply a deletion.',
        title='Copy number',
    )
    alleleFrequency: Nullable[float] = Field(
        None,
        description='The relative frequency (value in range [0,1]) of the allele at a given locus in the sample.',
        title='Allele frequency',
    )
    alleleDepth: Nullable[int] = Field(
        None,
        description='Specifies the number of reads that identified the allele in question whether it consists of one or a small sequence of contiguous nucleotides.',
        title='Allele depth (reads)',
    )
    zygosity: Nullable[CodedConcept] = Field(
        None,
        description='The observed level of occurrence of the variant in the set of chromosomes.',
        title='Zygosity',
        json_schema_extra={'x-terminology': 'Zygosity'},
    )
    inheritance: Nullable[CodedConcept] = Field(
        None,
        description='Variant inheritance origin (if known).',
        title='Inheritance',
        json_schema_extra={'x-terminology': 'VariantInheritance'},
    )
    coordinateSystem: Nullable[CodedConcept] = Field(
        None,
        description='Genomic coordinate system used for identifying nucleotides or amino acids within a sequence.',
        title='Coordinate system',
        json_schema_extra={'x-terminology': 'GenomicCoordinateSystem'},
    )
    clinvar: Nullable[str] = Field(
        None,
        description='Accession number in the ClinVar variant database, given for cross-reference.',
        title='ClinVar accession number',
    )


class GenomicVariant(GenomicVariantCreate, MetadataAnonymizationMixin):
    
    isPathogenic: Nullable[bool] = Field(
        default=None,
        title="Is Pathogenic",
        description="Whether the genomic variant is considered pathogenic in a clinical setting",
    )
    isVUS: Nullable[bool] = Field(
        default=None,
        title="Is VUS",
        description="Whether the genomic variant is considered a variant of unknown signifiance (VUS)",
    )
    dnaReferenceSequence: Nullable[str] = Field(
        default=None,
        title="DNA HGVS RefSeq",
        description="DNA reference sequence identifier used as dna HGVS reference.",
        pattern=rf"{orm.HGVSRegex.RNA_REFSEQ}|{orm.HGVSRegex.GENOMIC_REFSEQ}",
    )
    dnaChangePosition: Nullable[int] = Field(
        default=None,
        title="DNA change position",
        description="DNA-level single-nucleotide position where the variant was found.",
    )
    dnaChangePositionRange: Nullable[Range] = Field(
        default=None,
        title="DNA change range",
        description="DNA-level single-nucleotide position where the variant was found.",
    )
    dnaChangeType: Nullable[orm.DNAChangeType] = Field(
        default=None,
        title="DNA change type",
        description="DNA variant type of variant.",
    )
    rnaReferenceSequence: Nullable[str] = Field(
        default=None,
        title="RNA HGVS RefSeq",
        description="RNA reference sequence identifier used as rna HGVS reference.",
        pattern=orm.HGVSRegex.RNA_REFSEQ,
    )
    rnaChangePosition: Nullable[str] = Field(
        default=None,
        title="RNA change position",
        description="RNA-level nucleotide position/range where the variant was found.",
        pattern=orm.HGVSRegex.NUCLEOTIDE_POSITION_OR_RANGE,
    )
    rnaChangeType: Nullable[orm.RNAChangeType] = Field(
        default=None,
        title="RNA change type",
        description="RNA variant type of variant.",
    )
    proteinReferenceSequence: Nullable[str] = Field(
        default=None,
        title="Protein HGVS RefSeq",
        description="Protein reference sequence identifier used as protein HGVS reference.",
        pattern=orm.HGVSRegex.PROTEIN_REFSEQ,
    )
    proteinChangeType: Nullable[orm.ProteinChangeType] = Field(
        default=None,
        title="Protein change type",
        description="Protein variant type of variant.",
    )
    nucleotidesLength: Nullable[int] = Field(
        default=None,
        title="Variant length",
        description="Length of the variant in nucleotides",
    )
    regions: Nullable[List[str]] = Field(
        default=None,
        title="Gene regions",
        description="Gene regions (exons, introns, UTRs) affected by the variant. Estimated from MANE reference sequences.",
        alias="regions",
    )

    __anonymization_fields__ = ("date","assessmentDate",)
    __anonymization_key__ = "caseId"