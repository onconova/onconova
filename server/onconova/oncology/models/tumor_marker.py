from enum import Enum
from typing import List

import pghistory
from django.db import models
from django.utils.translation import gettext_lazy as _
from pydantic import BaseModel as PydanticBaseModel

import onconova.core.measures as measures
import onconova.terminology.fields as termfields
import onconova.terminology.models as terminologies
from onconova.core.measures.fields import MeasurementField
from onconova.core.models import BaseModel
from onconova.oncology.models import NeoplasticEntity, PatientCase


class TumorMarkerPresenceChoices(models.TextChoices):
    """
    An enumeration representing the possible presence states of an analyte in a tumor marker test.

    Attributes:
        POSITIVE: Indicates the analyte is present.
        NEGATIVE: Indicates the analyte is absent.
        INDETERMINATE: Indicates the presence of the analyte could not be determined.
    """
    POSITIVE = "positive"
    NEGATIVE = "negative"
    INDETERMINATE = "indeterminate"


class TumorMarkerNuclearExpressionStatusChoices(models.TextChoices):
    """
    An enumeration representing the status of nuclear expression for a tumor marker.

    Attributes:
        INTACT (str): Indicates that nuclear expression is intact.
        LOSS (str): Indicates a loss of nuclear expression.
        INDETERMINATE (str): Indicates that the nuclear expression status is indeterminate.
    """
    INTACT = "intact"
    LOSS = "loss"
    INDETERMINATE = "indeterminate"


class TumorMarkerTumorProportionScoreChoices(models.TextChoices):
    """
    An enumeration representing tumor proportion score categories.
    
    Attributes:
        TP0: Tumor proportion score 0.
        TC1: Tumor proportion score 1.
        TC2: Tumor proportion score 2.
        TC3: Tumor proportion score 3.
    """
    TP0 = "TC0"
    TC1 = "TC1"
    TC2 = "TC2"
    TC3 = "TC3"


class TumorMarkerImmuneCellScoreChoices(models.TextChoices):
    """
    Enumeration representing immune cell scores for tumor markers.

    Attributes:
        IC0: Immune cell score 0.
        IC1: Immune cell score 1.
        IC2: Immune cell score 2.
        IC3: Immune cell score 3.
    """
    IC0 = "IC0"
    IC1 = "IC1"
    IC2 = "IC2"
    IC3 = "IC3"


class TumorMarkerImmunohistochemicalScoreChoices(models.TextChoices):
    """
    An enumeration representing possible immunohistochemical scoring values for tumor markers.

    Attributes:
        ZERO (str): Score of "0", indicating no detectable staining.
        ONE (str): Score of "1+", indicating weak staining.
        TWO (str): Score of "2+", indicating moderate staining.
        THREE (str): Score of "3+", indicating strong staining.
        INDETERMINATE (str): Score of "indeterminate", indicating that the result cannot be determined.
    """
    ZERO = "0"
    ONE = "1+"
    TWO = "2+"
    THREE = "3+"
    INDETERMINATE = "indeterminate"


@pghistory.track()
class TumorMarker(BaseModel):
    """
    Represents a tumor marker result associated with a patient case.

    Attributes:
        case (models.ForeignKey[PatientCase]): Reference to the related patient case.
        date (models.DateField): Date when the tumor marker was analyzed.
        related_entities (models.ManyToManyField[NeoplasticEntity]): Neoplastic entities related to the tumor marker analysis.
        analyte (termfields.CodedConceptField[terminologies.TumorMarkerAnalyte]): The chemical or biological substance/agent analyzed.
        mass_concentration (MeasurementField[measures.MassConcentration]): Mass concentration of the analyte (optional).
        arbitrary_concentration (MeasurementField[measures.ArbitraryConcentration]): Arbitrary concentration of the analyte (optional).
        substance_concentration (MeasurementField[measures.SubstanceConcentration]): Substance concentration of the analyte (optional).
        fraction (MeasurementField[measures.Fraction]): Analyte fraction (optional).
        multiple_of_median (MeasurementField[measures.MultipleOfMedian]): Multiples of the median analyte (optional).
        tumor_proportion_score (models.CharField[TumorMarkerTumorProportionScoreChoices]): Tumor proportion score (TPS) for PD-L1 expression (optional).
        immune_cell_score (models.CharField[TumorMarkerImmuneCellScoreChoices]): Immune cell score (ICS) for PD-L1 positive immune cells (optional).
        combined_positive_score (MeasurementField[measures.Fraction]): Combined positive score (CPS) for PD-L1 (optional).
        immunohistochemical_score (models.CharField[TumorMarkerImmunohistochemicalScoreChoices]): Immunohistochemical score for analyte-positive cells (optional).
        presence (models.CharField[TumorMarkerPresenceChoices]): Indicates if the analyte tested positive or negative (optional).
        nuclear_expression_status (models.CharField[TumorMarkerNuclearExpressionStatusChoices]): Status of nuclear expression of the analyte (optional).
        value (str): Returns a string representation of the first available value among the measurement and score fields.
        description (str): Returns a human-readable description combining the analyte and its value.

    Constraints: 
        Ensures at least one value field is set for each tumor marker instance.
    """

    case = models.ForeignKey(
        verbose_name=_("Patient case"),
        help_text=_(
            "Indicates the case of the patient related to the tumor marker result"
        ),
        to=PatientCase,
        related_name="tumor_markers",
        on_delete=models.CASCADE,
    )
    date = models.DateField(
        verbose_name=_("Date"),
        help_text=_("Clinically-relevant date at which the tumor marker was analyzed."),
    )
    related_entities = models.ManyToManyField(
        verbose_name=_("Related neoplastic entities"),
        help_text=_(
            "References to the neoplastic entities that are related or the focus of the tumor marker analysis."
        ),
        to=NeoplasticEntity,
        related_name="tumor_markers",
    )
    analyte = termfields.CodedConceptField(
        verbose_name=_("Analyte"),
        help_text=_("The chemical or biological substance/agent that is analyzed."),
        terminology=terminologies.TumorMarkerAnalyte,
    )
    mass_concentration = MeasurementField(
        verbose_name=_("Mass concentration"),
        help_text=_("Mass concentration of the analyte (if revelant/measured)"),
        measurement=measures.MassConcentration,
        null=True,
        blank=True,
    )
    arbitrary_concentration = MeasurementField(
        verbose_name=_("Arbitrary concentration"),
        help_text=_("Arbitrary concentration of the analyte (if revelant/measured)"),
        measurement=measures.ArbitraryConcentration,
        default_unit="kIU__l",
        null=True,
        blank=True,
    )
    substance_concentration = MeasurementField(
        verbose_name=_("Substance concentration"),
        help_text=_("Substance concentration of the analyte (if revelant/measured)"),
        measurement=measures.SubstanceConcentration,
        null=True,
        blank=True,
    )
    fraction = MeasurementField(
        verbose_name=_("Fraction"),
        help_text=_("Analyte fraction (if revelant/measured)"),
        measurement=measures.Fraction,
        null=True,
        blank=True,
    )
    multiple_of_median = MeasurementField(
        verbose_name=_("Multiples of the median"),
        help_text=_("Multiples of the median analyte (if revelant/measured)"),
        measurement=measures.MultipleOfMedian,
        null=True,
        blank=True,
    )
    tumor_proportion_score = models.CharField(
        verbose_name=_("Immune Cells Score (ICS)"),
        help_text=_(
            "Categorization of the percentage of cells in a tumor that express PD-L1"
        ),
        choices=TumorMarkerTumorProportionScoreChoices,
        max_length=50,
        null=True,
        blank=True,
    )
    immune_cell_score = models.CharField(
        verbose_name=_("Immune Cells Score (ICS)"),
        help_text=_("Categorization of the percentage of PD-L1 positive immune cells"),
        choices=TumorMarkerImmuneCellScoreChoices,
        max_length=50,
        null=True,
        blank=True,
    )
    combined_positive_score = MeasurementField(
        verbose_name=_("Combined Positive Score (CPS)"),
        help_text=_(
            "The number of PD-L1 positive cells, including tumor cells, lymphocytes, and macrophages divided by the total number of viable tumor cells multiplied by 100"
        ),
        measurement=measures.Fraction,
        null=True,
        blank=True,
    )
    immunohistochemical_score = models.CharField(
        verbose_name=_("Immunohistochemical Score"),
        help_text=_(
            "Categorization of the number of analyte-positive cells in a sample"
        ),
        choices=TumorMarkerImmunohistochemicalScoreChoices,
        max_length=50,
        null=True,
        blank=True,
    )
    presence = models.CharField(
        verbose_name=_("Presence"),
        help_text=_("Whether an analyte has tested positive or negative."),
        choices=TumorMarkerPresenceChoices,
        max_length=50,
        null=True,
        blank=True,
    )
    nuclear_expression_status = models.CharField(
        verbose_name=_("Nuclear expression status"),
        help_text=_("Categorization of the status of expression of the analyte"),
        choices=TumorMarkerNuclearExpressionStatusChoices,
        max_length=50,
        null=True,
        blank=True,
    )

    @property
    def value(self):
        return str(
            self.mass_concentration
            or self.arbitrary_concentration
            or self.substance_concentration
            or self.fraction
            or self.multiple_of_median
            or self.tumor_proportion_score
            or self.immune_cell_score
            or self.combined_positive_score
            or self.immunohistochemical_score
            or self.presence
            or self.nuclear_expression_status
        )

    @property
    def description(self):
        if analyte_data := ANALYTES_DATA.get(self.analyte.code):
            analyte = analyte_data.acronym
        else:
            analyte = str(self.analyte)
        return f"{analyte}: {self.value}"

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(mass_concentration__isnull=False)
                | models.Q(arbitrary_concentration__isnull=False)
                | models.Q(substance_concentration__isnull=False)
                | models.Q(fraction__isnull=False)
                | models.Q(multiple_of_median__isnull=False)
                | models.Q(tumor_proportion_score__isnull=False)
                | models.Q(immune_cell_score__isnull=False)
                | models.Q(combined_positive_score__isnull=False)
                | models.Q(immunohistochemical_score__isnull=False)
                | models.Q(presence__isnull=False)
                | models.Q(nuclear_expression_status__isnull=False),
                name="tumor marker must at least have one value",
            ),
            # models.CheckConstraint(
            #     condition = ~models.Q(analyte='PD-L1 ICS') |
            #                 (models.Q(analyte='PD-L1 ICS') & models.Q(classification__in=IMMUNE_CELL_SCORES)),
            #     name='PD-L1 ICS can only have ICS classification'
            # ),
            # models.CheckConstraint(
            #     condition = ~models.Q(analyte='PD-L1 TPS') |
            #                 (models.Q(analyte='PD-L1 TPS') & models.Q(classification__in=TUMOR_PROPORTION_SCORES)),
            #     name='PD-L1 TPS can only have TPS classification'
            # )
        ]


class AnalyteResultType(Enum):
    """
    Enum representing the various types of analyte results that can be reported for tumor markers.

    Members:
        mass_concentration: Quantitative measurement of mass per unit volume (e.g., ng/mL).
        arbitary_concentration: Measurement based on arbitrary units, often used when no standard exists.
        substance_concentration: Quantitative measurement of substance amount per unit volume (e.g., mol/L).
        multiple_of_median: Value expressed as a multiple of the median value in a reference population.
        fraction: Proportion or percentage of a particular analyte present.
        presence: Indicates the presence or absence of the analyte.
        combined_positive_score: Composite score reflecting combined positivity of multiple markers.
        immmune_cells_score: Score representing the presence or activity of immune cells.
        tumor_proportion_score: Score indicating the proportion of tumor cells expressing a marker.
        immunohistochemical_score: Score derived from immunohistochemical staining results.
        nuclear_expression_status: Status indicating expression of a marker in the cell nucleus.
    """
    mass_concentration = "MassConcentration"
    arbitary_concentration = "ArbitraryConcentration"
    substance_concentration = "SubstanceConcentration"
    multiple_of_median = "MultipleOfMedian"
    fraction = "Fraction"
    presence = "Presence"
    combined_positive_score = "CombinedPositiveScore"
    immmune_cells_score = "ImmuneCellsScore"
    tumor_proportion_score = "TumorProportionScore"
    immunohistochemical_score = "ImmunoHistoChemicalScore"
    nuclear_expression_status = "NuclearExpressionStatus"


class AnalyteDetails(PydanticBaseModel):
    """
    Represents details about a tumor marker analyte.

    Attributes:
        acronym (str): The acronym or short name for the analyte.
        display (str): The display name or description of the analyte.
        valueTypes (List[AnalyteResultType]): List of possible result types for the analyte.
    """
    acronym: str
    display: str
    valueTypes: List[AnalyteResultType]

"""Structure containing details on tumor marker analytes"""
ANALYTES_DATA = {
    "LP28643-2": AnalyteDetails(
        acronym="CEA",
        display="Carcinoembryonic Antigen",
        valueTypes=[
            AnalyteResultType.mass_concentration,
            AnalyteResultType.arbitary_concentration,
            AnalyteResultType.substance_concentration,
        ],
    ),
    "LP14543-0": AnalyteDetails(
        acronym="CA125",
        display="Cancer Antigen 125",
        valueTypes=[AnalyteResultType.arbitary_concentration],
    ),
    "LP15461-4": AnalyteDetails(
        acronym="CA15-3",
        display="Cancer Antigen 15-3",
        valueTypes=[AnalyteResultType.arbitary_concentration],
    ),
    "LP14040-7": AnalyteDetails(
        acronym="CA19-9",
        display="Cancer Antigen 19-9",
        valueTypes=[AnalyteResultType.arbitary_concentration],
    ),
    "LP15463-0": AnalyteDetails(
        acronym="CA242",
        display="Cancer Antigen 242",
        valueTypes=[AnalyteResultType.arbitary_concentration],
    ),
    "LP15464-8": AnalyteDetails(
        acronym="CA27-29",
        display="Cancer Antigen 27-29",
        valueTypes=[AnalyteResultType.arbitary_concentration],
    ),
    "LP15465-5": AnalyteDetails(
        acronym="CA50",
        display="Cancer Antigen 50",
        valueTypes=[AnalyteResultType.arbitary_concentration],
    ),
    "LP15466-3": AnalyteDetails(
        acronym="CA549",
        display="Cancer Antigen 549",
        valueTypes=[AnalyteResultType.arbitary_concentration],
    ),
    "LP15467-1": AnalyteDetails(
        acronym="CA72-4",
        display="Cancer Antigen 72-4",
        valueTypes=[AnalyteResultType.arbitary_concentration],
    ),
    "LP18274-8": AnalyteDetails(
        acronym="CA DM/70K",
        display="Cancer Antigen DM/70K",
        valueTypes=[AnalyteResultType.arbitary_concentration],
    ),
    "LP28642-4": AnalyteDetails(
        acronym="CASA",
        display="Cancer-associated Serum Ag",
        valueTypes=[AnalyteResultType.arbitary_concentration],
    ),
    "LP135291-5": AnalyteDetails(
        acronym="CTC",
        display="Circulating tumor cells",
        valueTypes=[AnalyteResultType.arbitary_concentration],
    ),
    "LP63010-0": AnalyteDetails(
        acronym="FGF",
        display="Fibroblast growth factor",
        valueTypes=[
            AnalyteResultType.mass_concentration,
            AnalyteResultType.arbitary_concentration,
            AnalyteResultType.substance_concentration,
        ],
    ),
    "LP420752-0": AnalyteDetails(
        acronym="GRP",
        display="Gastrin releasing polypeptide prohormone",
        valueTypes=[
            AnalyteResultType.mass_concentration,
        ],
    ),
    "LP89249-4": AnalyteDetails(
        acronym="TNFBP1",
        display="Tumor necrosis factor binding protein 1",
        valueTypes=[AnalyteResultType.arbitary_concentration],
    ),
    "LP62856-7": AnalyteDetails(
        acronym="YKL-40",
        display="Chitinase-3-like protein 1",
        valueTypes=[AnalyteResultType.mass_concentration],
    ),
    "LP38032-6": AnalyteDetails(
        acronym="NSE",
        display="Neuron-specific enolase",
        valueTypes=[
            AnalyteResultType.mass_concentration,
            AnalyteResultType.arbitary_concentration,
        ],
    ),
    "LP15033-1": AnalyteDetails(
        acronym="LDH",
        display="Lactate dehydrogenase",
        valueTypes=[
            AnalyteResultType.arbitary_concentration,
        ],
    ),
    "LP14652-9": AnalyteDetails(
        acronym="CgA",
        display="Chromogranin A",
        valueTypes=[
            AnalyteResultType.mass_concentration,
            AnalyteResultType.substance_concentration,
        ],
    ),
    "LP57672-5": AnalyteDetails(
        acronym="S100B",
        display="S100 calcium binding protein B",
        valueTypes=[AnalyteResultType.mass_concentration],
    ),
    "LP18193-0": AnalyteDetails(
        acronym="PSA",
        display="Prostate specific Ag",
        valueTypes=[
            AnalyteResultType.mass_concentration,
            AnalyteResultType.arbitary_concentration,
            AnalyteResultType.substance_concentration,
        ],
    ),
    "LP14331-0": AnalyteDetails(
        acronym="AFP",
        display="Alpha-1-Fetoprotein",
        valueTypes=[
            AnalyteResultType.mass_concentration,
            AnalyteResultType.arbitary_concentration,
            AnalyteResultType.substance_concentration,
        ],
    ),
    "LP14329-4": AnalyteDetails(
        acronym="β-hCG",
        display="Choriogonadotropin subunit β",
        valueTypes=[
            AnalyteResultType.mass_concentration,
            AnalyteResultType.arbitary_concentration,
            AnalyteResultType.substance_concentration,
            AnalyteResultType.multiple_of_median,
        ],
    ),
    "LP19423-0": AnalyteDetails(
        acronym="CYFRA 21-1",
        display="Cytokeratin 19 Fragment",
        valueTypes=[
            AnalyteResultType.mass_concentration,
            AnalyteResultType.arbitary_concentration,
        ],
    ),
    "LP93517-8": AnalyteDetails(
        acronym="HE4",
        display="Human epididymis protein 4",
        valueTypes=[
            AnalyteResultType.mass_concentration,
            AnalyteResultType.substance_concentration,
        ],
    ),
    "LP15724-5": AnalyteDetails(
        acronym="Mel",
        display="Melanin",
        valueTypes=[
            AnalyteResultType.mass_concentration,
            AnalyteResultType.arbitary_concentration,
        ],
    ),
    "LP38066-4": AnalyteDetails(
        acronym="EBV Ab",
        display="Epstein Barr Virus Ab",
        valueTypes=[AnalyteResultType.arbitary_concentration],
    ),
    "LP220351-3": AnalyteDetails(
        acronym="PD-L1",
        display="Programmed cell death ligand 1",
        valueTypes=[
            AnalyteResultType.immmune_cells_score,
            AnalyteResultType.tumor_proportion_score,
            AnalyteResultType.combined_positive_score,
        ],
    ),
    "LP28442-9": AnalyteDetails(
        acronym="HER2",
        display="Human Epidermal Growth Factor Receptor 2",
        valueTypes=[
            AnalyteResultType.presence,
            AnalyteResultType.immunohistochemical_score,
        ],
    ),
    "LP18567-5": AnalyteDetails(
        acronym="ER",
        display="Estrogen receptor",
        valueTypes=[AnalyteResultType.fraction],
    ),
    "LP14902-8": AnalyteDetails(
        acronym="PR",
        display="Progesterone receptor",
        valueTypes=[AnalyteResultType.fraction],
    ),
    "LP68364-6": AnalyteDetails(
        acronym="AR",
        display="Androgen receptor",
        valueTypes=[AnalyteResultType.fraction],
    ),
    "LP39016-8": AnalyteDetails(
        acronym="Ki67",
        display="Ki-67 nuclear Ag",
        valueTypes=[AnalyteResultType.fraction],
    ),
    "LP420961-7": AnalyteDetails(
        acronym="MLH3",
        display="DNA mismatch repair protein MLH3",
        valueTypes=[AnalyteResultType.nuclear_expression_status],
    ),
    "LP212189-7": AnalyteDetails(
        acronym="MLH1",
        display="DNA mismatch repair protein MLH1",
        valueTypes=[AnalyteResultType.nuclear_expression_status],
    ),
    "LP212190-5": AnalyteDetails(
        acronym="MSH2",
        display="DNA mismatch repair protein MSH2",
        valueTypes=[AnalyteResultType.nuclear_expression_status],
    ),
    "LP420964-1": AnalyteDetails(
        acronym="MSH3",
        display="DNA mismatch repair protein MSH3",
        valueTypes=[AnalyteResultType.nuclear_expression_status],
    ),
    "LP212191-3": AnalyteDetails(
        acronym="MSH6",
        display="DNA mismatch repair protein MSH6",
        valueTypes=[AnalyteResultType.nuclear_expression_status],
    ),
    "LP212192-1": AnalyteDetails(
        acronym="PMS2",
        display="Mismatch repair endonuclease PMS2",
        valueTypes=[AnalyteResultType.nuclear_expression_status],
    ),
    "LP19646-6": AnalyteDetails(
        acronym="p16",
        display="Cyclin-dependent Kinase Inhibitor 2A",
        valueTypes=[AnalyteResultType.presence],
    ),
    "LP38570-5": AnalyteDetails(
        acronym="HPV DNA",
        display="Human papilloma virus DNA",
        valueTypes=[AnalyteResultType.presence],
    ),
    "LP38067-2": AnalyteDetails(
        acronym="EBV DNA",
        display="Epstein Barr Virus DNA",
        valueTypes=[
            AnalyteResultType.arbitary_concentration,
            AnalyteResultType.presence,
        ],
    ),
    "C17922": AnalyteDetails(
        acronym="SSTR2",
        display="Somatostatin Receptor Type 2",
        valueTypes=[AnalyteResultType.fraction],
    ),
}
