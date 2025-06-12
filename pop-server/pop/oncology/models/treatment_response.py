import pghistory

from django.db import models
from django.utils.translation import gettext_lazy as _

from pop.core.models import BaseModel
from pop.oncology.models import PatientCase, NeoplasticEntity
import pop.terminology.fields as termfields
import pop.terminology.models as terminologies


@pghistory.track()
class TreatmentResponse(BaseModel):

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
        null=True,
        blank=True,
        multiple=True,
    )

    def assign_therapy_line(self):
        from pop.oncology.models.therapy_line import TherapyLine

        TherapyLine.assign_therapy_lines(self.case)
        self.refresh_from_db()
        return self

    @property
    def description(self):
        methodology = (
            f' asserted by {self.methodology.display.split(" - ")[0]}'
            if self.methodology.code != "1287211007"
            else ""
        )
        return f"{self.recist.display}{methodology}"
