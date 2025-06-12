import pghistory

from django.db import models
from django.utils.translation import gettext_lazy as _

from pop.core.models import BaseModel
from pop.oncology.models import PatientCase, NeoplasticEntity
import pop.terminology.fields as termfields
import pop.terminology.models as terminologies


@pghistory.track()
class RiskAssessment(BaseModel):
    """
    A risk assessment may be done by collecting information about a person’s age, sex, personal
    and family medical history, ethnic background, lifestyle, and other factors and
    using statistics tools to calculate risk
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

    @property
    def description(self):
        return f"{self.risk} ({self.methodology})"
