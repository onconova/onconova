import pghistory 

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
from django.db.backends.postgresql.psycopg_any import NumericRange

from typing import Union
from django.contrib.postgres.aggregates import StringAgg, ArrayAgg
from django.db.models import Q, F, Func, CheckConstraint, When, Case, Value, Subquery, OuterRef
from django.db.models.expressions import RawSQL

from django.db.models.functions import Cast, Coalesce
from django.db.models.fields.json import KeyTextTransform

from queryable_properties.properties import AnnotationProperty, SubqueryFieldProperty
from queryable_properties.managers import QueryablePropertiesManager

from pop.core.models import BaseModel 
from pop.oncology.models import PatientCase 
import pop.terminology.fields as termfields 
import pop.terminology.models as terminologies 

    
class HGVSRegex:
    """ BASED ON v21.1.2 of HGVS"""

    AMINOACID = r"(?:Ter|(?:Gly|Ala|Val|Leu|Ile|Met|Phe|Trp|Pro|Ser|Thr|Cys|Tyr|Asn|Gln|Asp|Glu|Lys|Arg|His))"
    REPETITION_COPIES = r"\[(?:\d+|(?:\(\d+_\d+\)))\]"

    # Reference sequence identifiers
    VERSIONED_NUMBER = r"\d+(?:\.\d{1,3})?"
    
    # NCBI RefSeq Prefixes
    # (https://www.ncbi.nlm.nih.gov/books/NBK21091/table/ch18.T.refseq_accession_numbers_and_mole/?report=objectonly)
    GENOMIC_REFSEQ_PREFIX = r"(?:NC_|AC_|NG_|NT_|NW_|NZ_)"
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
    
    GENOMIC_REFSEQ = fr"(?:{GENOMIC_NCIB_REFSEQ})|(?:{GENOMIC_ENSEMBL_REFSEQ})|(?:{GENOMIC_LRG_REFSEQ})"
    RNA_REFSEQ = fr"(?:{RNA_NCIB_REFSEQ})|(?:{RNA_ENSEMBL_REFSEQ})|(?:{RNA_LRG_REFSEQ})"
    PROTEIN_REFSEQ = fr"(?:{PROTEIN_NCIB_REFSEQ})|(?:{PROTEIN_ENSEMBL_REFSEQ})|(?:{PROTEIN_LRG_REFSEQ})"

    # Genomic coordinates
    POSITION = r'(?:\?|\*|(?:\+|-)?\d+(?:(?:\+|-)?\d+)?)'
    NUCLEOTIDE_UNCERTAIN_POSITION = rf"\({POSITION}_{POSITION}\)"
    NUCLEOTIDE_POSITION = fr"(?:{POSITION}|{NUCLEOTIDE_UNCERTAIN_POSITION})"
    NUCLEOTIDE_RANGE = fr"(?:{NUCLEOTIDE_POSITION}_{NUCLEOTIDE_POSITION})"
    NUCLEOTIDE_POSITION_OR_RANGE = fr"(?:{NUCLEOTIDE_RANGE}|{NUCLEOTIDE_POSITION})"
    AMINOACID_UNCERTAIN_POSITION= rf"(?:(?:\(\?_{AMINOACID}\d+\))|(?:\({AMINOACID}\d+_\?\))|(?:\({AMINOACID}\d+_{AMINOACID}\d+\)))"
    AMINOACID_POSITION = fr"(?:{AMINOACID}\d+|{AMINOACID_UNCERTAIN_POSITION})"
    AMINOACID_RANGE = fr"(?:{AMINOACID_POSITION}_{AMINOACID_POSITION})"
    AMINOACID_POSITION_OR_RANGE = fr"(?:{AMINOACID_RANGE}|{AMINOACID_POSITION})"
    
    # Types of variants
    DNA_VARIANT_TYPE = r'>|delins|ins|del|dup|inv|='
    RNA_VARIANT_TYPE = r'>|delins|ins|del|dup|inv'
    PROTEIN_VARIANT_TYPE = r'(?:delins|ins|del|dup|fsTer|fs|extTer|ext|Ter|\*|)|(?:)'

    # Genomic sequences 
    DNA_SEQUENCE = r"(?:A|C|G|T|B|D|H|K|M|N|R|S|V|W|Y|X|-)+"
    RNA_SEQUENCE = r"(?:a|c|g|t|b|d|h|k|m|n|r|s|v|w|y)+"
    PROTEIN_SEQUENCE = rf"(?:{AMINOACID}+)"

    # DNA HGVS scenarios
    DNA_UNCHANGED = rf'{NUCLEOTIDE_POSITION_OR_RANGE}='
    DNA_SUBSTITUTION = rf'{NUCLEOTIDE_POSITION}{DNA_SEQUENCE}>{DNA_SEQUENCE}'
    DNA_DELETION_INSERTION = rf'{NUCLEOTIDE_POSITION_OR_RANGE}delins{DNA_SEQUENCE}'
    DNA_INSERTION = rf'{NUCLEOTIDE_RANGE}ins(?:{DNA_SEQUENCE}|{NUCLEOTIDE_RANGE})'
    DNA_DELETION = rf'{NUCLEOTIDE_POSITION_OR_RANGE}del'
    DNA_DUPLICATION = rf'{NUCLEOTIDE_POSITION_OR_RANGE}dup'
    DNA_INVERSION = rf'{NUCLEOTIDE_POSITION_OR_RANGE}inv'
    DNA_REPETITION = rf'{NUCLEOTIDE_POSITION_OR_RANGE}(?:{DNA_SEQUENCE})?{REPETITION_COPIES}'
    DNA_METHYLATION_GAIN = rf'{NUCLEOTIDE_POSITION_OR_RANGE}\|gom'
    DNA_METHYLATION_LOSS = rf'{NUCLEOTIDE_POSITION_OR_RANGE}\|lom'
    DNA_METHYLATION_EQUAL = rf'{NUCLEOTIDE_POSITION_OR_RANGE}\|met='
    DNA_TRANSLOCATION = rf'{NUCLEOTIDE_POSITION_OR_RANGE}delins\[{GENOMIC_REFSEQ}:g\.{NUCLEOTIDE_POSITION_OR_RANGE}\]'
    DNA_TRANSPOSITION = rf'{NUCLEOTIDE_POSITION_OR_RANGE}ins\[{GENOMIC_REFSEQ}:g\.{NUCLEOTIDE_POSITION_OR_RANGE}\]\sand\s{GENOMIC_REFSEQ}:g\.{NUCLEOTIDE_POSITION_OR_RANGE}del'
    DNA_CHANGE_DESCRIPTION = rf'{DNA_UNCHANGED}|{DNA_SUBSTITUTION}|{DNA_TRANSLOCATION}|{DNA_TRANSPOSITION}|{DNA_DELETION_INSERTION}|{DNA_INSERTION}|{DNA_DELETION}|{DNA_DUPLICATION}|{DNA_INVERSION}|{DNA_REPETITION}|{DNA_METHYLATION_GAIN}|{DNA_METHYLATION_LOSS}|{DNA_METHYLATION_EQUAL}'

    # RNA HGVS scenarios
    RNA_UNCHANGED = rf'{NUCLEOTIDE_POSITION_OR_RANGE}='
    RNA_SUBSTITUTION = rf'{NUCLEOTIDE_POSITION}{RNA_SEQUENCE}>{RNA_SEQUENCE}'
    RNA_DELETION_INSERTION = rf'{NUCLEOTIDE_POSITION_OR_RANGE}delins{RNA_SEQUENCE}'
    RNA_INSERTION = rf'{NUCLEOTIDE_RANGE}ins(?:{RNA_SEQUENCE}|{NUCLEOTIDE_RANGE})'
    RNA_DELETION = rf'{NUCLEOTIDE_POSITION_OR_RANGE}del'
    RNA_DUPLICATION = rf'{NUCLEOTIDE_POSITION_OR_RANGE}dup'
    RNA_INVERSION = rf'{NUCLEOTIDE_POSITION_OR_RANGE}inv'
    RNA_REPETITION = rf'{NUCLEOTIDE_POSITION_OR_RANGE}(?:{RNA_SEQUENCE})?{REPETITION_COPIES}'
    RNA_METHYLATION_GAIN = rf'{NUCLEOTIDE_POSITION_OR_RANGE}\|gom'
    RNA_METHYLATION_LOSS = rf'{NUCLEOTIDE_POSITION_OR_RANGE}\|lom'
    RNA_METHYLATION_EQUAL = rf'{NUCLEOTIDE_POSITION_OR_RANGE}\|met='
    RNA_CHANGE_DESCRIPTION = rf'{RNA_UNCHANGED}|{RNA_SUBSTITUTION}|{RNA_DELETION_INSERTION}|{RNA_INSERTION}|{RNA_DELETION}|{RNA_DUPLICATION}|{RNA_INVERSION}|{RNA_REPETITION}'

    # Protein HGVS scenarios
    PROTEIN_NOTHING = rf'0$'
    PROTEIN_SILENT = rf'{AMINOACID_POSITION}='
    PROTEIN_MISSENSE = rf'{AMINOACID_POSITION}{PROTEIN_SEQUENCE}'
    PROTEIN_DELETION_INSERTION = rf'{AMINOACID_POSITION_OR_RANGE}delins{PROTEIN_SEQUENCE}'
    PROTEIN_INSERTION = rf'{AMINOACID_RANGE}ins{PROTEIN_SEQUENCE}'
    PROTEIN_DELETION = rf'{AMINOACID_POSITION_OR_RANGE}del'
    PROTEIN_DUPLICATION = rf'{AMINOACID_POSITION_OR_RANGE}dup'
    PROTEIN_NONSENSE = rf'{AMINOACID_POSITION_OR_RANGE}(?:Ter|\*)'
    PROTEIN_REPETITION = rf'\(?{AMINOACID_POSITION_OR_RANGE}\)?{REPETITION_COPIES}'
    PROTEIN_FRAMESHIFT = rf'{AMINOACID_POSITION_OR_RANGE}{PROTEIN_SEQUENCE}?fs(?:Ter)?(?:{POSITION})*'
    PROTEIN_EXTENSION = rf'(?:(?:Met1ext-\d+)|(?:Ter\d+{PROTEIN_SEQUENCE}extTer\d+))'
    PROTEIN_CHANGE_DESCRIPTION = rf'{PROTEIN_NOTHING}|{PROTEIN_DELETION_INSERTION}|{PROTEIN_DELETION}|{PROTEIN_INSERTION}|{PROTEIN_DUPLICATION}|{PROTEIN_NONSENSE}|{PROTEIN_FRAMESHIFT}|{PROTEIN_EXTENSION}|{PROTEIN_REPETITION}|{PROTEIN_MISSENSE}|{PROTEIN_SILENT}'

    # Complete HGVS regexes for each scenario
    DNA_HGVS = rf'(?:{GENOMIC_REFSEQ}:g)|(?:(?:{GENOMIC_REFSEQ})?\(?({RNA_REFSEQ})\)?:c)\.({DNA_CHANGE_DESCRIPTION})'
    RNA_HGVS = rf'({RNA_REFSEQ}):r\.\(?({RNA_CHANGE_DESCRIPTION})\)?'
    PROTEIN_HGVS = rf'({PROTEIN_REFSEQ}):p\.\(?({PROTEIN_CHANGE_DESCRIPTION})\)?'

class RegexpMatchSubstring(Func):
    """
    Extracts the nth matching group from an HGVS expression using PostgreSQL's `regexp_match()`.
    
    :param expression: The database column containing the HGVS string.
    :param group: The group to capture.
    :param group_index: The index of the capturing group to extract (1-based).
    """
    function = 'substring'

    def __init__(self, expression, regex, **extra):
        # PostgreSQL regexp_match() returns an array, so we extract the nth element
        template = "(%(function)s(%(expressions)s, '%(regex)s'))"
        super().__init__(
            expression,
            regex=regex,
            template=template,
            **extra
        )

@pghistory.track()
class GenomicVariant(BaseModel):

    objects = QueryablePropertiesManager()
    
    class GenomicVariantAssessment(models.TextChoices):
        PRESENT = 'present'
        ABSENT = 'absent'
        NOCALL = 'no-call'
        INDETERMINATE = 'indeterminate'

    class GenomicVariantConfidence(models.TextChoices):
        LOW = 'low'
        HIGH = 'high'
        INDETERMINATE = 'indeterminate'

    class GenomicVariantClinicalRelevance(models.TextChoices):
        PATHOGENIC = 'pathogenic'
        LIKELY_PATHOGENIC = 'likely_pathogenic'
        UNCERTAIN_SIGNIFICANCE = 'uncertain_significance'
        AMBIGUOUS = 'ambiguous'
        LIKELY_BENIGN = 'likely_benign'
        BENIGN = 'benign'

    class DNAChangeType(models.TextChoices):
        SUBSTITUTION = 'substitution'
        DELETION_INSERTION = 'deletion-insertion'
        INSERTION = 'insertion'
        DELETION = 'deletion'
        DUPLICATION = 'duplication'
        INVERSION = 'inversion'
        UNCHANGED = 'unchanged'
        REPETITION = 'repetition'
        TRANSLOCATION = 'translocation'
        TRANSPOSITION = 'transposition'
        METHYLATION_GAIN = 'methylation-gain'
        METHYLATION_LOSS = 'methylation-loss'
        METHYLATION_UNCHANGED = 'methylation-unchanged'

    class RNAChangeType(models.TextChoices):
        SUBSTITUTION = 'substitution'
        DELETION_INSERTION = 'deletion-insertion'
        INSERTION = 'insertion'
        DELETION = 'deletion'
        DUPLICATION = 'duplication'
        INVERSION = 'inversion'
        UNCHANGED = 'unchanged'
        REPETITION = 'repetition'

    class ProteinChangeType(models.TextChoices):
        MISSENSE = 'missense'
        NONSENSE = 'nonsense'
        DELETION_INSERTION = 'deletion-insertion'
        INSERTION = 'insertion'
        DELETION = 'deletion'
        DUPLICATION = 'duplication'
        FRAMESHIFT = 'frameshift'
        EXTENSION = 'extension'
        SILENT = 'silent'
        NO_PROTEIN = 'no-protein'
        REPETITION = 'repetition'

    case = models.ForeignKey(
        verbose_name = _('Patient case'),
        help_text = _("Indicates the case of the patient who' genomic variant is described"),
        to = PatientCase,
        related_name = 'genomic_variants',
        on_delete = models.CASCADE,
    )
    date = models.DateField(
        verbose_name = _('Assessment date'),
        help_text=_("Clinically-relevant date at which the genomic variant was detected and/or reported."),
    )
    gene_panel = models.CharField(
        verbose_name = _('Gene panel'),
        help_text=_('Commercial or official name of the gene panel tested to identify the variant'),
        max_length = 200,  
        null = True, blank = True,
    )
    assessment = models.CharField(
        verbose_name = _('Assessment'),
        help_text=_('Classification of whether the variant is present or absent in the analysis results. Relevant for genomic studies that report presence and absence of variants.'),
        max_length = 15,  
        choices = GenomicVariantAssessment,
        null = True, blank = True,
    )
    confidence = models.CharField(
        verbose_name = _('Confidence'),
        help_text=_('Classification of the confidence for a true positive variant call based e.g. calling thresholds or phred-scaled confidence scores.'),
        max_length = 15,  
        choices = GenomicVariantConfidence,
        null = True, blank = True,
    )
    analysis_method = termfields.CodedConceptField(
        verbose_name = _('Analysis method'),
        help_text = _("Analysis method used to detect the variant"),
        terminology = terminologies.StructuralVariantAnalysisMethod,
        null = True, blank = True,
    )
    clinical_relevance = models.CharField(
        verbose_name = _('Clinical relevance'),
        help_text = _("Classification of the clinical relevance or pathogenicity of the variant."),
        choices = GenomicVariantClinicalRelevance,
        null = True, blank = True,
    )
    is_vus = models.GeneratedField(
        verbose_name = _('Is pathogenic'),
        help_text = _("Indicates if the variant is of unknown signfiance (determined automatically based on the clinical relevance classification)"),
        expression = models.Case(
            models.When(models.Q(clinical_relevance__isnull = True), then = models.Value(None)),  
            models.When(models.Q(clinical_relevance = GenomicVariantClinicalRelevance.UNCERTAIN_SIGNIFICANCE), then = models.Value(True)),  
            default = models.Value(False),
            output_field = models.BooleanField(),
        ),
        output_field = models.BooleanField(),
        db_persist = True,
        null = True,
    )   
    is_pathogenic = models.GeneratedField(
        verbose_name = _('Is pathogenic'),
        help_text = _("Indicates if the variant is pathogenic (determined automatically based on the clinical relevance classification)"),
        expression = models.Case(
            models.When(models.Q(clinical_relevance__isnull = True), then = models.Value(None)),  
            models.When(
                models.Q(clinical_relevance = GenomicVariantClinicalRelevance.LIKELY_PATHOGENIC) | models.Q(clinical_relevance = GenomicVariantClinicalRelevance.PATHOGENIC), 
                then = models.Value(True)
            ),  
            default = models.Value(False),
            output_field = models.BooleanField(),
        ),
        output_field = models.BooleanField(),
        db_persist = True,
    )    
    genes = termfields.CodedConceptField(
        verbose_name = _('Gene(s)'),
        help_text = _("Gene(s) affected by this variant"),
        terminology = terminologies.Gene,
        multiple = True,
    )
    cytogenetic_location = AnnotationProperty(
        verbose_name=_('Cytogenetic location'),
        annotation = StringAgg(Cast(KeyTextTransform('location', 'genes__properties'), output_field=models.CharField()),delimiter='::', distinct=True)
    )
    chromosomes = AnnotationProperty(
        verbose_name=_('Chromosomes'),
        annotation = Func(
            F('cytogenetic_location'),
            function = "REGEXP_MATCHES",
            template = "ARRAY(SELECT unnest(REGEXP_MATCHES(unnest(REGEXP_SPLIT_TO_ARRAY(%(expressions)s, '::')), '^([0-9XY]+)')))::TEXT[]",
            output_field = models.CharField(choices=[(chr, chr) for chr in ['X', 'Y', *list(range(1,23))]]), 
       )
    )
    genome_assembly_version = termfields.CodedConceptField(
        verbose_name = _('Genome assembly version'),
        help_text = _('The reference genome assembly versionused in this analysis.'),
        terminology = terminologies.ReferenceGenomeBuild,
        null = True, blank = True,
    )
    dna_hgvs = models.CharField(
        verbose_name=_('HGVS DNA-level expression'),
        help_text=_("Description of the coding (cDNA) sequence change using a valid HGVS-formatted expression, e.g. NM_005228.5:c.2369C>T"),
        max_length=500,
        null=True, blank=True,
    )
    dna_reference_sequence = AnnotationProperty(
        verbose_name = _('DNA HGVS RefSeq'),
        annotation = Coalesce(
            RegexpMatchSubstring(F('dna_hgvs'), fr'({HGVSRegex.RNA_REFSEQ})'),
            RegexpMatchSubstring(F('dna_hgvs'), fr'({HGVSRegex.GENOMIC_REFSEQ})'),
        ),
    )
    dna_change_position_range_start = AnnotationProperty(
        annotation=Case(
            When(
                Q(dna_hgvs__regex=rf'.*:[cg]\.{HGVSRegex.NUCLEOTIDE_RANGE}.*'),
                then=Cast(RegexpMatchSubstring(F('dna_hgvs'),rf':[cg]\.\D*(\d+)?(?:_\d+)?\D*_{HGVSRegex.NUCLEOTIDE_POSITION}'), output_field=models.IntegerField())
            ),
            default=None, output_field=models.IntegerField(),
        ),
    )
    dna_change_position_range_end = AnnotationProperty(
        annotation=Case(
            When(
                Q(dna_hgvs__regex=rf'.*:[cg]\.{HGVSRegex.NUCLEOTIDE_RANGE}.*'),
                then=Cast(RegexpMatchSubstring(F('dna_hgvs'),rf':[cg]\.{HGVSRegex.NUCLEOTIDE_POSITION}_\D*(?:\d+_)?(\d+)(?:_\?)?\D*'), output_field=models.IntegerField())
            ),
            default=None, output_field=models.IntegerField(),
        ),
    )
    dna_change_position = AnnotationProperty(
        verbose_name = _('DNA change position'),
        annotation =Case(
            When(
                ~Q(dna_hgvs__regex=rf'.*:[cg]\.{HGVSRegex.NUCLEOTIDE_RANGE}.*') & Q(dna_hgvs__regex=rf'.*:[cg]\.{HGVSRegex.NUCLEOTIDE_POSITION}.*'),
                then=Cast(RegexpMatchSubstring(F('dna_hgvs'),rf':[cg]\.\D*(\d+)?\D*.*'), output_field=models.IntegerField())
            ),
            default=None, output_field=models.IntegerField(),
        ),
    )    
    exons = AnnotationProperty(
        annotation=Case(
            When(dna_hgvs__regex=r'.*:c\..*', then=ArrayAgg(
                F('genes__exons__rank'), 
                filter=
                    Q(genes__exons__coding_dna_region__contains=F('dna_change_position'))
                    |                    
                    Q(genes__exons__coding_dna_region__contains=F('dna_change_position_range_start'))
                    |                    
                    Q(genes__exons__coding_dna_region__contains=F('dna_change_position_range_end'))
            )),
            When(dna_hgvs__regex=r'.*:g\..*', then=ArrayAgg(
                F('genes__exons__rank'), 
                filter=
                    Q(genes__exons__coding_genomic_region__contains=F('dna_change_position'))
                    |                    
                    Q(genes__exons__coding_genomic_region__contains=F('dna_change_position_range_start'))
                    |                    
                    Q(genes__exons__coding_genomic_region__contains=F('dna_change_position_range_end'))
            )),
            default=None,
        )            
    )
    dna_change_type = AnnotationProperty(
        verbose_name = _('DNA change type'),
        annotation = Case(
            When(dna_hgvs__regex=HGVSRegex.DNA_TRANSLOCATION, then=Value(DNAChangeType.TRANSLOCATION)),
            When(dna_hgvs__regex=HGVSRegex.DNA_TRANSPOSITION, then=Value(DNAChangeType.TRANSPOSITION)),
            When(dna_hgvs__regex=HGVSRegex.DNA_DELETION_INSERTION, then=Value(DNAChangeType.DELETION_INSERTION)),
            When(dna_hgvs__regex=HGVSRegex.DNA_INSERTION, then=Value(DNAChangeType.INSERTION)),
            When(dna_hgvs__regex=HGVSRegex.DNA_DELETION, then=Value(DNAChangeType.DELETION)),
            When(dna_hgvs__regex=HGVSRegex.DNA_DUPLICATION, then=Value(DNAChangeType.DUPLICATION)),
            When(dna_hgvs__regex=HGVSRegex.DNA_UNCHANGED, then=Value(DNAChangeType.UNCHANGED)),
            When(dna_hgvs__regex=HGVSRegex.DNA_INVERSION, then=Value(DNAChangeType.INVERSION)),
            When(dna_hgvs__regex=HGVSRegex.DNA_SUBSTITUTION, then=Value(DNAChangeType.SUBSTITUTION)),
            When(dna_hgvs__regex=HGVSRegex.DNA_REPETITION, then=Value(DNAChangeType.REPETITION)),
            When(dna_hgvs__regex=HGVSRegex.DNA_METHYLATION_GAIN, then=Value(DNAChangeType.METHYLATION_GAIN)),
            When(dna_hgvs__regex=HGVSRegex.DNA_METHYLATION_LOSS, then=Value(DNAChangeType.METHYLATION_LOSS)),
            When(dna_hgvs__regex=HGVSRegex.DNA_METHYLATION_EQUAL, then=Value(DNAChangeType.METHYLATION_UNCHANGED)),
            default=None,
            output_field=models.CharField(choices=DNAChangeType)
        ),
    )
    rna_hgvs = models.CharField(
        verbose_name=_('HGVS RNA-level expression'),
        help_text=_("Description of the RNA sequence change using a valid HGVS-formatted expression, e.g. NM_000016.9:r.1212a>c"),
        max_length=500,
        null=True, blank=True,
    )
    rna_reference_sequence = AnnotationProperty(
        verbose_name = _('RNA HGVS RefSeq'),
        annotation = RegexpMatchSubstring(F('rna_hgvs'), fr'({HGVSRegex.RNA_REFSEQ})'),
    )
    rna_change_position = AnnotationProperty(
        verbose_name = _('RNA change position'),
        annotation = RegexpMatchSubstring(F('rna_hgvs'), fr":r\.({HGVSRegex.NUCLEOTIDE_POSITION_OR_RANGE})"),
    )    
    rna_change_type = AnnotationProperty(
        verbose_name = _('RNA change type'),
        annotation = Case(
            When(rna_hgvs__regex=HGVSRegex.RNA_DELETION_INSERTION, then=Value(RNAChangeType.DELETION_INSERTION)),
            When(rna_hgvs__regex=HGVSRegex.RNA_INSERTION, then=Value(RNAChangeType.INSERTION)),
            When(rna_hgvs__regex=HGVSRegex.RNA_DELETION, then=Value(RNAChangeType.DELETION)),
            When(rna_hgvs__regex=HGVSRegex.RNA_DUPLICATION, then=Value(RNAChangeType.DUPLICATION)),
            When(rna_hgvs__regex=HGVSRegex.RNA_UNCHANGED, then=Value(RNAChangeType.UNCHANGED)),
            When(rna_hgvs__regex=HGVSRegex.RNA_INVERSION, then=Value(RNAChangeType.INVERSION)),
            When(rna_hgvs__regex=HGVSRegex.RNA_SUBSTITUTION, then=Value(RNAChangeType.SUBSTITUTION)),
            When(rna_hgvs__regex=HGVSRegex.RNA_REPETITION, then=Value(RNAChangeType.REPETITION)),
            default=None,
            output_field=models.CharField(choices=RNAChangeType)
        ),
    ) 
    protein_hgvs = models.CharField(
        verbose_name=_('HGVS protein-level expression'),
        help_text=_("Description of the amino-acid sequence change using a valid HGVS-formatted expression, e.g. NP_000016.9:p.Leu24Tyr"),
        max_length=500,
        null=True, blank=True,
    )
    protein_reference_sequence = AnnotationProperty(
        verbose_name = _('Protein HGVS RefSeq'),
        annotation = RegexpMatchSubstring(F('protein_hgvs'), fr'({HGVSRegex.PROTEIN_REFSEQ})'),
    )
    protein_change_type = AnnotationProperty(
        verbose_name = _('Protein change type'),
        annotation = Case(
            When(protein_hgvs__regex=HGVSRegex.PROTEIN_DELETION_INSERTION, then=Value(ProteinChangeType.DELETION_INSERTION)),
            When(protein_hgvs__regex=HGVSRegex.PROTEIN_INSERTION, then=Value(ProteinChangeType.INSERTION)),
            When(protein_hgvs__regex=HGVSRegex.PROTEIN_DELETION, then=Value(ProteinChangeType.DELETION)),
            When(protein_hgvs__regex=HGVSRegex.PROTEIN_DUPLICATION, then=Value(ProteinChangeType.DUPLICATION)),
            When(protein_hgvs__regex=HGVSRegex.PROTEIN_NONSENSE, then=Value(ProteinChangeType.NONSENSE)),
            When(protein_hgvs__regex=HGVSRegex.PROTEIN_FRAMESHIFT, then=Value(ProteinChangeType.FRAMESHIFT)),
            When(protein_hgvs__regex=HGVSRegex.PROTEIN_EXTENSION, then=Value(ProteinChangeType.EXTENSION)),
            When(protein_hgvs__regex=HGVSRegex.PROTEIN_REPETITION, then=Value(ProteinChangeType.REPETITION)),
            When(protein_hgvs__regex=HGVSRegex.PROTEIN_SILENT, then=Value(ProteinChangeType.SILENT)),
            When(protein_hgvs__regex=HGVSRegex.PROTEIN_NOTHING, then=Value(ProteinChangeType.NO_PROTEIN)),
            When(protein_hgvs__regex=HGVSRegex.PROTEIN_MISSENSE, then=Value(ProteinChangeType.MISSENSE)),
            default=None,
            output_field=models.CharField(choices=ProteinChangeType)
        ),
    )    
    nucleotides_length = AnnotationProperty(
        verbose_name = _('Total affected nucleotides (estimated if uncertain)'),
        annotation = Case(
            When(
                Q(dna_change_position_range_start__isnull=False) & Q(dna_change_position_range_end__isnull=False), 
                then=F('dna_change_position_range_end') - F('dna_change_position_range_start') + Value(1)
            ),
            When(Q(dna_change_position__isnull=False), then=Value(1)),
            default=None, output_field=models.IntegerField(),
        ),
    )    
    molecular_consequence = termfields.CodedConceptField(
        verbose_name = _('Molecular consequence'),
        help_text = _('The calculated or observed effect of a variant on its downstream transcript and, if applicable, ensuing protein sequence.'),
        terminology = terminologies.MolecularConsequence,
        null = True, blank = True,
    )
    copy_number = models.PositiveSmallIntegerField(
        verbose_name = _('Copy number'),
        help_text = _('Genomic structural variant copy number. It is a unit-less value. Note that a copy number of 1 can imply a deletion.'),
        null = True, blank = True,
    )
    allele_frequency = models.FloatField(
        verbose_name = _('Allele frequency'),
        help_text = _('The relative frequency (value in range [0,1]) of the allele at a given locus in the sample.'),
        validators = [MinValueValidator(0), MaxValueValidator(1)],
        null = True, blank = True,
    )
    allele_depth = models.PositiveIntegerField(
        verbose_name = _('Allele depth (reads)'),
        help_text = _('Specifies the number of reads that identified the allele in question whether it consists of one or a small sequence of contiguous nucleotides.'),
        null = True, blank = True,
    )
    zygosity = termfields.CodedConceptField(
        verbose_name = _('Zygosity'),
        help_text = _('The observed level of occurrence of the variant in the set of chromosomes.'),
        terminology = terminologies.Zygosity,
        null = True, blank = True,
    )
    inheritance = termfields.CodedConceptField(
        verbose_name = _('Inheritance'),
        help_text = _('Variant inheritance origin (if known).'),
        terminology = terminologies.VariantInheritance,
        null = True, blank = True,
    )
    coordinate_system = termfields.CodedConceptField(
        verbose_name = _('Coordinate system'),
        help_text = _('Genomic coordinate system used for identifying nucleotides or amino acids within a sequence.'),
        terminology = terminologies.GenomicCoordinateSystem,
        null = True, blank = True,
    )
    clinvar = models.CharField(
        verbose_name = _('ClinVar accession number'),
        help_text = _('Accession number in the ClinVar variant database, given for cross-reference.'),
        null = True, blank = True,
    )
    
    class Meta:
        constraints = [
            CheckConstraint(
                condition=Q(dna_hgvs__isnull=True) | Q(dna_hgvs__regex=HGVSRegex.DNA_HGVS),
                name="valid_dna_hgvs",
                violation_error_message="DNA HGVS must be a valid 'c.'-HGVS expression.",
            ),
            CheckConstraint(
                condition=Q(rna_hgvs__isnull=True) | Q(rna_hgvs__regex=HGVSRegex.RNA_HGVS),
                name="valid_rna_hgvs",
                violation_error_message="RNA HGVS must be a valid 'r.'-HGVS expression.",
            ),
            CheckConstraint(
                condition=Q(protein_hgvs__isnull=True) | Q(protein_hgvs__regex=HGVSRegex.PROTEIN_HGVS),
                name="valid_protein_hgvs",
                violation_error_message="Protein HGVS must be a valid 'p.'-HGVS expression.",
            )
        ]
    
    @property
    def mutation_label(self):    
        if self.molecular_consequence:    
            if self.molecular_consequence.code == 'SO:0001911': # copy_number_increase
                return 'amplification'
            elif self.molecular_consequence.code == 'SO:0001912': # copy_number_decrease 
                return 'loss'
            elif self.molecular_consequence.code == 'SO:0001565': # gene_fusion
                return 'fusion'
            else:
                return self.molecular_consequence.display.lower().replace('_',' ')
        elif self.copy_number:
            return 'amplification' if self.copy_number > 2 else 'loss'
        elif self.protein_change_type:
            return self.protein_change_type
        else:
            return self.dna_change_type
    
    @property
    def genes_label(self):
        genes = self.genes.all()
        if len(genes)==1: 
            genes = genes.first().display 
        else: 
            genes = '-'.join([g.display for g in genes])
        return genes
    
    @property
    def aminoacid_change(self):
        if self.protein_hgvs:
            protein_change = ' ' + self.protein_hgvs.split(':p.')[-1]
            if "?" in protein_change: 
                return None
            return protein_change
        return None
        
    @property
    def description(self):
        significance = '(Pathogenic)' if self.is_pathogenic else '(VUS)' if self.is_vus else None
        return ' '.join([piece for piece in [self.genes_label, self.aminoacid_change, self.mutation_label, significance] if piece])
