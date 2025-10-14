from typing import Union

import pghistory
from django.contrib.postgres.aggregates import ArrayAgg, StringAgg
from django.contrib.postgres.fields import IntegerRangeField
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Case, CheckConstraint, F, Func, Q, Value, When
from django.db.models.fields.json import KeyTextTransform
from django.db.models.functions import Cast, Coalesce, Concat
from django.utils.translation import gettext_lazy as _
from queryable_properties.managers import QueryablePropertiesManager
from queryable_properties.properties import AnnotationProperty

import onconova.terminology.fields as termfields
import onconova.terminology.models as terminologies
from onconova.core.models import BaseModel
from onconova.oncology.models import PatientCase


class HGVSRegex:
    """
    A collection of regular expressions for parsing and validating HGVS (Human Genome Variation Society) nomenclature strings.

    References:
        - HGVS v21.1.2 specification
        - NCBI RefSeq accession formats

    Attributes:
        AMINOACID (str): Regex for valid amino acid codes.
        REPETITION_COPIES (str): Regex for repetition copy notation.
        VERSIONED_NUMBER (str): Regex for versioned numbers.
        GENOMIC_REFSEQ (str): Regex for genomic reference sequence identifiers.
        RNA_REFSEQ (str): Regex for RNA reference sequence identifiers.
        PROTEIN_REFSEQ (str): Regex for protein reference sequence identifiers.
        NUCLEOTIDE_POSITION_OR_RANGE (str): Regex for nucleotide positions and ranges.
        AMINOACID_POSITION_OR_RANGE (str): Regex for amino acid positions and ranges.
        DNA_CHANGE_DESCRIPTION (str): Regex for DNA change descriptions.
        RNA_CHANGE_DESCRIPTION (str): Regex for RNA change descriptions.
        PROTEIN_CHANGE_DESCRIPTION (str): Regex for protein change descriptions.
        DNA_HGVS (str): Complete regex for HGVS strings for DNA.
        RNA_HGVS (str): Complete regex for HGVS strings for RNA.
        PROTEIN_HGVS (str): Complete regex for HGVS strings for protein.

    Usage:
        Use these regex patterns to match, validate, or extract components from HGVS variant strings in genomic data processing pipelines.
    """

    AMINOACID = r"(?:Ter|(?:Gly|Ala|Val|Leu|Ile|Met|Phe|Trp|Pro|Ser|Thr|Cys|Tyr|Asn|Gln|Asp|Glu|Lys|Arg|His))"
    REPETITION_COPIES = r"\[(?:\d+|(?:\(\d+_\d+\)))\]"

    # Reference sequence identifiers
    VERSIONED_NUMBER = r"\d+(?:\.\d{1,3})?"

    # NCBI RefSeq Prefixes
    # (https://www.ncbi.nlm.nih.gov/books/NBK21091/table/ch18.T.refseq_accession_numbers_and_mole/?report=objectonly)
    GENOMIC_REFSEQ_PREFIX = r"(?:NC_|AC_|NG_|NT_|NW_|NZ_|GCF_)"
    GENOMIC_NCIB_REFSEQ = rf"{GENOMIC_REFSEQ_PREFIX}{VERSIONED_NUMBER}"
    RNA_REFSEQ_PREFIX = r"(?:NM_|NR_|XM_|XR_)"
    RNA_NCIB_REFSEQ = rf"{RNA_REFSEQ_PREFIX}{VERSIONED_NUMBER}"
    PROTEIN_REFSEQ_PREFIX = r"(?:AP_|NP_|YP_|XP_|WP_)"
    PROTEIN_NCIB_REFSEQ = rf"{PROTEIN_REFSEQ_PREFIX}{VERSIONED_NUMBER}"

    # ENSEMBL RefSeq
    GENOMIC_ENSEMBL_REFSEQ = rf"ENSG{VERSIONED_NUMBER}"
    RNA_ENSEMBL_REFSEQ = rf"ENST{VERSIONED_NUMBER}"
    PROTEIN_ENSEMBL_REFSEQ = rf"ENSP{VERSIONED_NUMBER}"

    # LRG RefSeq
    GENOMIC_LRG_REFSEQ = r"LRG_\d+"
    RNA_LRG_REFSEQ = r"LRG_\d+t\d{1,3}"
    PROTEIN_LRG_REFSEQ = r"LRG_\d+p\d{1,3}"

    GENOMIC_REFSEQ = rf"(?:{GENOMIC_NCIB_REFSEQ})|(?:{GENOMIC_ENSEMBL_REFSEQ})|(?:{GENOMIC_LRG_REFSEQ})"
    RNA_REFSEQ = rf"(?:{RNA_NCIB_REFSEQ})|(?:{RNA_ENSEMBL_REFSEQ})|(?:{RNA_LRG_REFSEQ})"
    PROTEIN_REFSEQ = rf"(?:{PROTEIN_NCIB_REFSEQ})|(?:{PROTEIN_ENSEMBL_REFSEQ})|(?:{PROTEIN_LRG_REFSEQ})"

    # Genomic coordinates
    CODING_POSITION = r"(?:\?|\*|\d+)"
    UTR3_POSITION = r"(?:\*\d+(?:[\+-]\d+)?)"
    UTR5_POSITION = r"(?:-\d+(?:[\+-]\d+)?)"
    INTRONIC_POSITION = r"(?:(?:(?:\+|-)\d+)|(?:(?:\?|\*|\d+)(?:\+|-)\d+))"
    NONCODING_POSITION = rf"(?:{UTR3_POSITION}|{UTR5_POSITION}|{INTRONIC_POSITION})"
    POSITION = rf"(?:{NONCODING_POSITION}|{CODING_POSITION})"
    NUCLEOTIDE_UNCERTAIN_POSITION = rf"\({POSITION}_{POSITION}\)"
    NUCLEOTIDE_POSITION = rf"(?:{POSITION}|{NUCLEOTIDE_UNCERTAIN_POSITION})"
    NUCLEOTIDE_RANGE = rf"(?:{NUCLEOTIDE_POSITION}_{NUCLEOTIDE_POSITION})"
    NUCLEOTIDE_POSITION_OR_RANGE = rf"(?:{NUCLEOTIDE_RANGE}|{NUCLEOTIDE_POSITION})"
    AMINOACID_UNCERTAIN_POSITION = rf"(?:(?:\(\?_{AMINOACID}\d+\))|(?:\({AMINOACID}\d+_\?\))|(?:\({AMINOACID}\d+_{AMINOACID}\d+\)))"
    AMINOACID_POSITION = rf"(?:{AMINOACID}\d+|{AMINOACID_UNCERTAIN_POSITION})"
    AMINOACID_RANGE = rf"(?:{AMINOACID_POSITION}_{AMINOACID_POSITION})"
    AMINOACID_POSITION_OR_RANGE = rf"(?:{AMINOACID_RANGE}|{AMINOACID_POSITION})"

    # Types of variants
    DNA_VARIANT_TYPE = r">|delins|ins|del|dup|inv|="
    RNA_VARIANT_TYPE = r">|delins|ins|del|dup|inv"
    PROTEIN_VARIANT_TYPE = r"(?:delins|ins|del|dup|fsTer|fs|extTer|ext|Ter|\*|)|(?:)"

    # Genomic sequences
    DNA_SEQUENCE = r"(?:A|C|G|T|B|D|H|K|M|N|R|S|V|W|Y|X|-)+"
    RNA_SEQUENCE = r"(?:a|c|g|t|b|d|h|k|m|n|r|s|v|w|y)+"
    PROTEIN_SEQUENCE = rf"(?:{AMINOACID}+)"

    # DNA HGVS scenarios
    DNA_UNCHANGED = rf"{NUCLEOTIDE_POSITION_OR_RANGE}="
    DNA_SUBSTITUTION = rf"{NUCLEOTIDE_POSITION}{DNA_SEQUENCE}>{DNA_SEQUENCE}"
    DNA_DELETION_INSERTION = rf"{NUCLEOTIDE_POSITION_OR_RANGE}delins{DNA_SEQUENCE}"
    DNA_INSERTION = rf"{NUCLEOTIDE_RANGE}ins(?:{DNA_SEQUENCE}|{NUCLEOTIDE_RANGE})"
    DNA_DELETION = rf"{NUCLEOTIDE_POSITION_OR_RANGE}del"
    DNA_DUPLICATION = rf"{NUCLEOTIDE_POSITION_OR_RANGE}dup"
    DNA_INVERSION = rf"{NUCLEOTIDE_POSITION_OR_RANGE}inv"
    DNA_REPETITION = (
        rf"{NUCLEOTIDE_POSITION_OR_RANGE}(?:{DNA_SEQUENCE})?{REPETITION_COPIES}"
    )
    DNA_METHYLATION_GAIN = rf"{NUCLEOTIDE_POSITION_OR_RANGE}\|gom"
    DNA_METHYLATION_LOSS = rf"{NUCLEOTIDE_POSITION_OR_RANGE}\|lom"
    DNA_METHYLATION_EQUAL = rf"{NUCLEOTIDE_POSITION_OR_RANGE}\|met="
    DNA_TRANSLOCATION = rf"{NUCLEOTIDE_POSITION_OR_RANGE}delins\[(?:(?:{GENOMIC_REFSEQ}):)?g\.{NUCLEOTIDE_POSITION_OR_RANGE}\]"
    DNA_TRANSPOSITION = rf"{NUCLEOTIDE_POSITION_OR_RANGE}ins\[(?:(?:{GENOMIC_REFSEQ}):)?g\.{NUCLEOTIDE_POSITION_OR_RANGE}\]\sand\s(?:(?:{GENOMIC_REFSEQ}):)?g\.{NUCLEOTIDE_POSITION_OR_RANGE}del"
    DNA_CHANGE_DESCRIPTION = rf"{DNA_UNCHANGED}|{DNA_SUBSTITUTION}|{DNA_TRANSLOCATION}|{DNA_TRANSPOSITION}|{DNA_DELETION_INSERTION}|{DNA_INSERTION}|{DNA_DELETION}|{DNA_DUPLICATION}|{DNA_INVERSION}|{DNA_REPETITION}|{DNA_METHYLATION_GAIN}|{DNA_METHYLATION_LOSS}|{DNA_METHYLATION_EQUAL}"

    # RNA HGVS scenarios
    RNA_UNCHANGED = rf"{NUCLEOTIDE_POSITION_OR_RANGE}="
    RNA_SUBSTITUTION = rf"{NUCLEOTIDE_POSITION}{RNA_SEQUENCE}>{RNA_SEQUENCE}"
    RNA_DELETION_INSERTION = rf"{NUCLEOTIDE_POSITION_OR_RANGE}delins{RNA_SEQUENCE}"
    RNA_INSERTION = rf"{NUCLEOTIDE_RANGE}ins(?:{RNA_SEQUENCE}|{NUCLEOTIDE_RANGE})"
    RNA_DELETION = rf"{NUCLEOTIDE_POSITION_OR_RANGE}del"
    RNA_DUPLICATION = rf"{NUCLEOTIDE_POSITION_OR_RANGE}dup"
    RNA_INVERSION = rf"{NUCLEOTIDE_POSITION_OR_RANGE}inv"
    RNA_REPETITION = (
        rf"{NUCLEOTIDE_POSITION_OR_RANGE}(?:{RNA_SEQUENCE})?{REPETITION_COPIES}"
    )
    RNA_METHYLATION_GAIN = rf"{NUCLEOTIDE_POSITION_OR_RANGE}\|gom"
    RNA_METHYLATION_LOSS = rf"{NUCLEOTIDE_POSITION_OR_RANGE}\|lom"
    RNA_METHYLATION_EQUAL = rf"{NUCLEOTIDE_POSITION_OR_RANGE}\|met="
    RNA_CHANGE_DESCRIPTION = rf"{RNA_UNCHANGED}|{RNA_SUBSTITUTION}|{RNA_DELETION_INSERTION}|{RNA_INSERTION}|{RNA_DELETION}|{RNA_DUPLICATION}|{RNA_INVERSION}|{RNA_REPETITION}"

    # Protein HGVS scenarios
    PROTEIN_UNKNOWN = r"\?"
    PROTEIN_NOTHING = r"0\??"
    PROTEIN_SILENT = rf"{AMINOACID_POSITION}="
    PROTEIN_MISSENSE = rf"{AMINOACID_POSITION}{PROTEIN_SEQUENCE}"
    PROTEIN_DELETION_INSERTION = (
        rf"{AMINOACID_POSITION_OR_RANGE}delins{PROTEIN_SEQUENCE}"
    )
    PROTEIN_INSERTION = rf"{AMINOACID_RANGE}ins{PROTEIN_SEQUENCE}"
    PROTEIN_DELETION = rf"{AMINOACID_POSITION_OR_RANGE}del"
    PROTEIN_DUPLICATION = rf"{AMINOACID_POSITION_OR_RANGE}dup"
    PROTEIN_NONSENSE = rf"{AMINOACID_POSITION_OR_RANGE}(?:Ter|\*)"
    PROTEIN_REPETITION = rf"\(?{AMINOACID_POSITION_OR_RANGE}\)?{REPETITION_COPIES}"
    PROTEIN_FRAMESHIFT = (
        rf"{AMINOACID_POSITION_OR_RANGE}{PROTEIN_SEQUENCE}?fs(?:Ter)?(?:{POSITION})*"
    )
    PROTEIN_EXTENSION = rf"(?:(?:Met1ext-\d+)|(?:Ter\d+{PROTEIN_SEQUENCE}extTer\d+))"
    PROTEIN_CHANGE_DESCRIPTION = rf"{PROTEIN_NOTHING}|{PROTEIN_UNKNOWN}|{PROTEIN_DELETION_INSERTION}|{PROTEIN_DELETION}|{PROTEIN_INSERTION}|{PROTEIN_DUPLICATION}|{PROTEIN_NONSENSE}|{PROTEIN_FRAMESHIFT}|{PROTEIN_EXTENSION}|{PROTEIN_REPETITION}|{PROTEIN_MISSENSE}|{PROTEIN_SILENT}"

    # Complete HGVS regexes for each scenario
    DNA_HGVS = rf"(?:(?:(?:(?:{GENOMIC_REFSEQ}):)?g)|(?:(?:(?:{GENOMIC_REFSEQ})?\(?({RNA_REFSEQ})\)?:)?c))\.({DNA_CHANGE_DESCRIPTION})"
    RNA_HGVS = rf"(?:({RNA_REFSEQ}):)?r\.\(?({RNA_CHANGE_DESCRIPTION})\)?"
    PROTEIN_HGVS = rf"(?:({PROTEIN_REFSEQ}):)?p\.\(?({PROTEIN_CHANGE_DESCRIPTION})\)?"


class RegexpMatchSubstring(Func):
    """
    A custom Django Func expression to extract a substring from a field using a regular expression.

    This class wraps the PostgreSQL `substring` function, allowing you to specify a regular expression
    to match and extract a substring from a given expression (typically a model field).

    Args:
        expression (Any): The database field or expression to apply the regular expression to.
        regex (str): The regular expression pattern to use for matching the substring.
        extra (dict): Additional keyword arguments passed to the parent Func class.

    Example:
        RegexpMatchSubstring('field_name', r'[A-Za-z]+')
    """

    function = "substring"

    def __init__(self, expression, regex: str, **extra):
        # PostgreSQL regexp_match() returns an array, so we extract the nth element
        template = "(%(function)s(%(expressions)s, '%(regex)s'))"
        super().__init__(expression, regex=regex, template=template, **extra)


class GenomicVariantAssessmentChoices(models.TextChoices):
    """
    An enumeration representing possible assessments for a genomic variant.

    Attributes:
        PRESENT: Indicates the variant is present.
        ABSENT: Indicates the variant is absent.
        NOCALL: Indicates the variant call could not be made.
        INDETERMINATE: Indicates the assessment is inconclusive.
    """
    PRESENT = "present"
    ABSENT = "absent"
    NOCALL = "no-call"
    INDETERMINATE = "indeterminate"

class GenomicVariantConfidenceChoices(models.TextChoices):
    """
    An enumeration representing the confidence level assigned to a genomic variant.

    Attributes:
        LOW: Indicates low confidence in the variant call.
        HIGH: Indicates high confidence in the variant call.
        INDETERMINATE: Indicates that the confidence level could not be determined.
    """
    LOW = "low"
    HIGH = "high"
    INDETERMINATE = "indeterminate"

class GenomicVariantClinicalRelevanceChoices(models.TextChoices):
    """
    An enumeration of clinical relevance categories for genomic variants.

    Attributes:
        PATHOGENIC: Indicates the variant is pathogenic.
        LIKELY_PATHOGENIC: Indicates the variant is likely pathogenic.
        UNCERTAIN_SIGNIFICANCE: Indicates the variant has uncertain clinical significance.
        AMBIGUOUS: Indicates the variant's relevance is ambiguous.
        LIKELY_BENIGN: Indicates the variant is likely benign.
        BENIGN: Indicates the variant is benign.
    """
    PATHOGENIC = "pathogenic"
    LIKELY_PATHOGENIC = "likely_pathogenic"
    UNCERTAIN_SIGNIFICANCE = "uncertain_significance"
    AMBIGUOUS = "ambiguous"
    LIKELY_BENIGN = "likely_benign"
    BENIGN = "benign"

class DNAChangeType(models.TextChoices):
    """
    An enumeration of possible DNA change types for genomic variants.

    Attributes:
        SUBSTITUTION: A single nucleotide is replaced by another.
        DELETION_INSERTION: A combination of deletion and insertion at the same location.
        INSERTION: Addition of one or more nucleotides into the DNA sequence.
        DELETION: Removal of one or more nucleotides from the DNA sequence.
        DUPLICATION: A segment of DNA is duplicated.
        INVERSION: A segment of DNA is reversed end to end.
        UNCHANGED: No change detected in the DNA sequence.
        REPETITION: A sequence motif is repeated multiple times.
        TRANSLOCATION: A segment of DNA is moved to a different location.
        TRANSPOSITION: Movement of a DNA segment to a new position within the genome.
        METHYLATION_GAIN: Gain of methylation at a specific DNA region.
        METHYLATION_LOSS: Loss of methylation at a specific DNA region.
        METHYLATION_UNCHANGED: No change in methylation status.
    """
    SUBSTITUTION = "substitution"
    DELETION_INSERTION = "deletion-insertion"
    INSERTION = "insertion"
    DELETION = "deletion"
    DUPLICATION = "duplication"
    INVERSION = "inversion"
    UNCHANGED = "unchanged"
    REPETITION = "repetition"
    TRANSLOCATION = "translocation"
    TRANSPOSITION = "transposition"
    METHYLATION_GAIN = "methylation-gain"
    METHYLATION_LOSS = "methylation-loss"
    METHYLATION_UNCHANGED = "methylation-unchanged"

class RNAChangeType(models.TextChoices):
    """
    An enumeration of possible RNA change types for genomic variants.

    Attributes:
        SUBSTITUTION: Represents a substitution mutation in RNA.
        DELETION_INSERTION: Represents a combined deletion and insertion mutation.
        INSERTION: Represents an insertion mutation in RNA.
        DELETION: Represents a deletion mutation in RNA.
        DUPLICATION: Represents a duplication mutation in RNA.
        INVERSION: Represents an inversion mutation in RNA.
        UNCHANGED: Indicates no change in the RNA sequence.
        REPETITION: Represents a repetition mutation in RNA.
    """
    SUBSTITUTION = "substitution"
    DELETION_INSERTION = "deletion-insertion"
    INSERTION = "insertion"
    DELETION = "deletion"
    DUPLICATION = "duplication"
    INVERSION = "inversion"
    UNCHANGED = "unchanged"
    REPETITION = "repetition"

class ProteinChangeType(models.TextChoices):
    """
    An enumeration of protein change types observed in genomic variants.

    Attributes:
        MISSENSE: A single nucleotide change resulting in a different amino acid.
        NONSENSE: A mutation introducing a premature stop codon.
        DELETION_INSERTION: A complex event involving both deletion and insertion of nucleotides.
        INSERTION: Addition of one or more nucleotides into the DNA sequence.
        DELETION: Removal of one or more nucleotides from the DNA sequence.
        DUPLICATION: Duplication of a segment of DNA.
        FRAMESHIFT: A mutation that shifts the reading frame of the genetic code.
        EXTENSION: Extension of the protein sequence beyond its normal length.
        SILENT: A mutation that does not alter the amino acid sequence.
        NO_PROTEIN: No protein product is produced due to the mutation.
        UNKNOWN: The effect of the mutation on the protein is unknown.
        REPETITION: Repetition of a segment within the protein sequence.
    """
    MISSENSE = "missense"
    NONSENSE = "nonsense"
    DELETION_INSERTION = "deletion-insertion"
    INSERTION = "insertion"
    DELETION = "deletion"
    DUPLICATION = "duplication"
    FRAMESHIFT = "frameshift"
    EXTENSION = "extension"
    SILENT = "silent"
    NO_PROTEIN = "no-protein"
    UNKNOWN = "unknown"
    REPETITION = "repetition"

@pghistory.track()
class GenomicVariant(BaseModel):
    """
    Represents a clinically relevant genomic variant detected in a patient's case.

    This model captures detailed information about a genomic variant, including its assessment, confidence, clinical relevance, molecular consequence, and sequence-level changes at the DNA, RNA, and protein levels. It supports annotation and querying of variant properties, such as affected genes, cytogenetic location, chromosomes, and variant type, using HGVS expressions and coded concepts.

    Attributes:
        case (models.ForeignKey[PatientCase]): Reference to the patient case associated with the variant.
        date (models.DateField): Date relevant to the variant (e.g., specimen collection).
        assessment_date (models.DateField): Date the variant was assessed or reported.
        gene_panel (models.CharField): Name of the gene panel used for testing.
        assessment (models.CharField): Classification of variant presence/absence.
        confidence (models.CharField): Confidence level of the variant call.
        analysis_method (termfields.CodedConceptField[terminologies.GenomicVariantAnalysisMethod]): Method used to detect the variant.
        clinical_relevance (models.CharField): Pathogenicity or clinical relevance classification.
        is_vus (models.GeneratedField): Indicates if the variant is of unknown significance.
        is_pathogenic (models.GeneratedField): Indicates if the variant is pathogenic.
        genes (termfields.CodedConceptField[terminologies.Gene]): Genes affected by the variant.
        cytogenetic_location (models.AnnotationProperty): Cytogenetic location(s) of affected genes.
        chromosomes (models.AnnotationProperty): Chromosomes involved in the variant.
        genome_assembly_version (termfields.CodedConceptField[terminologies.GenomeAssemblyVersion]): Reference genome assembly version.
        dna_hgvs (models.CharField): HGVS DNA-level expression.
        dna_reference_sequence (AnnotationProperty): DNA reference sequence from HGVS.
        dna_change_position_range_start (AnnotationProperty): Start position of DNA change range.
        dna_change_position_range_end (AnnotationProperty): End position of DNA change range.
        dna_change_position_range (AnnotationProperty): Range of DNA change positions.
        dna_change_position (AnnotationProperty): Single DNA change position.
        dna_change_position_intron (AnnotationProperty): Intron position of DNA change.
        regions (AnnotationProperty): Genomic regions affected (exon, intron, UTR).
        dna_change_type (AnnotationProperty): Type of DNA change (e.g., substitution, deletion).
        rna_hgvs (models.CharField): HGVS RNA-level expression.
        rna_reference_sequence (AnnotationProperty): RNA reference sequence from HGVS.
        rna_change_position (AnnotationProperty): RNA change position or range.
        rna_change_type (AnnotationProperty): Type of RNA change.
        protein_hgvs (models.CharField): HGVS protein-level expression.
        protein_reference_sequence (AnnotationProperty): Protein reference sequence from HGVS.
        protein_change_type (AnnotationProperty): Type of protein change.
        nucleotides_length (AnnotationProperty): Total affected nucleotides.
        molecular_consequence (termfields.CodedConceptField[terminologies.MolecularConsequence]): Effect of the variant on transcript/protein.
        copy_number (models.PositiveSmallIntegerField): Structural variant copy number.
        allele_frequency (models.FloatField): Relative frequency of the allele in the sample.
        allele_depth (models.PositiveIntegerField): Number of reads supporting the allele.
        zygosity (termfields.CodedConceptField[terminologies.Zygosity]): Zygosity of the variant.
        inheritance (termfields.CodedConceptField[terminologies.Inheritance]): Inheritance origin of the variant.
        coordinate_system (termfields.CodedConceptField[terminologies.GenomicCoordinateSystem]): Genomic coordinate system used.
        clinvar (models.CharField): ClinVar accession number for cross-reference.

    Constraints:
        Constraints ensure valid HGVS expressions for DNA, RNA, and protein change fields.

    """

    objects = QueryablePropertiesManager()

    case = models.ForeignKey(
        verbose_name=_("Patient case"),
        help_text=_(
            "Indicates the case of the patient who' genomic variant is described"
        ),
        to=PatientCase,
        related_name="genomic_variants",
        on_delete=models.CASCADE,
    )
    date = models.DateField(
        verbose_name=_("Date"),
        help_text=_(
            "Clinically-relevant date of the genomic variant (e.g. the specimen collection date)."
        ),
    )
    assessment_date = models.DateField(
        verbose_name=_("Assessment date"),
        help_text=_("Date at which the genomic variant was assessed and/or reported."),
        null=True,
        blank=True,
    )
    gene_panel = models.CharField(
        verbose_name=_("Gene panel"),
        help_text=_(
            "Commercial or official name of the gene panel tested to identify the variant"
        ),
        max_length=200,
        null=True,
        blank=True,
    )
    assessment = models.CharField(
        verbose_name=_("Assessment"),
        help_text=_(
            "Classification of whether the variant is present or absent in the analysis results. Relevant for genomic studies that report presence and absence of variants."
        ),
        max_length=15,
        choices=GenomicVariantAssessmentChoices,
        null=True,
        blank=True,
    )
    confidence = models.CharField(
        verbose_name=_("Confidence"),
        help_text=_(
            "Classification of the confidence for a true positive variant call based e.g. calling thresholds or phred-scaled confidence scores."
        ),
        max_length=15,
        choices=GenomicVariantConfidenceChoices,
        null=True,
        blank=True,
    )
    analysis_method = termfields.CodedConceptField(
        verbose_name=_("Analysis method"),
        help_text=_("Analysis method used to detect the variant"),
        terminology=terminologies.StructuralVariantAnalysisMethod,
        null=True,
        blank=True,
    )
    clinical_relevance = models.CharField(
        verbose_name=_("Clinical relevance"),
        help_text=_(
            "Classification of the clinical relevance or pathogenicity of the variant."
        ),
        choices=GenomicVariantClinicalRelevanceChoices,
        null=True,
        blank=True,
    )
    is_vus = models.GeneratedField(  # type: ignore
        verbose_name=_("Is pathogenic"),
        help_text=_(
            "Indicates if the variant is of unknown signfiance (determined automatically based on the clinical relevance classification)"
        ),
        expression=models.Case(
            models.When(
                models.Q(clinical_relevance__isnull=True), then=models.Value(None)
            ),
            models.When(
                models.Q(
                    clinical_relevance=GenomicVariantClinicalRelevanceChoices.UNCERTAIN_SIGNIFICANCE
                ),
                then=models.Value(True),
            ),
            default=models.Value(False),
            output_field=models.BooleanField(),
        ),
        output_field=models.BooleanField(),
        db_persist=True,
        null=True,
    )
    is_pathogenic = models.GeneratedField(  # type: ignore
        verbose_name=_("Is pathogenic"),
        help_text=_(
            "Indicates if the variant is pathogenic (determined automatically based on the clinical relevance classification)"
        ),
        expression=models.Case(
            models.When(
                models.Q(clinical_relevance__isnull=True), then=models.Value(None)
            ),
            models.When(
                models.Q(
                    clinical_relevance=GenomicVariantClinicalRelevanceChoices.LIKELY_PATHOGENIC
                )
                | models.Q(
                    clinical_relevance=GenomicVariantClinicalRelevanceChoices.PATHOGENIC
                ),
                then=models.Value(True),
            ),
            default=models.Value(False),
            output_field=models.BooleanField(),
        ),
        output_field=models.BooleanField(),
        db_persist=True,
    )
    genes = termfields.CodedConceptField(
        verbose_name=_("Gene(s)"),
        help_text=_("Gene(s) affected by this variant"),
        terminology=terminologies.Gene,
        multiple=True,
    )
    cytogenetic_location = AnnotationProperty(
        verbose_name=_("Cytogenetic location"),
        annotation=StringAgg(
            Cast(
                KeyTextTransform("location", "genes__properties"),
                output_field=models.CharField(),
            ),
            delimiter="::",
            distinct=True,
        ),
    )
    chromosomes = AnnotationProperty(
        verbose_name=_("Chromosomes"),
        annotation=Func(
            F("cytogenetic_location"),
            function="REGEXP_MATCHES",
            template="ARRAY(SELECT unnest(REGEXP_MATCHES(unnest(REGEXP_SPLIT_TO_ARRAY(%(expressions)s, '::')), '^([0-9XY]+)')))::TEXT[]",
            output_field=models.CharField(
                choices=[(chr, chr) for chr in ["X", "Y", *list(range(1, 23))]]
            ),
        ),
    )
    genome_assembly_version = termfields.CodedConceptField(
        verbose_name=_("Genome assembly version"),
        help_text=_("The reference genome assembly versionused in this analysis."),
        terminology=terminologies.ReferenceGenomeBuild,
        null=True,
        blank=True,
    )
    dna_hgvs = models.CharField(
        verbose_name=_("HGVS DNA-level expression"),
        help_text=_(
            "Description of the coding (cDNA) sequence change using a valid HGVS-formatted expression, e.g. NM_005228.5:c.2369C>T"
        ),
        max_length=500,
        null=True,
        blank=True,
    )
    dna_reference_sequence = AnnotationProperty(
        verbose_name=_("DNA HGVS RefSeq"),
        annotation=Coalesce(
            RegexpMatchSubstring(F("dna_hgvs"), rf"({HGVSRegex.RNA_REFSEQ})"),
            RegexpMatchSubstring(F("dna_hgvs"), rf"({HGVSRegex.GENOMIC_REFSEQ})"),
        ),
    )
    dna_change_position_range_start = AnnotationProperty(
        annotation=Case(
            When(
                Q(dna_hgvs__regex=rf".*:[cg]\.{HGVSRegex.NUCLEOTIDE_RANGE}.*"),
                then=Cast(
                    RegexpMatchSubstring(
                        F("dna_hgvs"),
                        rf":[cg]\.\D*(\d+)?(?:_\d+)?\D*_{HGVSRegex.NUCLEOTIDE_POSITION}",
                    ),
                    output_field=models.IntegerField(),
                ),
            ),
            default=None,
        ),
    )
    dna_change_position_range_end = AnnotationProperty(
        annotation=Case(
            When(
                Q(dna_hgvs__regex=rf".*:[cg]\.{HGVSRegex.NUCLEOTIDE_RANGE}.*"),
                then=Cast(
                    RegexpMatchSubstring(
                        F("dna_hgvs"),
                        rf":[cg]\.{HGVSRegex.NUCLEOTIDE_POSITION}_\D*(?:\d+_)?(\d+)(?:_\?)?\D*",
                    ),
                    output_field=models.IntegerField(),
                ),
            ),
            default=None,
        ),
    )
    dna_change_position_range = AnnotationProperty(
        annotation=Case(
            When(
                ~Q(dna_hgvs__regex=rf".*:[cg]\.{HGVSRegex.NUCLEOTIDE_RANGE}.*"),
                then=None,
            ),
            When(
                Q(dna_hgvs__regex=rf".*:[cg]\.{HGVSRegex.NUCLEOTIDE_RANGE}.*")
                & Q(
                    dna_change_position_range_start__gt=F(
                        "dna_change_position_range_end"
                    )
                ),
                then=Func(
                    F("dna_change_position_range_end"),
                    F("dna_change_position_range_start"),
                    function="int4range",
                    output_field=IntegerRangeField(),
                ),
            ),
            default=Func(
                F("dna_change_position_range_start"),
                F("dna_change_position_range_end"),
                function="int4range",
                output_field=IntegerRangeField(),
            ),
        ),
    )
    dna_change_position = AnnotationProperty(
        verbose_name=_("DNA change position"),
        annotation=Case(
            When(
                ~Q(dna_hgvs__regex=rf".*:[cg]\.{HGVSRegex.NUCLEOTIDE_RANGE}.*")
                & Q(dna_hgvs__regex=rf".*:[cg]\.{HGVSRegex.NUCLEOTIDE_POSITION}.*")
                & ~Q(dna_hgvs__regex=rf".*:[cg]\.{HGVSRegex.INTRONIC_POSITION}.*"),
                then=Cast(
                    RegexpMatchSubstring(F("dna_hgvs"), rf":[cg]\.\D*(\d+)?\D*.*"),
                    output_field=models.IntegerField(),
                ),
            ),
            default=None,
            output_field=models.IntegerField(),
        ),
    )
    dna_change_position_intron = AnnotationProperty(
        annotation=Case(
            When(
                Q(dna_hgvs__regex=rf".*:[cg]\.\D*{HGVSRegex.INTRONIC_POSITION}.*"),
                then=Cast(
                    RegexpMatchSubstring(
                        F("dna_hgvs"), rf":[cg]\.\D*({HGVSRegex.INTRONIC_POSITION}).*"
                    ),
                    output_field=models.CharField(),
                ),
            ),
            default=None,
            output_field=models.CharField(),
        ),
    )
    regions = AnnotationProperty(
        annotation=Case(
            When(
                dna_hgvs__regex=rf".*:c\.{HGVSRegex.UTR3_POSITION}.*",
                then=ArrayAgg(
                    Concat(
                        "genes__display",
                        models.Value(" 3'UTR"),
                        output_field=models.CharField(),
                    ),
                    distinct=True,
                ),
            ),
            When(
                dna_hgvs__regex=rf".*:c\.{HGVSRegex.UTR5_POSITION}.*",
                then=ArrayAgg(
                    Concat(
                        "genes__display",
                        models.Value(" 5'UTR"),
                        output_field=models.CharField(),
                    ),
                    distinct=True,
                ),
            ),
            When(
                dna_hgvs__regex=rf".*:c\.\D*{HGVSRegex.INTRONIC_POSITION}.*",
                then=ArrayAgg(
                    Concat(
                        "genes__exons__gene__display",
                        models.Value(" intron "),
                        Case(
                            When(
                                Q(dna_change_position_intron__regex=r"\+"),
                                then=F("genes__exons__rank") + 1,
                            ),
                            default=F("genes__exons__rank"),
                        ),
                        output_field=models.CharField(),
                    ),
                    filter=Q(
                        genes__exons__coding_dna_region__contains=Cast(
                            RegexpMatchSubstring(
                                F("dna_change_position_intron"), r"(\d+)[\+-]\d+"
                            ),
                            output_field=models.IntegerField(),
                        )
                    ),
                    distinct=True,
                ),
            ),
            When(
                dna_hgvs__regex=r".*:c\..*",
                then=ArrayAgg(
                    Concat(
                        "genes__exons__gene__display",
                        models.Value(" exon "),
                        "genes__exons__rank",
                        output_field=models.CharField(),
                    ),
                    filter=Q(
                        genes__exons__coding_dna_region__contains=F(
                            "dna_change_position"
                        )
                    )
                    | Q(
                        genes__exons__coding_dna_region__overlap=F(
                            "dna_change_position_range"
                        )
                    ),
                    distinct=True,
                ),
            ),
            When(
                dna_hgvs__regex=r".*:g\..*",
                then=ArrayAgg(
                    Concat(
                        "genes__exons__gene__display",
                        models.Value(" exon "),
                        "genes__exons__rank",
                        output_field=models.CharField(),
                    ),
                    filter=Q(
                        genes__exons__coding_genomic_region__contains=F(
                            "dna_change_position"
                        )
                    )
                    | Q(
                        genes__exons__coding_genomic_region__overlap=F(
                            "dna_change_position_range"
                        )
                    ),
                    distinct=True,
                ),
            ),
            default=None,
        )
    )
    dna_change_type = AnnotationProperty(
        verbose_name=_("DNA change type"),
        annotation=Case(
            When(
                dna_hgvs__regex=HGVSRegex.DNA_TRANSLOCATION,
                then=Value(DNAChangeType.TRANSLOCATION),
            ),
            When(
                dna_hgvs__regex=HGVSRegex.DNA_TRANSPOSITION,
                then=Value(DNAChangeType.TRANSPOSITION),
            ),
            When(
                dna_hgvs__regex=HGVSRegex.DNA_DELETION_INSERTION,
                then=Value(DNAChangeType.DELETION_INSERTION),
            ),
            When(
                dna_hgvs__regex=HGVSRegex.DNA_INSERTION,
                then=Value(DNAChangeType.INSERTION),
            ),
            When(
                dna_hgvs__regex=HGVSRegex.DNA_DELETION,
                then=Value(DNAChangeType.DELETION),
            ),
            When(
                dna_hgvs__regex=HGVSRegex.DNA_DUPLICATION,
                then=Value(DNAChangeType.DUPLICATION),
            ),
            When(
                dna_hgvs__regex=HGVSRegex.DNA_UNCHANGED,
                then=Value(DNAChangeType.UNCHANGED),
            ),
            When(
                dna_hgvs__regex=HGVSRegex.DNA_INVERSION,
                then=Value(DNAChangeType.INVERSION),
            ),
            When(
                dna_hgvs__regex=HGVSRegex.DNA_SUBSTITUTION,
                then=Value(DNAChangeType.SUBSTITUTION),
            ),
            When(
                dna_hgvs__regex=HGVSRegex.DNA_REPETITION,
                then=Value(DNAChangeType.REPETITION),
            ),
            When(
                dna_hgvs__regex=HGVSRegex.DNA_METHYLATION_GAIN,
                then=Value(DNAChangeType.METHYLATION_GAIN),
            ),
            When(
                dna_hgvs__regex=HGVSRegex.DNA_METHYLATION_LOSS,
                then=Value(DNAChangeType.METHYLATION_LOSS),
            ),
            When(
                dna_hgvs__regex=HGVSRegex.DNA_METHYLATION_EQUAL,
                then=Value(DNAChangeType.METHYLATION_UNCHANGED),
            ),
            default=None,
            output_field=models.CharField(choices=DNAChangeType),
        ),
    )
    rna_hgvs = models.CharField(
        verbose_name=_("HGVS RNA-level expression"),
        help_text=_(
            "Description of the RNA sequence change using a valid HGVS-formatted expression, e.g. NM_000016.9:r.1212a>c"
        ),
        max_length=500,
        null=True,
        blank=True,
    )
    rna_reference_sequence = AnnotationProperty(
        verbose_name=_("RNA HGVS RefSeq"),
        annotation=RegexpMatchSubstring(F("rna_hgvs"), rf"({HGVSRegex.RNA_REFSEQ})"),
    )
    rna_change_position = AnnotationProperty(
        verbose_name=_("RNA change position"),
        annotation=RegexpMatchSubstring(
            F("rna_hgvs"), rf":r\.({HGVSRegex.NUCLEOTIDE_POSITION_OR_RANGE})"
        ),
    )
    rna_change_type = AnnotationProperty(
        verbose_name=_("RNA change type"),
        annotation=Case(
            When(
                rna_hgvs__regex=HGVSRegex.RNA_DELETION_INSERTION,
                then=Value(RNAChangeType.DELETION_INSERTION),
            ),
            When(
                rna_hgvs__regex=HGVSRegex.RNA_INSERTION,
                then=Value(RNAChangeType.INSERTION),
            ),
            When(
                rna_hgvs__regex=HGVSRegex.RNA_DELETION,
                then=Value(RNAChangeType.DELETION),
            ),
            When(
                rna_hgvs__regex=HGVSRegex.RNA_DUPLICATION,
                then=Value(RNAChangeType.DUPLICATION),
            ),
            When(
                rna_hgvs__regex=HGVSRegex.RNA_UNCHANGED,
                then=Value(RNAChangeType.UNCHANGED),
            ),
            When(
                rna_hgvs__regex=HGVSRegex.RNA_INVERSION,
                then=Value(RNAChangeType.INVERSION),
            ),
            When(
                rna_hgvs__regex=HGVSRegex.RNA_SUBSTITUTION,
                then=Value(RNAChangeType.SUBSTITUTION),
            ),
            When(
                rna_hgvs__regex=HGVSRegex.RNA_REPETITION,
                then=Value(RNAChangeType.REPETITION),
            ),
            default=None,
            output_field=models.CharField(choices=RNAChangeType),
        ),
    )
    protein_hgvs = models.CharField(
        verbose_name=_("HGVS protein-level expression"),
        help_text=_(
            "Description of the amino-acid sequence change using a valid HGVS-formatted expression, e.g. NP_000016.9:p.Leu24Tyr"
        ),
        max_length=500,
        null=True,
        blank=True,
    )
    protein_reference_sequence = AnnotationProperty(
        verbose_name=_("Protein HGVS RefSeq"),
        annotation=RegexpMatchSubstring(
            F("protein_hgvs"), rf"({HGVSRegex.PROTEIN_REFSEQ})"
        ),
    )
    protein_change_type = AnnotationProperty(
        verbose_name=_("Protein change type"),
        annotation=Case(
            When(
                protein_hgvs__regex=HGVSRegex.PROTEIN_DELETION_INSERTION,
                then=Value(ProteinChangeType.DELETION_INSERTION),
            ),
            When(
                protein_hgvs__regex=HGVSRegex.PROTEIN_INSERTION,
                then=Value(ProteinChangeType.INSERTION),
            ),
            When(
                protein_hgvs__regex=HGVSRegex.PROTEIN_DELETION,
                then=Value(ProteinChangeType.DELETION),
            ),
            When(
                protein_hgvs__regex=HGVSRegex.PROTEIN_DUPLICATION,
                then=Value(ProteinChangeType.DUPLICATION),
            ),
            When(
                protein_hgvs__regex=HGVSRegex.PROTEIN_NONSENSE,
                then=Value(ProteinChangeType.NONSENSE),
            ),
            When(
                protein_hgvs__regex=HGVSRegex.PROTEIN_FRAMESHIFT,
                then=Value(ProteinChangeType.FRAMESHIFT),
            ),
            When(
                protein_hgvs__regex=HGVSRegex.PROTEIN_EXTENSION,
                then=Value(ProteinChangeType.EXTENSION),
            ),
            When(
                protein_hgvs__regex=HGVSRegex.PROTEIN_REPETITION,
                then=Value(ProteinChangeType.REPETITION),
            ),
            When(
                protein_hgvs__regex=HGVSRegex.PROTEIN_SILENT,
                then=Value(ProteinChangeType.SILENT),
            ),
            When(
                protein_hgvs__regex=HGVSRegex.PROTEIN_MISSENSE,
                then=Value(ProteinChangeType.MISSENSE),
            ),
            When(
                protein_hgvs__regex=rf"p.\(?{HGVSRegex.PROTEIN_NOTHING}\)?",
                then=Value(ProteinChangeType.NO_PROTEIN),
            ),
            When(
                protein_hgvs__regex=rf"p.\(?{HGVSRegex.PROTEIN_UNKNOWN}\)?",
                then=Value(ProteinChangeType.UNKNOWN),
            ),
            default=None,
            output_field=models.CharField(choices=ProteinChangeType),
        ),
    )
    nucleotides_length = AnnotationProperty(
        verbose_name=_("Total affected nucleotides (estimated if uncertain)"),
        annotation=Case(
            When(
                Q(dna_change_position_range_start__isnull=False)
                & Q(dna_change_position_range_end__isnull=False),
                then=Value(1)
                + F("dna_change_position_range_end")
                - F("dna_change_position_range_start"),
            ),
            When(Q(dna_change_position__isnull=False), then=Value(1)),
            default=None,
            output_field=models.IntegerField(),
        ),
    )
    molecular_consequence = termfields.CodedConceptField(
        verbose_name=_("Molecular consequence"),
        help_text=_(
            "The calculated or observed effect of a variant on its downstream transcript and, if applicable, ensuing protein sequence."
        ),
        terminology=terminologies.MolecularConsequence,
        null=True,
        blank=True,
    )
    copy_number = models.PositiveSmallIntegerField(
        verbose_name=_("Copy number"),
        help_text=_(
            "Genomic structural variant copy number. It is a unit-less value. Note that a copy number of 1 can imply a deletion."
        ),
        null=True,
        blank=True,
    )
    allele_frequency = models.FloatField(
        verbose_name=_("Allele frequency"),
        help_text=_(
            "The relative frequency (value in range [0,1]) of the allele at a given locus in the sample."
        ),
        validators=[MinValueValidator(0), MaxValueValidator(1)],
        null=True,
        blank=True,
    )
    allele_depth = models.PositiveIntegerField(
        verbose_name=_("Allele depth (reads)"),
        help_text=_(
            "Specifies the number of reads that identified the allele in question whether it consists of one or a small sequence of contiguous nucleotides."
        ),
        null=True,
        blank=True,
    )
    zygosity = termfields.CodedConceptField(
        verbose_name=_("Zygosity"),
        help_text=_(
            "The observed level of occurrence of the variant in the set of chromosomes."
        ),
        terminology=terminologies.Zygosity,
        null=True,
        blank=True,
    )
    inheritance = termfields.CodedConceptField(
        verbose_name=_("Inheritance"),
        help_text=_("Variant inheritance origin (if known)."),
        terminology=terminologies.VariantInheritance,
        null=True,
        blank=True,
    )
    coordinate_system = termfields.CodedConceptField(
        verbose_name=_("Coordinate system"),
        help_text=_(
            "Genomic coordinate system used for identifying nucleotides or amino acids within a sequence."
        ),
        terminology=terminologies.GenomicCoordinateSystem,
        null=True,
        blank=True,
    )
    clinvar = models.CharField(
        verbose_name=_("ClinVar accession number"),
        help_text=_(
            "Accession number in the ClinVar variant database, given for cross-reference."
        ),
        null=True,
        blank=True,
    )

    class Meta:
        constraints = [
            CheckConstraint(
                check=Q(dna_hgvs__isnull=True) | Q(dna_hgvs__regex=HGVSRegex.DNA_HGVS),
                name="valid_dna_hgvs",
                violation_error_message="DNA HGVS must be a valid 'c.'-HGVS expression.",
            ),
            CheckConstraint(
                check=Q(rna_hgvs__isnull=True) | Q(rna_hgvs__regex=HGVSRegex.RNA_HGVS),
                name="valid_rna_hgvs",
                violation_error_message="RNA HGVS must be a valid 'r.'-HGVS expression.",
            ),
            CheckConstraint(
                check=Q(protein_hgvs__isnull=True)
                | Q(protein_hgvs__regex=HGVSRegex.PROTEIN_HGVS),
                name="valid_protein_hgvs",
                violation_error_message="Protein HGVS must be a valid 'p.'-HGVS expression.",
            ),
        ]

    @property
    def mutation_label(self):
        if self.molecular_consequence:
            if self.molecular_consequence.code == "SO:0001911":  # copy_number_increase
                return "amplification"
            elif (
                self.molecular_consequence.code == "SO:0001912"
            ):  # copy_number_decrease
                return "loss"
            elif self.molecular_consequence.code == "SO:0001565":  # gene_fusion
                return "fusion"
            else:
                return str(self.molecular_consequence).lower().replace("_", " ")
        elif self.copy_number:
            return "amplification" if self.copy_number > 2 else "loss"
        elif self.protein_change_type:
            return self.protein_change_type
        else:
            return self.dna_change_type

    @property
    def genes_label(self):
        genes = self.genes.all()
        if len(genes) == 1 and (gene := genes.first()):
            genes = gene.display
        else:
            genes = "-".join([g.display for g in genes])
        return genes

    @property
    def aminoacid_change(self):
        if self.protein_hgvs:
            protein_change = self.protein_hgvs.split("p.")[-1]
            if "?" in protein_change:
                return None
            if protein_change[0] == "(" and protein_change[-1] == ")":
                return protein_change[1:-1]
            else:
                return protein_change
        return None

    @property
    def description(self):
        significance = (
            "(Pathogenic)" if self.is_pathogenic else "(VUS)" if self.is_vus else None
        )
        return " ".join(
            [
                piece
                for piece in [
                    self.genes_label,
                    self.aminoacid_change,
                    self.mutation_label,
                    significance,
                ]
                if piece
            ]
        )
