
from django.db import models
from django.utils.translation import gettext_lazy as _
import django.contrib.postgres.fields as postgres
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator

from pop.core.models import BaseModel 
from pop.oncology.models import PatientCase 
import pop.terminology.fields as termfields 
import pop.terminology.models as terminologies 
    
class GenomicVariant(BaseModel):

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
    chromosomes = termfields.CodedConceptField(
        verbose_name = _('Chromosome(s)'),
        help_text = _("Chromosome(s) affected by this variant"),
        terminology = terminologies.ChromosomeIdentifier,
        null = True, blank = True,
        multiple = True,        
    )
    cytogenetic_location = models.CharField(
        verbose_name = _('Cytogenetic location'),
        help_text=_('The genetic address of the variant specifying the relevant chromosomal region.'),
        max_length = 60,
        null = True, blank = True,
        validators = [RegexValidator(
            r"^(?:[1-9]|1[0-9]|2[0-2]|X|Y)([pq])(\d+)(\d+)(?:\.(\d+))?$", 
            "The string should be a valid cytogenetic location (chromosomal locus).")
        ],
    )
    genome_assembly_version = termfields.CodedConceptField(
        verbose_name = _('Genome assembly version'),
        help_text = _('The reference genome assembly versionused in this analysis.'),
        terminology = terminologies.ReferenceGenomeBuild,
        null = True, blank = True,
    )
    genomic_refseq = models.CharField(
        verbose_name = _('Genomic RefSeq'),
        help_text = _("""
            Identifier the transcript reference sequence, which includes transcribed and non transcribed stretches. 
            Can be an NCBI's RefSeq ('NC_...' or 'NG...'), and LRG ('LRG...')"""
        ),
        max_length = 200,
        validators = [RegexValidator(
            r"^(?:NG|NC|LRG|)(.*)$", 
            "The string should be a valid transcript RefSeq identifier.")
        ],
        null = True, blank = True,
    )
    transcript_refseq = models.CharField(
        verbose_name = _('Transcript RefSeq'),
        help_text = _("""
            Identifier the transcript reference sequence, which includes transcribed and non transcribed stretches. 
            Can be an NCBI's RefSeq ('NM_...' or 'NG...'), Ensembl ('ENST...'), and LRG ('LRG...' plus 't1' to indicate transcript)"""
        ),
        max_length = 200,
        validators = [RegexValidator(
            r"^(?:NM|NG|ENST|LRG|)(.*)$", 
            "The string should be a valid transcript RefSeq identifier.")
        ],
        null = True, blank = True,
    )
    coding_hgsv = models.CharField(
        verbose_name=_('Coding DNA change expression (cHGVS)'),
        help_text=_("Description of the coding (cDNA) sequence change using a valid HGVS-formatted expression, e.g. NM_005228.5:c.2369C>T"),
        max_length=500,
        null=True, blank=True,
        validators=[RegexValidator(
            r"^(.*):c\.(.*)$", 
            "The string should be a valid coding DNA HGVS expression.")
        ],
    )
    protein_hgsv = models.CharField(
        verbose_name=_('Protein/aminoacid change expression (pHGVS)'),
        help_text=_("Description of the protein (aminoacid) sequence change using a valid HGVS-formatted expression, e.g. NP_000050.2:p.(Asn1836Lys)"),
        max_length=500,
        null=True, blank=True,
        validators=[RegexValidator(
            r"^(.*):p\.(.*)$", 
            "The string should be a valid protein HGVS expression.")
        ],
    )
    genomic_hgsv = models.CharField(
        verbose_name=_('Genomic change expression (gHGVS)'),
        help_text=_("Description of the genomic (gDNA) sequence change using a valid HGVS-formatted expression, e.g. NC_000016.9:g.2124200_2138612dup"),
        max_length=500,
        null=True, blank=True,
        validators=[RegexValidator(
            r"^(.*):g\.(.*)$", 
            "The string should be a valid genomic HGVS expression.")
        ],
    )
    dna_change_type = termfields.CodedConceptField(
        verbose_name = _('Coding DNA change type'),
        help_text = _('Classification of the DNA change type of the variant.'),
        terminology = terminologies.DnaChangeType,
        null = True, blank = True,
    )
    aminoacid_change_type = termfields.CodedConceptField(
        verbose_name = _('Aminoacid change type'),
        help_text = _('Classification of the amino acid change type'),
        terminology = terminologies.AminoAcidChangeType,
        null = True, blank = True,
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
    exact_genomic_coordinates = postgres.BigIntegerRangeField(
        verbose_name = _('Exact genomic coordinates'),
        help_text = _('The exact integer-based genomic coordinates of the start and end of the variant region. "High" can be omitted for single nucleotide variants.'),
        null = True, blank = True,
    ) 
    inner_genomic_coordinates = postgres.BigIntegerRangeField(
        verbose_name = _('Inner genomic coordinates'),
        help_text = _('The genomic coordinates of the narrowest genomic range in which the variant might reside. Used when the exact boundaries of the variant are not clear.'),
        null = True, blank = True,
    ) 
    outer_genomic_coordinates = postgres.BigIntegerRangeField(
        verbose_name = _('Outer genomic coordinates'),
        help_text = _('The genomic coordinates of the widest genomic range in which the variant might reside. Used when the exact boundaries of the variant are not clear.'),
        null = True, blank = True,
    ) 
    clinvar = models.CharField(
        verbose_name = _('ClinVar accession number'),
        help_text = _('Accession number in the ClinVar variant database, given for cross-reference.'),
        null = True, blank = True,
    )
    
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
        elif self.dna_change_type:
            if self.dna_change_type.code == 'SO:0001742': # copy_number_gain
                return 'amplification'
            elif self.dna_change_type.code == 'SO:0001743': # copy_number_loss 
                return 'loss'
            else:
                return self.dna_change_type.display.lower()
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
        if self.protein_hgsv:
            protein_change = ' ' + self.protein_hgsv.split(':p.')[-1]
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
