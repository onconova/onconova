from dataclasses import dataclass
from typing import Dict, List

import pghistory
from django.db import models
from django.db.models import Case, Sum, When
from django.utils.translation import gettext_lazy as _
from queryable_properties.managers import QueryablePropertiesManager
from queryable_properties.properties import AnnotationProperty

import onconova.terminology.fields as termfields
import onconova.terminology.models as terminologies
from onconova.core.models import BaseModel
from onconova.oncology.models import NeoplasticEntity, PatientCase


class ComorbiditiesAssessmentPanelChoices(models.TextChoices):
    """
    An enumeration of comorbidity panel types used in oncology models.

    Attributes:
        CHARLSON: Represents the Charlson comorbidity index panel.
        ELIXHAUSER: Represents the Elixhauser comorbidity index panel.
        NCI: Represents the National Cancer Institute (NCI) comorbidity index panel.
    """
    CHARLSON = "Charlson"
    ELIXHAUSER = "Elixhauser"
    NCI = "NCI"


@dataclass
class ComorbidityPanelCategory:
    """
    Represents a category within a comorbidity panel, including its label, default value, associated codes, and weight.

    Attributes:
        label (str): The display name of the comorbidity category.
        default (str): The default value or code for the category.
        codes (List[str]): A list of codes associated with this category.
        weight (int | float): The numerical weight assigned to this category.

    Methods:
        get_weight(codes: List[str]) -> int | float:
            Returns the weight of the category if any of the provided codes match the category's codes; otherwise, returns 0.
    """
    label: str
    default: str
    codes: List[str]
    weight: int | float

    def get_weight(self, codes: List[str]) -> int | float:
        return self.weight if any([code in codes for code in self.codes]) else 0


@dataclass
class ElixhauserPanelDetails:
    """
    This class defines the Elixhauser comorbidity index panel, mapping ICD codes to comorbidity categories and their respective weights.
    Each comorbidity is represented as a class attribute, instantiated as a `ComorbidityPanelCategory` with a label, default ICD code, a list of ICD codes, and a weight.

    References:
        - van Walraven al., Medical Care 47(6):p 626-633, June 2009.
        - Quan H et al., Medical Care 2005; 43(11):1130-1139.
    """

    chf = ComorbidityPanelCategory(
        label="Congestive heart failure",
        default="I50.0",
        codes=[
            "I09.9",
            "I11.0",
            "I13.0",
            "I13.2",
            "I25.5",
            "I42.0",
            "I42.5",
            "I42.6",
            "I42.7",
            "I42.8",
            "I42.9",
            "I43",
            "I50",
            "I50.0",
            "P29.0",
        ],
        weight=7,
    )
    carit = ComorbidityPanelCategory(
        label="Cardiac arrhythmias",
        default="I45.9",
        codes=[
            "I44.1",
            "I44.2",
            "I44.3",
            "I45.6",
            "I45.9",
            "I47",
            "I48",
            "I49",
            "R00.0",
            "R00.1",
            "R00.8",
            "T82.1",
            "Z45.0",
            "Z95.0",
        ],
        weight=5,
    )
    valv = ComorbidityPanelCategory(
        label="Valvular disease",
        default="I08.9",
        codes=[
            "A52.0",
            "I05",
            "I06",
            "I07",
            "I08",
            "I08.9",
            "I09.1",
            "I09.8",
            "I34",
            "I35",
            "I36",
            "I37",
            "I38",
            "I39",
            "Q23.0",
            "Q23.1",
            "Q23.2",
            "Q23.3",
            "Z95.2",
            "Z95.3",
            "Z95.4",
        ],
        weight=-1,
    )
    pcd = ComorbidityPanelCategory(
        label="Pulmonary circulation disorders",
        default="I28.9",
        codes=["I26", "I27", "I28.0", "I28.8", "I28.9"],
        weight=4,
    )
    pvd = ComorbidityPanelCategory(
        label="Peripheral vascular disorders",
        default="I73.9",
        codes=[
            "I70",
            "I71",
            "I731",
            "I738",
            "I73.9",
            "I77.1",
            "I79.0",
            "I79.2",
            "K55.1",
            "K55.8",
            "K55.9",
            "Z95.8",
            "Z95.9",
        ],
        weight=2,
    )
    hypunc = ComorbidityPanelCategory(
        label="Hypertension, uncomplicated",
        default="I10",
        codes=["I10"],
        weight=0,
    )
    hypc = ComorbidityPanelCategory(
        label="Hypertension, complicated",
        default="I15",
        codes=["I11", "I12", "I13", "I15"],
        weight=0,
    )
    para = ComorbidityPanelCategory(
        label="Paralysis",
        default="G83.9",
        codes=[
            "G04.1",
            "G11.4",
            "G80.1",
            "G80.2",
            "G81",
            "G82",
            "G83.0",
            "G83.1",
            "G83.2",
            "G83.3",
            "G83.4",
            "G83.9",
        ],
        weight=7,
    )
    ond = ComorbidityPanelCategory(
        label="Neurological disorders",
        default="G31.9",
        codes=[
            "G10",
            "G11",
            "G12",
            "G13",
            "G20",
            "G21",
            "G22",
            "G25.4",
            "G25.5",
            "G31.2",
            "G31.8",
            "G31.9",
            "G32",
            "G35",
            "G36",
            "G37",
            "G40",
            "G41",
            "G93.1",
            "G93.4",
            "R47.0",
            "R56",
        ],
        weight=6,
    )
    cpd = ComorbidityPanelCategory(
        label="Chronic pulmonary disease",
        default="J44.9",
        codes=[
            "I27.8",
            "I27.9",
            "J40",
            "J41",
            "J42",
            "J43",
            "J44",
            "J44.9",
            "J45",
            "J46",
            "J47",
            "J60",
            "J61",
            "J62",
            "J63",
            "J64",
            "J65",
            "J66",
            "J67",
            "J68.4",
            "J70.1",
            "J70.3",
        ],
        weight=3,
    )
    diabunc = ComorbidityPanelCategory(
        label="Diabetes, uncomplicated",
        default="E14.9",
        codes=[
            "E10.0",
            "E10.1",
            "E10.9",
            "E11.0",
            "E11.1",
            "E11.9",
            "E12.0",
            "E12.1",
            "E12.9",
            "E13.0",
            "E13.1",
            "E13.9",
            "E14.0",
            "E14.1",
            "E14.9",
        ],
        weight=0,
    )
    diabc = ComorbidityPanelCategory(
        label="Diabetes, complicated",
        default="E14.8",
        codes=[
            "E10.2",
            "E10.3",
            "E10.4",
            "E10.5",
            "E10.6",
            "E10.7",
            "E10.8",
            "E11.2",
            "E11.3",
            "E11.4",
            "E11.5",
            "E11.6",
            "E11.7",
            "E11.8",
            "E12.2",
            "E12.3",
            "E12.4",
            "E12.5",
            "E12.6",
            "E12.7",
            "E12.8",
            "E13.2",
            "E13.3",
            "E13.4",
            "E13.5",
            "E13.6",
            "E13.7",
            "E13.8",
            "E14.2",
            "E14.3",
            "E14.4",
            "E14.5",
            "E14.6",
            "E14.7",
            "E14.8",
        ],
        weight=0,
    )
    hypothy = ComorbidityPanelCategory(
        label="Hypothyroidism",
        default="E03.9",
        codes=["E00", "E01", "E02", "E03", "E03.9", "E89.0"],
        weight=0,
    )
    rf = ComorbidityPanelCategory(
        label="Renal failure",
        default="N19",
        codes=[
            "I12.0",
            "I13.1",
            "N18",
            "N19",
            "N25.0",
            "Z49.0",
            "Z49.1",
            "Z49.2",
            "Z94.0",
            "Z99.2",
        ],
        weight=5,
    )
    ld = ComorbidityPanelCategory(
        label="Liver disease",
        default="K76.9",
        codes=[
            "B18",
            "I85",
            "I86.4",
            "I98.2",
            "K70",
            "K71.1",
            "K71.3",
            "K71.4",
            "K71.5",
            "K71.7",
            "K72",
            "K73",
            "K74",
            "K76.0",
            "K76.2",
            "K76.3",
            "K76.4",
            "K76.5",
            "K76.6",
            "K76.7",
            "K76.8",
            "K76.9",
            "Z94.4",
        ],
        weight=11,
    )
    pud = ComorbidityPanelCategory(
        label="Peptic ulcer disease, excluding bleeding",
        default="K29",
        codes=[
            "K25.7",
            "K25.9",
            "K26.7",
            "K26.9",
            "K27.7",
            "K27.9",
            "K28.7",
            "K28.9",
            "K29",
        ],
        weight=0,
    )
    aids = ComorbidityPanelCategory(
        label="AIDS/HIV",
        default="B24",
        codes=["B20", "B21", "B22", "B24"],
        weight=0,
    )
    rheumd = ComorbidityPanelCategory(
        label="Rheumatoid arthritis/collaged vascular disease",
        default="M35.9",
        codes=[
            "L94.0",
            "L94.1",
            "L94.3",
            "M05",
            "M06",
            "M08",
            "M12.0",
            "M12.3",
            "M30",
            "M31.0",
            "M31.1",
            "M31.2",
            "M31.3",
            "M32",
            "M33",
            "M34",
            "M35",
            "M35.9",
            "M45",
            "M46.1",
            "M46.8",
            "M46.9",
        ],
        weight=0,
    )
    coag = ComorbidityPanelCategory(
        label="Coagulopathy",
        default="D68.9",
        codes=[
            "D65",
            "D66",
            "D67",
            "D68",
            "D68.9",
            "D69.1",
            "D69.3",
            "D69.4",
            "D69.5",
            "D69.6",
        ],
        weight=3,
    )
    obes = ComorbidityPanelCategory(
        label="Obesity",
        default="E66",
        codes=["E66"],
        weight=-4,
    )
    wloss = ComorbidityPanelCategory(
        label="Weight loss",
        default="R63.4",
        codes=["E40", "E41", "E42", "E43", "E44", "E45", "E46", "R63.4", "R64"],
        weight=6,
    )
    fed = ComorbidityPanelCategory(
        label="Fluid and electrolyte disorders",
        default="E87",
        codes=["E22.2", "E86", "E87"],
        weight=5,
    )
    blane = ComorbidityPanelCategory(
        label="Blood loss anaemia",
        default="D50.0",
        codes=["D50.0"],
        weight=-2,
    )
    dane = ComorbidityPanelCategory(
        label="Deficiency anaemia",
        default="D50.9",
        codes=["D50.8", "D50.9", "D51", "D52", "D53"],
        weight=-2,
    )
    alcohol = ComorbidityPanelCategory(
        label="Alcohol abuse",
        default="Z72.1",
        codes=[
            "F10",
            "E52",
            "G62.1",
            "I42.6",
            "K29.2",
            "K70.0",
            "K70.3",
            "K70.9",
            "T51",
            "Z50.2",
            "Z71.4",
            "Z72.1",
        ],
        weight=0,
    )
    drug = ComorbidityPanelCategory(
        label="Drug abuse",
        default="Z72.2",
        codes=[
            "F11",
            "F12",
            "F13",
            "F14",
            "F15",
            "F16",
            "F18",
            "F19",
            "Z71.5",
            "Z72.2",
        ],
        weight=-7,
    )
    psycho = ComorbidityPanelCategory(
        label="Psychoses",
        default="F29",
        codes=[
            "F20",
            "F22",
            "F23",
            "F24",
            "F25",
            "F28",
            "F29",
            "F302",
            "F31.2",
            "F31.5",
        ],
        weight=0,
    )
    depre = ComorbidityPanelCategory(
        label="Depression",
        default="F32",
        codes=[
            "F20.4",
            "F31.3",
            "F31.4",
            "F31.5",
            "F32",
            "F33",
            "F34.1",
            "F41.2",
            "F43.2",
        ],
        weight=-3,
    )

    @classmethod
    def get_score_annotation(cls) -> Sum:
        """
        Calculates the total comorbidity score annotation for a queryset by summing the weights of present conditions.

        This method returns a Django ORM annotation that uses a conditional sum (Sum + Case + When) to assign
        specific weights to each condition code found in `present_conditions__code`. Each condition group (e.g., chf, carit, valv)
        has its own set of codes and associated weight. If a condition code matches one of the predefined groups,
        its corresponding weight is added to the total score. If no match is found, a default value of 0 is used.

        Returns:
            (django.db.models.Sum): An annotation that can be used in queryset aggregation to compute the total score.
        """
        return Sum(
            Case(
                When(present_conditions__code__in=cls.chf.codes, then=cls.chf.weight),
                When(
                    present_conditions__code__in=cls.carit.codes,
                    then=cls.carit.weight,
                ),
                When(present_conditions__code__in=cls.valv.codes, then=cls.valv.weight),
                When(present_conditions__code__in=cls.pcd.codes, then=cls.pcd.weight),
                When(present_conditions__code__in=cls.pvd.codes, then=cls.pvd.weight),
                When(
                    present_conditions__code__in=cls.hypunc.codes,
                    then=cls.hypunc.weight,
                ),
                When(present_conditions__code__in=cls.hypc.codes, then=cls.hypc.weight),
                When(present_conditions__code__in=cls.para.codes, then=cls.para.weight),
                When(present_conditions__code__in=cls.ond.codes, then=cls.ond.weight),
                When(present_conditions__code__in=cls.cpd.codes, then=cls.cpd.weight),
                When(
                    present_conditions__code__in=cls.diabunc.codes,
                    then=cls.diabunc.weight,
                ),
                When(
                    present_conditions__code__in=cls.diabc.codes,
                    then=cls.diabc.weight,
                ),
                When(
                    present_conditions__code__in=cls.hypothy.codes,
                    then=cls.hypothy.weight,
                ),
                When(present_conditions__code__in=cls.rf.codes, then=cls.rf.weight),
                When(present_conditions__code__in=cls.ld.codes, then=cls.ld.weight),
                When(present_conditions__code__in=cls.pud.codes, then=cls.pud.weight),
                When(present_conditions__code__in=cls.aids.codes, then=cls.aids.weight),
                When(
                    present_conditions__code__in=cls.rheumd.codes,
                    then=cls.rheumd.weight,
                ),
                When(present_conditions__code__in=cls.coag.codes, then=cls.coag.weight),
                When(present_conditions__code__in=cls.obes.codes, then=cls.obes.weight),
                When(
                    present_conditions__code__in=cls.wloss.codes,
                    then=cls.wloss.weight,
                ),
                When(present_conditions__code__in=cls.fed.codes, then=cls.fed.weight),
                When(
                    present_conditions__code__in=cls.blane.codes,
                    then=cls.blane.weight,
                ),
                When(present_conditions__code__in=cls.dane.codes, then=cls.dane.weight),
                When(
                    present_conditions__code__in=cls.alcohol.codes,
                    then=cls.alcohol.weight,
                ),
                When(present_conditions__code__in=cls.drug.codes, then=cls.drug.weight),
                When(
                    present_conditions__code__in=cls.psycho.codes,
                    then=cls.psycho.weight,
                ),
                When(
                    present_conditions__code__in=cls.depre.codes,
                    then=cls.depre.weight,
                ),
                default=0,
                output_field=models.FloatField(),
            )
        )


@dataclass(kw_only=True)
class CharlsonPanelDetails:
    """
    Class that provides comorbidity categories and scoring logic for the Charlson Comorbidity Index.

    References:
        - C. N. Klabunde et al., Annals of Epidemiology,Volume 17, Issue 8, 2007, 584-590
        - Quan H et al., Medical Care 2005; 43(11):1130-1139.
    """

    acute_mi = ComorbidityPanelCategory(
        label="Acute myocardial infarction",
        default="I21",
        codes=["I21", "I22"],
        weight=1,
    )
    history_mi = ComorbidityPanelCategory(
        label="History of myocardial infarction",
        default="I25.2",
        codes=["I25.2"],
        weight=1,
    )
    chf = ComorbidityPanelCategory(
        label="Congestive heart failure",
        default="I50.0",
        codes=[
            "I50.0",
            "I09.9",
            "I11.0",
            "I13.0",
            "I13.2",
            "I25.5",
            "I42.0",
            "I43",
            "P29.0",
            "I42.5",
            "I42.6",
            "I42.7",
            "I42.8",
            "I42.9",
        ],
        weight=1,
    )
    pvd = ComorbidityPanelCategory(
        label="Peripheral vascular disease",
        default="I73.9",
        codes=[
            "I73.9",
            "I70",
            "I71",
            "I73.1",
            "I73.8",
            "I73.9",
            "I77.1",
            "I79.0",
            "I79.2",
            "K55.1",
            "K55.8",
            "K55.9",
            "Z95.8",
            "Z95.9",
        ],
        weight=1,
    )
    cvd = ComorbidityPanelCategory(
        label="Cerebrovascular disease",
        default="I67.9",
        codes=["I67.9", "G45", "G46", "H34.0", "I6"],
        weight=1,
    )
    cpd = ComorbidityPanelCategory(
        label="Chronic pulmonary disease",
        default="J44.9",
        codes=["J44.9", "I27.8", "I27.9", "J68.4", "J70.1", "J70.3"]
        + [f"J4{n}" for n in range(0, 8)]
        + [f"J6{n}" for n in range(0, 8)],
        weight=1,
    )
    dementia = ComorbidityPanelCategory(
        label="Dementia",
        default="F03",
        codes=["F03", "G30", "F05.1", "G31.1"] + [f"F0{n}" for n in range(0, 3)],
        weight=1,
    )
    paralysis = ComorbidityPanelCategory(
        label="Hemiplegia or paraplegia",
        default="G83.9",
        codes=["G83.9", "G81", "G04.1", "G11.4", "G80.1", "G80.2", "G82"]
        + [f"G83.{n}" for n in range(0, 5)],
        weight=1,
    )
    diabetes = ComorbidityPanelCategory(
        label="Diabetes without chronic complications",
        default="E14.9",
        codes=[
            "E14.9",
            "E14.1",
            "E14.6",
            "E14.8",
            "E11.9",
            "E10.0",
            "E10.1",
            "E10.6",
            "E10.8",
            "E10.9",
            "E11.0",
            "E11.1",
            "E11.6",
            "E11.8",
            "E13.0",
            "E13.1",
            "E13.6",
            "E13.8",
            "E13.9",
        ],
        weight=1,
    )
    diabates_complications = ComorbidityPanelCategory(
        label="Diabetes with chronic complications",
        default="E14.8",
        codes=[
            "E14.2",
            "E14.3",
            "E14.4",
            "E14.5",
            "E14.7",
            "E10.2",
            "E10.3",
            "E10.4",
            "E10.5",
            "E10.7",
            "E11.2",
            "E11.3",
            "E11.4",
            "E11.5",
            "E11.7",
            "E13.2",
            "E13.3",
            "E13.4",
            "E13.5",
            "E13.7",
        ],
        weight=2,
    )
    renal_disease = ComorbidityPanelCategory(
        label="Renal disease",
        default="N28.9",
        codes=["N28.9", "N19", "I12.0", "I13.1", "N18", "N25.0", "Z94.0", "Z99.2"]
        + [f"N03.{n}" for n in range(2, 8)]
        + [f"N05.{n}" for n in range(2, 8)]
        + [f"Z49.{n}" for n in range(0, 3)],
        weight=2,
    )
    mild_liver_disease = ComorbidityPanelCategory(
        label="Mild liver disease",
        default="K76.9",
        codes=[
            "K76.9",
            "K70",
            "B18",
            "K70.9",
            "K71.7",
            "K73",
            "K74",
            "K76.0",
            "K76.8",
            "Z94.4",
        ]
        + [f"K70.{n}" for n in range(0, 4)]
        + [f"K71.{n}" for n in range(3, 6)]
        + [f"K76.{n}" for n in range(2, 5)],
        weight=1,
    )
    liver_disease = ComorbidityPanelCategory(
        label="Moderate/Severe liver disease",
        default="K72.9",
        codes=[
            "K72.9",
            "I85.0",
            "I85.9",
            "I86.4",
            "I98.2",
            "K70.4",
            "K71.1",
            "K72.1",
            "K76.5",
            "K76.6",
            "K76.7",
        ],
        weight=3,
    )
    ulcers = ComorbidityPanelCategory(
        label="Peptic ulcer disease",
        default="K29",
        codes=[f"K2{n}" for n in range(9, 5, -1)],
        weight=1,
    )
    rheumatic_disease = ComorbidityPanelCategory(
        label="Rheumatic disease",
        default="M35.9",
        codes=[
            "M35.9",
            "M05",
            "M06",
            "M31.5",
            "M32",
            "M33",
            "M34",
            "M35.1",
            "M35.3",
            "M36.0",
        ],
        weight=1,
    )
    aids = ComorbidityPanelCategory(
        label="AIDS/HIV",
        default="B24",
        codes=["B24", "B20", "B21", "B22"],
        weight=6,
    )

    @classmethod
    def get_score_annotation(cls) -> Sum:
        """
        Constructs a Django ORM annotation that calculates the total comorbidity score for a patient
        based on the presence of specific condition codes. Each condition code is mapped to a weight,
        and the sum of these weights is computed using conditional logic.

        Returns:
            (django.db.models.Sum): An annotation expression that can be used in queryset aggregation
            to compute the total comorbidity score for each patient.
        """
        return Sum(
            Case(
                When(
                    present_conditions__code__in=cls.acute_mi.codes
                    + cls.history_mi.codes,
                    then=Case(
                        When(
                            present_conditions__code__in=cls.acute_mi.codes,
                            then=cls.acute_mi.weight,
                        ),
                        When(
                            present_conditions__code__in=cls.history_mi.codes,
                            then=cls.history_mi.weight,
                        ),
                        default=0,
                    ),
                ),
                When(present_conditions__code__in=cls.chf.codes, then=cls.chf.weight),
                When(present_conditions__code__in=cls.pvd.codes, then=cls.pvd.weight),
                When(present_conditions__code__in=cls.cvd.codes, then=cls.cvd.weight),
                When(
                    present_conditions__code__in=cls.dementia.codes,
                    then=cls.dementia.weight,
                ),
                When(
                    present_conditions__code__in=cls.paralysis.codes,
                    then=cls.paralysis.weight,
                ),
                When(
                    present_conditions__code__in=cls.diabetes.codes
                    + cls.diabates_complications.codes,
                    then=Case(
                        When(
                            present_conditions__code__in=cls.diabetes.codes,
                            then=cls.diabetes.weight,
                        ),
                        When(
                            present_conditions__code__in=cls.diabates_complications.codes,
                            then=cls.diabates_complications.weight,
                        ),
                        default=0,
                    ),
                ),
                When(
                    present_conditions__code__in=cls.renal_disease.codes,
                    then=cls.renal_disease.weight,
                ),
                When(
                    present_conditions__code__in=cls.mild_liver_disease.codes
                    + cls.liver_disease.codes,
                    then=Case(
                        When(
                            present_conditions__code__in=cls.mild_liver_disease.codes,
                            then=cls.mild_liver_disease.weight,
                        ),
                        When(
                            present_conditions__code__in=cls.liver_disease.codes,
                            then=cls.liver_disease.weight,
                        ),
                        default=0,
                    ),
                ),
                When(
                    present_conditions__code__in=cls.ulcers.codes,
                    then=cls.ulcers.weight,
                ),
                When(
                    present_conditions__code__in=cls.rheumatic_disease.codes,
                    then=cls.rheumatic_disease.weight,
                ),
                When(present_conditions__code__in=cls.aids.codes, then=cls.aids.weight),
                default=0,
                output_field=models.FloatField(),
            )
        )


@dataclass
class NciPanelDetails:
    """
    This class defines comorbidity categories and their associated ICD codes and weights for the NCI comorbidity panel. 
    Each comorbidity is represented as a `ComorbidityPanelCategory` with a label, default ICD code, a list of ICD codes, and a weight.

    References:
        - C. N. Klabunde et al., Annals of Epidemiology, Volume 17, Issue 8, 2007, 584-590
        - Quan H et al., Medical Care 2005; 43(11):1130-1139.
    """

    acute_mi = ComorbidityPanelCategory(
        label="Acute myocardial infarction",
        default="I21",
        codes=["I21", "I22"],
        weight=0.12624,
    )
    history_mi = ComorbidityPanelCategory(
        label="History of myocardial infarction",
        default="I25.2",
        codes=["I25.2"],
        weight=0.7999,
    )
    chf = ComorbidityPanelCategory(
        label="Congestive heart failure",
        default="I50.0",
        codes=[
            "I50.0",
            "I09.9",
            "I11.0",
            "I13.0",
            "I13.2",
            "I25.5",
            "I42.0",
            "I43",
            "P29.0",
            "I42.5",
            "I42.6",
            "I42.7",
            "I42.8",
            "I42.9",
        ],
        weight=0.64441,
    )
    pvd = ComorbidityPanelCategory(
        label="Peripheral vascular disease",
        default="I73.9",
        codes=[
            "I73.9",
            "I70",
            "I71",
            "I73.1",
            "I73.8",
            "I73.9",
            "I77.1",
            "I79.0",
            "I79.2",
            "K55.1",
            "K55.8",
            "K55.9",
            "Z95.8",
            "Z95.9",
        ],
        weight=0.26232,
    )
    cvd = ComorbidityPanelCategory(
        label="Cerebrovascular disease",
        default="I67.9",
        codes=["I67.9", "G45", "G46", "H34.0", "I6"],
        weight=0.27868,
    )
    cpd = ComorbidityPanelCategory(
        label="Chronic pulmonary disease",
        default="J44.9",
        codes=["J44.9", "I27.8", "I27.9", "J68.4", "J70.1", "J70.3"]
        + [f"J4{n}" for n in range(0, 8)]
        + [f"J6{n}" for n in range(0, 8)],
        weight=1,
    )
    dementia = ComorbidityPanelCategory(
        label="Dementia",
        default="F03",
        codes=["F03", "G30", "F05.1", "G31.1"] + [f"F0{n}" for n in range(0, 3)],
        weight=0.72219,
    )
    paralysis = ComorbidityPanelCategory(
        label="Hemiplegia or paraplegia",
        default="G83.9",
        codes=["G83.9", "G81", "G04.1", "G11.4", "G80.1", "G80.2", "G82"]
        + [f"G83.{n}" for n in range(0, 5)],
        weight=0.39882,
    )
    diabetes = ComorbidityPanelCategory(
        label="Diabetes without chronic complications",
        default="E14.9",
        codes=[
            "E14.9",
            "E14.1",
            "E14.6",
            "E14.8",
            "E11.9",
            "E10.0",
            "E10.1",
            "E10.6",
            "E10.8",
            "E10.9",
            "E11.0",
            "E11.1",
            "E11.6",
            "E11.8",
            "E13.0",
            "E13.1",
            "E13.6",
            "E13.8",
            "E13.9",
        ],
        weight=0.29408,
    )
    diabates_complications = ComorbidityPanelCategory(
        label="Diabetes with chronic complications",
        default="E14.8",
        codes=[
            "E14.2",
            "E14.3",
            "E14.4",
            "E14.5",
            "E14.7",
            "E10.2",
            "E10.3",
            "E10.4",
            "E10.5",
            "E10.7",
            "E11.2",
            "E11.3",
            "E11.4",
            "E11.5",
            "E11.7",
            "E13.2",
            "E13.3",
            "E13.4",
            "E13.5",
            "E13.7",
        ],
        weight=0.29408,
    )
    renal_disease = ComorbidityPanelCategory(
        label="Renal disease",
        default="N28.9",
        codes=["N28.9", "N19", "I12.0", "I13.1", "N18", "N25.0", "Z94.0", "Z99.2"]
        + [f"N03.{n}" for n in range(2, 8)]
        + [f"N05.{n}" for n in range(2, 8)]
        + [f"Z49.{n}" for n in range(0, 3)],
        weight=0.47010,
    )
    mild_liver_disease = ComorbidityPanelCategory(
        label="Mild liver disease",
        default="K76.9",
        codes=[
            "K76.9",
            "K70",
            "B18",
            "K70.9",
            "K71.7",
            "K73",
            "K74",
            "K76.0",
            "K76.8",
            "Z94.4",
        ]
        + [f"K70.{n}" for n in range(0, 4)]
        + [f"K71.{n}" for n in range(3, 6)]
        + [f"K76.{n}" for n in range(2, 5)],
        weight=0.73803,
    )
    liver_disease = ComorbidityPanelCategory(
        label="Moderate/Severe liver disease",
        default="K72.9",
        codes=[
            "K72.9",
            "I85.0",
            "I85.9",
            "I86.4",
            "I98.2",
            "K70.4",
            "K71.1",
            "K72.1",
            "K76.5",
            "K76.6",
            "K76.7",
        ],
        weight=0.73803,
    )
    ulcers = ComorbidityPanelCategory(
        label="Peptic ulcer disease",
        default="K29",
        codes=[f"K2{n}" for n in range(9, 5, -1)],
        weight=0.07506,
    )
    rheumatic_disease = ComorbidityPanelCategory(
        label="Rheumatic disease",
        default="M35.9",
        codes=[
            "M35.9",
            "M05",
            "M06",
            "M31.5",
            "M32",
            "M33",
            "M34",
            "M35.1",
            "M35.3",
            "M36.0",
        ],
        weight=0.21905,
    )
    aids = ComorbidityPanelCategory(
        label="AIDS/HIV",
        default="B24",
        codes=["B24", "B20", "B21", "B22"],
        weight=0.58362,
    )

    @classmethod
    def get_score_annotation(cls) -> Sum:
        """
        Generates a Django ORM annotation that calculates the weighted comorbidity score for a queryset.

        The score is computed by summing the weights of present comorbid conditions, based on their codes.
        Each condition is checked against its respective code list, and the corresponding weight is applied.
        Special handling is provided for diabetes and liver disease, where the weight depends on whether
        complications or severity are present.

        Returns:
            Sum: A Django ORM annotation representing the total comorbidity score as a float.
        """
        return Sum(
            Case(
                When(
                    present_conditions__code__in=cls.acute_mi.codes,
                    then=cls.acute_mi.weight,
                ),
                When(
                    present_conditions__code__in=cls.history_mi.codes,
                    then=cls.history_mi.weight,
                ),
                When(present_conditions__code__in=cls.chf.codes, then=cls.chf.weight),
                When(present_conditions__code__in=cls.pvd.codes, then=cls.pvd.weight),
                When(present_conditions__code__in=cls.cvd.codes, then=cls.cvd.weight),
                When(
                    present_conditions__code__in=cls.dementia.codes,
                    then=cls.dementia.weight,
                ),
                When(
                    present_conditions__code__in=cls.paralysis.codes,
                    then=cls.paralysis.weight,
                ),
                When(
                    present_conditions__code__in=cls.diabetes.codes
                    + cls.diabates_complications.codes,
                    then=Case(
                        When(
                            present_conditions__code__in=cls.diabetes.codes,
                            then=cls.diabetes.weight,
                        ),
                        When(
                            present_conditions__code__in=cls.diabates_complications.codes,
                            then=cls.diabates_complications.weight,
                        ),
                        default=0.0,
                    ),
                ),
                When(
                    present_conditions__code__in=cls.renal_disease.codes,
                    then=cls.renal_disease.weight,
                ),
                When(
                    present_conditions__code__in=cls.mild_liver_disease.codes
                    + cls.liver_disease.codes,
                    then=Case(
                        When(
                            present_conditions__code__in=cls.mild_liver_disease.codes,
                            then=cls.mild_liver_disease.weight,
                        ),
                        When(
                            present_conditions__code__in=cls.liver_disease.codes,
                            then=cls.liver_disease.weight,
                        ),
                        default=0.0,
                    ),
                ),
                When(
                    present_conditions__code__in=cls.ulcers.codes,
                    then=cls.ulcers.weight,
                ),
                When(
                    present_conditions__code__in=cls.rheumatic_disease.codes,
                    then=cls.rheumatic_disease.weight,
                ),
                When(present_conditions__code__in=cls.aids.codes, then=cls.aids.weight),
                default=0.0,
                output_field=models.FloatField(),
            )
        )


@pghistory.track()
class ComorbiditiesAssessment(BaseModel):
    """
    Represents an assessment of patient comorbidities within a specific clinical case.

    Attributes:
        COMORBIDITY_PANELS_DETAILS (dict): Maps comorbidity panel types to their detail classes.
        objects (QueryablePropertiesManager): Custom manager for querying properties.
        case (models.ForeignKey[PatientCase]): Reference to the patient case being assessed.
        date (models.DateField): Date when the comorbidities assessment was performed.
        index_condition (models.ForeignKey[NeoplasticEntity]): The primary neoplastic entity for comorbidity assessment.
        panel (models.CharField): Type of comorbidities panel used for assessment.
        present_conditions (termfields.CodedConceptField[terminologies.ICD10Condition]): List of present comorbid conditions (ICD-10).
        absent_conditions (termfields.CodedConceptField[terminologies.ICD10Condition]): List of absent comorbid conditions (ICD-10).
        score (AnnotationProperty): Calculated comorbidity score based on the selected panel.
    """

    COMORBIDITY_PANELS_DETAILS = {
        ComorbiditiesAssessmentPanelChoices.CHARLSON: CharlsonPanelDetails,
        ComorbiditiesAssessmentPanelChoices.NCI: NciPanelDetails,
        ComorbiditiesAssessmentPanelChoices.ELIXHAUSER: ElixhauserPanelDetails,
    }

    objects = QueryablePropertiesManager()

    case = models.ForeignKey(
        verbose_name=_("Patient case"),
        help_text=_(
            "Indicates the case of the patient who's comorbidities are being recorded"
        ),
        to=PatientCase,
        related_name="comorbidities",
        on_delete=models.CASCADE,
    )
    date = models.DateField(
        verbose_name=_("Assessment date"),
        help_text=_(
            "Clinically-relevant date at which the patient's comorbidities were assessed and recorded."
        ),
    )
    index_condition = models.ForeignKey(
        verbose_name=_("Index neoplastic entity"),
        help_text=_(
            "The primary neoplastic entity against which comorbidities are assessed"
        ),
        to=NeoplasticEntity,
        related_name="comorbidities",
        on_delete=models.CASCADE,
    )
    panel = models.CharField(
        verbose_name=_("Panel"),
        help_text=_("Comorbidities panel"),
        choices=ComorbiditiesAssessmentPanelChoices,
        max_length=30,
        null=True,
        blank=True,
    )
    present_conditions = termfields.CodedConceptField(
        verbose_name=_("Present comorbid conditions"),
        help_text=_("Present comorbid conditions"),
        terminology=terminologies.ICD10Condition,
        multiple=True,
        blank=True,
    )
    absent_conditions = termfields.CodedConceptField(
        verbose_name=_("Absent comorbid conditions"),
        help_text=_("Absent comorbid conditions"),
        terminology=terminologies.ICD10Condition,
        multiple=True,
        blank=True,
    )
    score = AnnotationProperty(
        verbose_name=_("Comorbidity score"),
        annotation=Case(
            When(
                panel=ComorbiditiesAssessmentPanelChoices.CHARLSON,
                then=CharlsonPanelDetails.get_score_annotation(),
            ),
            When(
                panel=ComorbiditiesAssessmentPanelChoices.NCI,
                then=NciPanelDetails.get_score_annotation(),
            ),
            When(
                panel=ComorbiditiesAssessmentPanelChoices.ELIXHAUSER,
                then=ElixhauserPanelDetails.get_score_annotation(),
            ),
            default=None,
            output_field=models.FloatField(),
        ),
    )

    @property
    def description(self):
        if self.panel:
            return f"{self.panel} panel (Score: {self.score})"
        else:
            return f"Comorbidities: {self.present_conditions.count()} present and {self.absent_conditions.count()} absent"
