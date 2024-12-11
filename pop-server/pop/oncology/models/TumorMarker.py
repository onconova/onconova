from django.db import models
from django.utils.translation import gettext_lazy as _

from django_measurement.models import MeasurementField

from pop.core.models import BaseModel 
from pop.oncology.models import PatientCase, NeoplasticEntity 
import pop.core.measures as measures


BLOOD_ANALYTES = [
    ('CEA',    'Carcinoembryonic Antigen'),
    ('CA19-9', 'Cancer Antigen 19-9'),
    ('CA125',  'Cancer Antigen 125'),
    ('CA15-3', 'Cancer Antigen 15-3'),
    ('CA72-4', 'Cancer Antigen 72-4'),
    ('CA27-29','Cancer Antigen 27-29'),
    ('NSE',    'Neuron-specific enolase'),
    ('LDH',    'Lactate dehydrogenase'),
    ('CgA',    'Chromogranin A'),
    ('S100A1', 'S100 Calcium-binding Protein A1'),
    ('S100B',  'S100 Calcium-binding Protein B'),
    ('PSA',    'Prostate-specific Ag'),
    ('AFP',    'Alpha-1-Fetoprotein'),
    ('β-hCG',  'Choriogonadotropin subunit β',),
    ('B2M',  'β-2 microglobulin',),
    ('CYFRA 21-1', 'Cytokeratin 19 Fragment'),
    ('EBV',    'Epstein Barr Virus Antibody'),
]
TISSUE_ANALYTES = [
    ('PD-L1 ICS', 'PDL1 Immune Cell Score'),
    ('PD-L1 TPS', 'PDL1 Tumor Proportion Score'),
    ('PD-L1 CPS', 'PDL1 Combined Positive Score'),
    ('HER2',  'Human Epidermal Growth Factor Receptor 2'),
    ('ER',    'Estrogen receptor'),
    ('PR',    'Progesterone receptor'),
    ('AR',    'Androgen receptor'),
    ('Ki67',  'Antigen Kiel 67'),
    ('SSTR2', 'Somatostatin Receptor Type 2'),
    ('MLH1',  'DNA mismatch repair protein MLH1'),
    ('MSH2',  'DNA mismatch repair protein MSH2'),
    ('MSH6',  'DNA mismatch repair protein MSH6'),
    ('PMS2',  'Mismatch repair endonuclease PMS2'),
    ('p16',   'Cyclin-dependent Kinase Inhibitor 2A'),
    ('EBV',   'Epstein Barr virus DNA'),
    ('HPV',   'Human papillomavirus'),
]
ANALYTE_PRESENCES = [
    ('positive', 'Positive'), 
    ('negative', 'Negative'),
    ('indeterminate', 'Indeterminate')
]
NUCLEAR_EXPRESSION_STATII = [
    ('intact', 'Intact'), 
    ('loss', 'Loss'), 
    ('indeterminate', 'Indeterminate'),
]
IMMUNE_CELL_SCORES = [
    ('IC0', 'IC0'),
    ('IC1', 'IC1'),
    ('IC2', 'IC2'),
    ('IC3', 'IC3'),
]
TUMOR_PROPORTION_SCORES = [
    ('TC0', 'TC0'),
    ('TC1', 'TC1'),
    ('TC2', 'TC2'),
    ('TC3', 'TC3'),
]
IHC_SCORES = [
    ('0', '0'),
    ('1+', '1+'),
    ('2+', '2+'),
    ('3+', '3+'),
    ('indeterminate', 'Indeterminate'),
]

class TumorMarker(BaseModel):

    case = models.ForeignKey(
        verbose_name = _('Patient case'),
        help_text = _('Indicates the case of the patient related to the tumor marker result'),
        to = PatientCase,
        related_name = 'tumor_markers',
        on_delete = models.CASCADE,
    )
    date = models.DateField(
        verbose_name = _('Date'),
        help_text=_('Clinically-relevant date at which the tumor marker was analyzed.'),
    ) 
    related_entities = models.ManyToManyField(
        verbose_name = _('Related neoplastic entities'),
        help_text = _('References to the neoplastic entities that are related or the focus of the tumor marker analysis.'),
        to = NeoplasticEntity,
        related_name = 'tumor_markers',
    )
    analyte = models.CharField(
        verbose_name = _('Analyte'),
        help_text = _('The chemical or biological substance/agent that is analyzed.'),
        max_length = 50,
        choices = BLOOD_ANALYTES + TISSUE_ANALYTES,
    )
    mass_concentration = MeasurementField(
        verbose_name= _('Mass concentration'),
        help_text = _('Mass concentration of the analyte (if revelant/measured)'),
        measurement = measures.MassConcentration,
        null=True, blank=True,
    )
    arbitrary_concentration = MeasurementField(
        verbose_name= _('Arbitrary concentration'),
        help_text = _('Arbitrary concentration of the analyte (if revelant/measured)'),
        measurement = measures.ArbitraryConcentration,
        null=True, blank=True,
    )
    substance_concentration = MeasurementField(
        verbose_name= _('Substance concentration'),
        help_text = _('Substance concentration of the analyte (if revelant/measured)'),
        measurement = measures.SubstanceConcentration,
        null=True, blank=True,
    )
    fraction = MeasurementField(
        verbose_name= _('Fraction'),
        help_text = _('Analyte fraction (if revelant/measured)'),
        measurement = measures.Fraction,
        null=True, blank=True,
    )
    multiple_of_median = MeasurementField(
        verbose_name= _('Multiples of the median'),
        help_text = _('Multiples of the median analyte (if revelant/measured)'),
        measurement = measures.MultipleOfMedian,
        null=True, blank=True,
    )
    classification = models.CharField(
        verbose_name = _('Classification'),
        help_text = _('Qualitative classification of the analyte'),
        max_length = 50,
        choices = ANALYTE_PRESENCES \
                + NUCLEAR_EXPRESSION_STATII \
                + IMMUNE_CELL_SCORES \
                + TUMOR_PROPORTION_SCORES \
                + IHC_SCORES,
        null=True, blank=True,
    )
    
    @property
    def value(self):
        return str(
            self.mass_concentration \
            or self.arbitrary_concentration \
            or self.substance_concentration \
            or self.fraction \
            or self.multiple_of_median \
            or self.classification \
        ) 
    
    @property
    def description(self):
        return f'{self.analyte}: {self.value}'
    
    class Meta:
        constraints = [
            models.CheckConstraint(
                condition = models.Q(mass_concentration__isnull=False) |
                            models.Q(arbitrary_concentration__isnull=False) |
                            models.Q(substance_concentration__isnull=False) |
                            models.Q(fraction__isnull=False) |
                            models.Q(multiple_of_median__isnull=False) |
                            models.Q(classification__isnull=False),
                name = 'tumor marker must at least have one value'
            ),
            models.CheckConstraint(
                condition = ~models.Q(analyte='PD-L1 ICS') | 
                            (models.Q(analyte='PD-L1 ICS') & models.Q(classification__in=IMMUNE_CELL_SCORES)),
                name='PD-L1 ICS can only have ICS classification'
            ),
            models.CheckConstraint(
                condition = ~models.Q(analyte='PD-L1 TPS') | 
                            (models.Q(analyte='PD-L1 TPS') & models.Q(classification__in=TUMOR_PROPORTION_SCORES)),
                name='PD-L1 TPS can only have TPS classification'
            )
        ]