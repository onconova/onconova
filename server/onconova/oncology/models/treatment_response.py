import pghistory
from django.db import models
from django.utils.translation import gettext_lazy as _

import onconova.terminology.fields as termfields
import onconova.terminology.models as terminologies
from onconova.core.models import BaseModel
from onconova.oncology.models import NeoplasticEntity, PatientCase


@pghistory.track()
class TreatmentResponse(BaseModel):
    """
    Represents a clinical assessment of a patient's response to treatment.

    Attributes:
        case (models.ForeignKey[PatientCase]): The patient case associated with this treatment response.
        date (models.DateField): The date when the treatment response was assessed.
        assessed_entities (models.ManyToManyField[NeoplasticEntity]): Neoplastic entities evaluated for treatment response.
        recist (termfields.CodedConceptField[terminologies.CancerTreatmentResponse]): RECIST classification of the treatment response.
        recist_interpreted (models.BooleanField): Indicates if the RECIST value was interpreted or taken directly from the radiology report.
        methodology (termfields.CodedConceptField[terminologies.CancerTreatmentResponseObservationMethod]): Method used to assess and classify the treatment response.
        assessed_bodysites (termfields.CodedConceptField[terminologies.ObservationBodySite]): Anatomical locations assessed to determine the treatment response.
        description (str): Returns a human-readable description of the treatment response, including RECIST classification and assessment methodology.
    """

    case = models.ForeignKey(
        verbose_name=_("Patient case"),
        help_text=_(
            "Indicates the case of the patient who's treatment response is asseessed"
        ),
        to=PatientCase,
        related_name="treatment_responses",
        on_delete=models.CASCADE,
    )
    date = models.DateField(
        verbose_name=_("Assessment date"),
        help_text=_("Clinically-relevant date of the treatment response assessment"),
    )
    assessed_entities = models.ManyToManyField(
        verbose_name=_("Assessed neoplastic entities"),
        help_text=_(
            "References to the neoplastic entities that were assesed for treatment response"
        ),
        to=NeoplasticEntity,
        related_name="treatment_responses",
    )
    recist = termfields.CodedConceptField(
        verbose_name=_("RECIST"),
        help_text=_("The classification of the treatment response according to RECIST"),
        terminology=terminologies.CancerTreatmentResponse,
    )
    recist_interpreted = models.BooleanField(
        verbose_name=_("RECIST Interpreted?"),
        help_text=_(
            "Indicates whether the RECIST value was interpreted or taken from the radiology report"
        ),
        null=True,
        blank=True,
    )
    methodology = termfields.CodedConceptField(
        verbose_name=_("Assessment method"),
        help_text=_("Method used to assess and classify the treatment response"),
        terminology=terminologies.CancerTreatmentResponseObservationMethod,
    )
    assessed_bodysites = termfields.CodedConceptField(
        verbose_name=_("Assessed anatomical location"),
        help_text=_("Anatomical location assessed to determine the treatment response"),
        terminology=terminologies.ObservationBodySite,
        blank=True,
        multiple=True,
    )

    def assign_therapy_line(self):
        """
        Assigns therapy lines to the current case and refreshes the instance from the database.

        This method imports the `TherapyLine` model and calls its `assign_therapy_lines` method,
        passing the current case as an argument. After assignment, it refreshes the instance
        from the database to ensure updated data is loaded.

        Returns:
            (Self): The updated instance after refreshing from the database.
        """
        from onconova.oncology.models.therapy_line import TherapyLine

        TherapyLine.assign_therapy_lines(self.case)
        self.refresh_from_db()
        return self

    @property
    def description(self):
        methodology = (
            f' asserted by {str(self.methodology).split(" - ")[0]}'
            if self.methodology.code != "1287211007"
            else ""
        )
        return f"{self.recist.display}{methodology}"
