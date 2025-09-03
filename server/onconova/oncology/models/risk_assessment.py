import pghistory
from django.db import models
from django.utils.translation import gettext_lazy as _

import onconova.terminology.fields as termfields
import onconova.terminology.models as terminologies
from onconova.core.models import BaseModel
from onconova.oncology.models import NeoplasticEntity, PatientCase


@pghistory.track()
class RiskAssessment(BaseModel):
    """
    Represents a risk assessment for a patient's cancer case.

    Attributes:
        case (models.ForeignKey[PatientCase]): Reference to the patient's case being assessed.
        date (models.DateField): Date when the risk assessment was performed and recorded.
        assessed_entities (models.ManyToManyField[NeoplasticEntity]): Neoplastic entities assessed to estimate risk.
        methodology (termfields.CodedConceptField[terminologies.CancerRiskAssessmentMethod]): Method or type of risk assessment used.
        risk (termfields.CodedConceptField[terminologies.CancerRiskAssessmentClassification]): Assessed risk classification.
        score (models.FloatField): Quantitative score used to classify the risk (optional).
    """

    case = models.ForeignKey(
        verbose_name=_("Patient case"),
        help_text=_("Indicates the case of the patient who's cancer risk is assesed"),
        to=PatientCase,
        related_name="risk_assessments",
        on_delete=models.CASCADE,
    )
    date = models.DateField(
        verbose_name=_("Assessment date"),
        help_text=_(
            "Clinically-relevant date at which the risk assessment was performed and recorded."
        ),
    )
    assessed_entities = models.ManyToManyField(
        verbose_name=_("Assessed neoplastic entities"),
        help_text=_(
            "References to the neoplastic entities that were assessed to estimate the risk."
        ),
        to=NeoplasticEntity,
        related_name="risk_assessments",
    )
    methodology = termfields.CodedConceptField(
        verbose_name=_("Assessment methodology"),
        help_text=_("Indicates the method or type of risk assessment"),
        terminology=terminologies.CancerRiskAssessmentMethod,
    )
    risk = termfields.CodedConceptField(
        verbose_name=_("Risk"),
        help_text=_("Assessed risk"),
        terminology=terminologies.CancerRiskAssessmentClassification,
    )
    score = models.FloatField(
        verbose_name=_("Score"),
        help_text=_("Quantitative score used to classify the risk"),
        blank=True,
        null=True,
    )

    def save(self, *args, **kwargs):
        try:
            validate_risk_classification(self)
            super().save(*args, **kwargs)
        except AssertionError:
            raise ValueError(
                f'{self.risk} is not a valid choice for risk methodology "{self.methodology}".'
            )

    @property
    def description(self):
        return f"{self.risk} ({self.methodology})"


def validate_risk_classification(assessment):
    """
    Validates that the risk classification code in the given assessment matches the expected codes
    for the specified risk assessment methodology.

    The function checks the `assessment.methodology.code` and asserts that `assessment.risk.code`
    is one of the allowed codes for that methodology.

    Args:
        assessment (RiskAssessment | RiskAssessmentSchema): An object containing `methodology.code` and `risk.code` attributes.

    Raises:
        AssertionError: If the risk code does not match the expected codes for the methodology.
    """
    if (
        assessment.methodology.code == "C136962"
    ):  # Follicular Lymphoma International Prognostic Index (FLIPI)
        assert assessment.risk.code in (
            "C136965",  # FLIPI Score 0-1, Low Risk
            "C136967",  # FLIPI Score 2, Intermediate Risk
            "C136968",  # FLIPI Score Greater than or Equal to 3, High Risk
        )
    elif (
        assessment.methodology.code == "C181086"
    ):  # D'Amico Prostate Cancer Risk Classification
        assert assessment.risk.code in (
            "C102403",  # Low risk
            "C102402",  # Intermediate risk
            "C102401",  # High risk
        )
    elif (
        assessment.methodology.code == "C127872"
    ):  # European Treatment Outcome Study (EUTOS) Score
        assert assessment.risk.code in (
            "C102403",  # Low risk
            "C102401",  # High risk
        )
    elif assessment.methodology.code == "C127873":  # Hasford Score
        assert assessment.risk.code in (
            "C102403",  # Low risk
            "C102402",  # Intermediate risk
            "C102401",  # High risk
        )
    elif assessment.methodology.code == "C127875":  # Sokal Score
        assert assessment.risk.code in (
            "C102403",  # Low risk
            "C102402",  # Intermediate risk
            "C102401",  # High risk
        )
    elif (
        assessment.methodology.code == "C155843"
    ):  # International Metastatic Renal Cell Carcinoma Database Consortium (IMDC) Criteria
        assert assessment.risk.code in (
            "C155844",  # IMDC Favorable risk
            "C155845",  # IMDC Intermediate Risk
            "C155846",  # IMDC Poor risk
        )
    elif (
        assessment.methodology.code == "C161805"
    ):  # International Prognostic Index (IPI) Risk Group
        assert assessment.risk.code in (
            "C161809",  # High Risk
            "C161808",  # High-Intermediate Risk
            "C161806",  # Low Risk
            "C161807",  # Low-Intermediate Risk
        )
    elif (
        assessment.methodology.code == "C177562"
    ):  # European LeukemiaNet Risk Classification
        assert assessment.risk.code in (
            "C188368",  # Adverse-Risk
            "C188369",  # Favorable-Risk
            "C188370",  # Intermediate-Risk
        )
    elif assessment.methodology.code == "C121007":  # Child-Pugh Clinical Classification
        assert assessment.risk.code in (
            "C113691",  # Class A
            "C146790",  # Class A5
            "C146791",  # Class A6
            "C113692",  # Class B
            "C146792",  # Class B7
            "C146793",  # Class B8
            "C146794",  # Class B9
            "C113694",  # Class C
            "C146795",  # Class C10
            "C146796",  # Class C11
            "C146797",  # Class C12
            "C146798",  # Class C13
            "C146799",  # Class C14
            "C146801",  # Class C15
            "C148151",  # Class A-B7 Cirrhosis
        )
    elif (
        assessment.methodology.code == "C181085"
    ):  # USCF Cancer of the Prostate Risk Assessment Score
        assert assessment.risk.code in (
            "C102403",  # Low risk
            "C102402",  # Intermediate risk
            "C102401",  # High risk
        )
    elif (
        assessment.methodology.code == "C162781"
    ):  # Mantle Cell Lymphoma International Prognostic Index (MIPI)
        assert assessment.risk.code in (
            "C102403",  # Low risk
            "C102402",  # Intermediate risk
            "C102401",  # High risk
        )
    elif (
        assessment.methodology.code == "C181084"
    ):  # NCCN Prostate Cancer Risk Stratification for Clinically Localized Disease
        assert assessment.risk.code in (
            "C192873",  # Very Low Risk
            "C192874",  # Low Risk
            "C192877",  # Unfavorable-Intermediate Risk
            "C192876",  # Favorable-Intermediate Risk
            "C192875",  # Intermediate Risk
            "C192878",  # High Risk
            "C192879",  # Very High Risk
        )
    elif assessment.methodology.code == "C177309":  # Seminoma IGCCC Risk Classification
        assert assessment.risk.code in (
            "C177313",  # Good
            "C177314",  # Intermediate
        )
    elif (
        assessment.methodology.code == "C177308"
    ):  # Non-Seminomatous Germ Cell Tumor IGCCC Risk Classification
        assert assessment.risk.code in (
            "C177310",  # Good
            "C177311",  # Intermediate
            "C177312",  # Poor
        )
    elif (
        assessment.methodology.code == "C142346"
    ):  # International Society of Urological Pathology Gleason Grade Group
        assert assessment.risk.code in (
            "C162654",  # Grade Pattern 1
            "C162655",  # Grade Pattern 2
            "C162656",  # Grade Pattern 3
            "C162657",  # Grade Pattern 4
            "C162658",  # Grade Pattern 5
        )
