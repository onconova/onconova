import pghistory
from django.db import models
from django.utils.translation import gettext_lazy as _

import onconova.terminology.fields as termfields
import onconova.terminology.models as terminologies
from onconova.core.models import BaseModel
from onconova.oncology.models import PatientCase


@pghistory.track()
class FamilyHistory(BaseModel):
    """
    Represents a record of a patient's family member's cancer history.

    Attributes:
        case (models.ForeignKey[PatientCase]): Reference to the patient case whose family history is being recorded.
        date (models.DateField): Date when the family history assessment was performed.
        relationship (termfields.CodedConceptField[terminologies.FamilyMemberType]): Relationship of the family member to the patient.
        had_cancer (models.BooleanField): Indicates if the family member had a history of cancer.
        contributed_to_death (models.BooleanField): Indicates if cancer contributed to the family member's death.
        onset_age (models.PositiveSmallIntegerField): Age at which the family member's cancer manifested.
        topography (termfields.CodedConceptField[terminologies.CancerTopography]): Topography of the family member's cancer.
        morphology (termfields.CodedConceptField[terminologies.CancerMorphology]): Morphology of the family member's cancer.
    """

    case = models.ForeignKey(
        verbose_name=_("Patient case"),
        help_text=_(
            "Indicates the case of the patient who's family's history is being recorded"
        ),
        to=PatientCase,
        related_name="family_histories",
        on_delete=models.CASCADE,
    )
    date = models.DateField(
        verbose_name=_("Assessment date"),
        help_text=_(
            "Clinically-relevant date at which the patient's family history was assessed and recorded."
        ),
    )
    relationship = termfields.CodedConceptField(
        verbose_name=_("Relationship"),
        help_text=_("Relationship to the patient"),
        terminology=terminologies.FamilyMemberType,
    )
    had_cancer = models.BooleanField(
        verbose_name=_("Had cancer"),
        help_text=_("Whether the family member has a history of cancer"),
    )
    contributed_to_death = models.BooleanField(
        verbose_name=_("Contributed to death"),
        help_text=_(
            "Whether the cancer contributed to the cause of death of the family member"
        ),
        null=True,
        blank=True,
    )
    onset_age = models.PositiveSmallIntegerField(
        verbose_name=_("Onset age"),
        help_text=_("Age at which the family member's cancer manifested"),
        null=True,
        blank=True,
    )
    topography = termfields.CodedConceptField(
        verbose_name=_("Topography"),
        help_text=_("Estimated or actual topography of the family member's cancer"),
        terminology=terminologies.CancerTopography,
        null=True,
        blank=True,
    )
    morphology = termfields.CodedConceptField(
        verbose_name=_("Morphology"),
        help_text=_("Morphology of the family member's cancer (if known)"),
        terminology=terminologies.CancerMorphology,
        null=True,
        blank=True,
    )

    @property
    def description(self):
        if self.relationship.display:
            relationship = self.relationship.display.title()
        condition = ""
        if self.had_cancer:
            if self.topography and self.topography.display:
                condition = f" with {self.topography.display.lower().replace(', nos','')} cancer"
            else:
                condition = "with history of cancer"
        else:
            condition = "without history of cancer"
        return f"{relationship}{condition}"
