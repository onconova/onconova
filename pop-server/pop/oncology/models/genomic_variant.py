
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
import enum 
from typing import Union
from django.contrib.postgres.aggregates import StringAgg
from django.db.models import Q, F, Func, CheckConstraint
from django.db.models.functions import Cast
from django.db.models.fields.json import KeyTextTransform

from queryable_properties.properties import AnnotationProperty, MappingProperty
from queryable_properties.managers import QueryablePropertiesManager

from pop.core.models import BaseModel 
from pop.oncology.models import PatientCase 
import pop.terminology.fields as termfields 
import pop.terminology.models as terminologies 
import re


HGVS_VARIANT_CHANGE_TYPE = (
    ('=', 'unchanged'),
    ('>', 'substitution'),
    ('delins', 'deletion-insertion'),
    ('dup', 'duplication'),
    ('ins', 'insertion'),
    ('del', 'deletion'),
    ('inv', 'inversion'),
    ('rpt', 'repetition'),
)

HGVS_PROTEIN_CHANGE_TYPE = (
    ('=', 'silent'),
    ('', 'missense'),
    ('delins', 'deletion-insertion'),
    ('dup', 'duplication'),
    ('ins', 'insertion'),
    ('del', 'deletion'),
    ('Ter', 'nonsense'),
    ('*', 'nonsense'),
    ('fs', 'frameshift'),
    ('fsTer', 'frameshift'),
    ('ext', 'extension'),
    ('extTer', 'extension'),
)

class HgvsMatchingGroup(str, enum.Enum): 
    VARIANT_TYPE = 'variant-type'
    SEQUENCE_IDENTIFIER = 'sequence-identifier'
    POSITION_RANGE = 'position-range'
    COORDINATE = 'coordinate'
    SEQUENCE = 'sequence'
    
class HGVSRegex:
    """ BASED ON v21.1.2 of HGVS"""

    AMINOACID = r"(?:Gly|Ala|Val|Leu|Ile|Met|Phe|Trp|Pro|Ser|Thr|Cys|Tyr|Asn|Gln|Asp|Glu|Lys|Arg|His)"

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
    COORDINATE = r"g|c|p|r"
    NUCLEOTIDE_UNCERTAIN_POSITION= r"(?:(?:\(\?_\d+\))|(?:\(\d+_\?\))|(?:\(\d+_\d+\)))"
    NUCLEOTIDE_POSITION = fr"(?:\d+|{NUCLEOTIDE_UNCERTAIN_POSITION})"
    NUCLEOTIDE_RANGE = fr"(?:{NUCLEOTIDE_POSITION}_{NUCLEOTIDE_POSITION})"
    NUCLEOTIDE_POSITION_OR_RANGE = fr"(?:{NUCLEOTIDE_POSITION}|{NUCLEOTIDE_RANGE})"
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
    PROTEIN_SEQUENCE = rf"{AMINOACID}+"
    

    class DNAMatchGroup(enum.Enum):
        REFSEQ = 1
        POSITION_OR_RANGE = 2
        REFERENCE_SEQUENCE = 3
        VARIANT_TYPE = 4
        ALTERNATE_SEQUENCE = 5

    class ProteinMatchGroup(enum.Enum):
        REFSEQ = 1
        POSITION_OR_RANGE = 2
        VARIANT_TYPE = 3
        ALTERNATE_SEQUENCE = 4
        
    @classmethod
    def construct_genomic_hgvs_regex(cls):
        return rf'({cls.GENOMIC_REFSEQ}):g\.({cls.NUCLEOTIDE_POSITION_OR_RANGE})({cls.DNA_SEQUENCE})?({cls.DNA_VARIANT_TYPE})({cls.DNA_SEQUENCE})?'

    @classmethod
    def construct_rna_hgvs_regex(cls):
        return rf'({cls.RNA_REFSEQ}):r\.({cls.NUCLEOTIDE_POSITION_OR_RANGE})({cls.RNA_SEQUENCE})?({cls.RNA_VARIANT_TYPE})({cls.RNA_SEQUENCE})?'

    @classmethod
    def construct_dna_hgvs_regex(cls):
        return rf'(?:{cls.GENOMIC_REFSEQ})?\(?({cls.RNA_REFSEQ})\)?:c\.({cls.NUCLEOTIDE_POSITION_OR_RANGE})({cls.DNA_SEQUENCE})?({cls.DNA_VARIANT_TYPE})({cls.DNA_SEQUENCE})?'

    @classmethod
    def construct_protein_hgvs_regex(cls):
        print( rf'({cls.PROTEIN_REFSEQ}):p\.\(?({cls.AMINOACID_POSITION_OR_RANGE})?(?:{cls.PROTEIN_SEQUENCE})?({cls.PROTEIN_VARIANT_TYPE})({cls.PROTEIN_SEQUENCE})?\)?(?:\d+)?')
        return rf'({cls.PROTEIN_REFSEQ}):p\.\(?({cls.AMINOACID_POSITION_OR_RANGE})(?:{cls.PROTEIN_SEQUENCE})?({cls.PROTEIN_VARIANT_TYPE})({cls.PROTEIN_SEQUENCE})?\)?(?:\d+)?'


class MatchHgvsProperty(Func):
    """
    Extracts the nth matching group from an HGVS expression using PostgreSQL's `regexp_match()`.
    
    :param expression: The database column containing the HGVS string.
    :param group: The group to capture.
    :param group_index: The index of the capturing group to extract (1-based).
    """
    function = 'regexp_match'

    def __init__(self, molecule_type, group=Union[HGVSRegex.DNAMatchGroup, HGVSRegex.ProteinMatchGroup], **extra):
        # PostgreSQL regexp_match() returns an array, so we extract the nth element
        template = "(%(function)s(%(expressions)s, '%(regex)s'))[%(group)s]"

        if molecule_type == 'genomic':
            expression = F('genomic_hgvs')
            hgvs_regex = HGVSRegex.construct_genomic_hgvs_regex() 
        elif molecule_type == 'dna':
            expression = F('dna_hgvs')
            hgvs_regex = HGVSRegex.construct_dna_hgvs_regex() 
        elif molecule_type == 'rna':
            expression = F('rna_hgvs')
            hgvs_regex = HGVSRegex.construct_rna_hgvs_regex() 
        elif molecule_type == 'protein':
            expression = F('protein_hgvs')
            hgvs_regex = HGVSRegex.construct_protein_hgvs_regex() 
        else:
            raise KeyError(f'Unsupported HGVS molecule type: "{molecule_type}"')
        
        super().__init__(
            expression,
            regex=hgvs_regex,
            template=template,
            group=group.value,  # 1-based index in PostgreSQL arrays
            **extra
        )

    
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
    genomic_hgvs = models.CharField(
        verbose_name=_('HGVS genomic-level expression'),
        help_text=_("Description of the genomic sequence change using a valid HGVS-formatted expression, e.g. NC_000016.9:g.2124200_2138612dup"),
        max_length=500,
        null=True, blank=True,
        validators=[RegexValidator(HGVSRegex.construct_genomic_hgvs_regex(), "The string should be a valid genomic HGVS expression.")],
    )
    genomic_reference_sequence = AnnotationProperty(
        verbose_name = _('Genomic HGVS RefSeq'),
        annotation = MatchHgvsProperty('genomic', HGVSRegex.DNAMatchGroup.REFSEQ),
    )
    genomic_change_position = AnnotationProperty(
        verbose_name = _('Genomic change position'),
        annotation = MatchHgvsProperty('genomic', HGVSRegex.DNAMatchGroup.POSITION_OR_RANGE),
    )    
    _genomic_hgvs_change_type = AnnotationProperty(
        annotation = MatchHgvsProperty('genomic', HGVSRegex.DNAMatchGroup.VARIANT_TYPE),
    )
    genomic_change_type = MappingProperty(
        verbose_name = _('Genomic change type'),
        attribute_path = '_genomic_hgvs_change_type',
        mappings=HGVS_VARIANT_CHANGE_TYPE,
        default=None,
        output_field=models.CharField(choices=HGVS_VARIANT_CHANGE_TYPE)
    )    

    
    dna_hgvs = models.CharField(
        verbose_name=_('HGVS DNA-level expression'),
        help_text=_("Description of the coding (cDNA) sequence change using a valid HGVS-formatted expression, e.g. NM_005228.5:c.2369C>T"),
        max_length=500,
        null=True, blank=True,
        validators=[RegexValidator(HGVSRegex.construct_dna_hgvs_regex(), "The string should be a valid DNA HGVS expression.")],
    )
    dna_reference_sequence = AnnotationProperty(
        verbose_name = _('Coding HGVS RefSeq'),
        annotation = MatchHgvsProperty('dna', HGVSRegex.DNAMatchGroup.REFSEQ),
    )
    dna_change_position = AnnotationProperty(
        verbose_name = _('DNA change position'),
        annotation = MatchHgvsProperty('dna', HGVSRegex.DNAMatchGroup.POSITION_OR_RANGE),
    )    
    _dna_hgvs_change_type = AnnotationProperty(
        annotation = MatchHgvsProperty('dna', HGVSRegex.DNAMatchGroup.VARIANT_TYPE),
    )
    dna_change_type = MappingProperty(
        verbose_name = _('DNA change type'),
        attribute_path = '_dna_hgvs_change_type',
        mappings=HGVS_VARIANT_CHANGE_TYPE,
        default=None,
        output_field=models.CharField(choices=HGVS_VARIANT_CHANGE_TYPE)
    )    

    rna_hgvs = models.CharField(
        verbose_name=_('HGVS RNA-level expression'),
        help_text=_("Description of the RNA sequence change using a valid HGVS-formatted expression, e.g. NM_000016.9:r.1212a>c"),
        max_length=500,
        null=True, blank=True,
        validators=[RegexValidator(HGVSRegex.construct_rna_hgvs_regex(), "The string should be a valid RNA HGVS expression.")],
    )
    rna_reference_sequence = AnnotationProperty(
        verbose_name = _('RNA HGVS RefSeq'),
        annotation = MatchHgvsProperty('rna', HGVSRegex.DNAMatchGroup.REFSEQ),
    )
    rna_change_position = AnnotationProperty(
        verbose_name = _('RNA change position'),
        annotation = MatchHgvsProperty('rna', HGVSRegex.DNAMatchGroup.POSITION_OR_RANGE),
    )    
    _rna_hgvs_change_type = AnnotationProperty(
        annotation = MatchHgvsProperty('rna', HGVSRegex.DNAMatchGroup.VARIANT_TYPE),
    )
    rna_change_type = MappingProperty(
        verbose_name = _('RNA change type'),
        attribute_path = '_rna_hgvs_change_type',
        mappings=HGVS_VARIANT_CHANGE_TYPE,
        default=None,
        output_field=models.CharField(choices=HGVS_VARIANT_CHANGE_TYPE)
    )    

    protein_hgvs = models.CharField(
        verbose_name=_('HGVS protein-level expression'),
        help_text=_("Description of the amino-acid sequence change using a valid HGVS-formatted expression, e.g. NP_000016.9:p.Leu24Tyr"),
        max_length=500,
        null=True, blank=True,
        validators=[RegexValidator(HGVSRegex.construct_protein_hgvs_regex(), "The string should be a valid protein HGVS expression.")],
    )
    protein_reference_sequence = AnnotationProperty(
        verbose_name = _('Protein HGVS RefSeq'),
        annotation = MatchHgvsProperty('protein', HGVSRegex.ProteinMatchGroup.REFSEQ),
    )
    protein_change_position = AnnotationProperty(
        verbose_name = _('Protein change position'),
        annotation = MatchHgvsProperty('protein', HGVSRegex.ProteinMatchGroup.POSITION_OR_RANGE),
    )    
    _protein_hgvs_change_type = AnnotationProperty(
        annotation = MatchHgvsProperty('protein', HGVSRegex.ProteinMatchGroup.VARIANT_TYPE),
    )
    protein_change_type = MappingProperty(
        verbose_name = _('Protein change type'),
        attribute_path = '_protein_hgvs_change_type',
        mappings=HGVS_PROTEIN_CHANGE_TYPE,
        default=None,
        output_field=models.CharField(choices=HGVS_PROTEIN_CHANGE_TYPE)
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
                condition=Q(genomic_hgvs__isnull=True) | Q(genomic_hgvs__regex=HGVSRegex.construct_genomic_hgvs_regex()),
                name="valid_genomic_hgvs",
                violation_error_message="Genomic HGVS must be a valid 'g.'-HGVS expression.",
            ),
            CheckConstraint(
                condition=Q(dna_hgvs__isnull=True) | Q(dna_hgvs__regex=HGVSRegex.construct_dna_hgvs_regex()),
                name="valid_dna_hgvs",
                violation_error_message="DNA HGVS must be a valid 'c.'-HGVS expression.",
            ),
            CheckConstraint(
                condition=Q(rna_hgvs__isnull=True) | Q(rna_hgvs__regex=HGVSRegex.construct_rna_hgvs_regex()),
                name="valid_rna_hgvs",
                violation_error_message="RNA HGVS must be a valid 'r.'-HGVS expression.",
            ),
            CheckConstraint(
                condition=Q(protein_hgvs__isnull=True) | Q(protein_hgvs__regex=HGVSRegex.construct_protein_hgvs_regex()),
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
            if self.copy_number > 2:
                return 'amplification'
            if self.copy_number < 2:
                return 'loss'
            else:
                return self.dna_change_type
        elif self.aminoacid_change_type:
            return self.aminoacid_change_type.display.lower()
        else:
            return None
    
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
        if self.is_pathogenic:
            significance_label = '(Pathogenic)'
        elif self.is_vus:
            significance_label = '(VUS)'
        else:
            significance_label = None   
        return ' '.join([piece for piece in [self.genes_label, self.aminoacid_change, self.mutation_label, significance_label] if piece])
