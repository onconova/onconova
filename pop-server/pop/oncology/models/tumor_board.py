import pghistory

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.postgres.fields import ArrayField
from django.core.validators import RegexValidator

from pop.core.models import BaseModel
from pop.oncology.models import PatientCase
from pop.oncology.models.neoplastic_entity import NeoplasticEntity
from pop.oncology.models.genomic_variant import GenomicVariant
from pop.oncology.models.genomic_signature import GenomicSignature
from pop.oncology.models.tumor_marker import TumorMarker
import pop.terminology.fields as termfields
import pop.terminology.models as terminologies


class TumorBoardSpecialties(models.TextChoices):
    UNSPECIFIED = "unspecified"
    MOLECULAR = "molecular"


@pghistory.track(
    obj_field=pghistory.ObjForeignKey(
        related_name="parent_events",
        related_query_name="parent_events",
    )
)
class TumorBoard(BaseModel):

    case = models.ForeignKey(
        verbose_name=_("Patient case"),
        help_text=_(
            "Indicates the case of the patient which was discussed at the tumor board"
        ),
        to=PatientCase,
        related_name="tumor_boards",
        on_delete=models.CASCADE,
    )
    date = models.DateField(
        verbose_name=_("Date"),
        help_text=_(
            "Date at which the tumor board took place and/or when the board provided a recommendation."
        ),
    )
    related_entities = models.ManyToManyField(
        verbose_name=_("Related neoplastic entities"),
        help_text=_(
            "References to the neoplastic entities that were the focus of the tumor board."
        ),
        to=NeoplasticEntity,
        related_name="+",
    )
    recommendations = termfields.CodedConceptField(
        verbose_name=_("Recommendations"),
        help_text=_(
            "Recommendation(s) provided by the board regarding the patient's care"
        ),
        terminology=terminologies.TumorBoardRecommendation,
        multiple=True,
        null=True,
        blank=True,
    )

    @property
    def tumor_board_specialty(self):
        for signature_type in TumorBoardSpecialties.values:
            try:
                getattr(self, signature_type)
                return signature_type
            except:
                continue

    @property
    def specialized_tumor_board(self):
        if self.tumor_board_specialty:
            return getattr(self, self.tumor_board_specialty, None)

    @property
    def description(self):
        if self.specialized_tumor_board:
            return self.specialized_tumor_board.description
        else:
            return f"Tumor board with {self.recommendations.count()} recommendations"


@pghistory.track()
class UnspecifiedTumorBoard(TumorBoard):

    tumor_board = models.OneToOneField(
        to=TumorBoard,
        on_delete=models.CASCADE,
        related_name=TumorBoardSpecialties.UNSPECIFIED.value,
        parent_link=True,
        primary_key=True,
    )


@pghistory.track()
class MolecularTumorBoard(TumorBoard):

    tumor_board = models.OneToOneField(
        to=TumorBoard,
        on_delete=models.CASCADE,
        related_name=TumorBoardSpecialties.MOLECULAR.value,
        parent_link=True,
        primary_key=True,
    )
    conducted_molecular_comparison = models.BooleanField(
        verbose_name=_("Conducted molecular comparison?"),
        help_text=_(
            "Indicates whether a molecular comparison was conducted during the molecular tumor board"
        ),
        null=True,
        blank=True,
    )
    molecular_comparison_match = models.ForeignKey(
        verbose_name=_("Molecular comparison match"),
        help_text=_(
            "The neoplastic entity that was matched during the molecular comparison"
        ),
        to=NeoplasticEntity,
        related_name="+",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    conducted_cup_characterization = models.BooleanField(
        verbose_name=_("Conducted CUP characterization?"),
        help_text=_(
            "Whether there was a cancer of unknown primary (CUP) characterization during the molecular tumor board."
        ),
        null=True,
        blank=True,
    )
    characterized_cup = models.BooleanField(
        verbose_name=_("Successful CUP characterization?"),
        help_text=_(
            "Whether the cancer of unknown primary (CUP) characterization was successful."
        ),
        null=True,
        blank=True,
    )
    reviewed_reports = ArrayField(
        verbose_name="Reviewed genomics reports",
        base_field=models.CharField(
            max_length=500,
        ),
        blank=True,
        default=list,
    )

    @property
    def description(self):
        recommendations = (
            self.therapeutic_recommendations.count() + self.recommendations.count()
        )
        if recommendations == 0:
            recommendations = "no"
        return f"MTB review with {recommendations} recommendations"


@pghistory.track()
class MolecularTherapeuticRecommendation(BaseModel):

    molecular_tumor_board = models.ForeignKey(
        verbose_name=_("Molecular tumor board"),
        help_text=_("Molecular tumor board where the recommendation was issued"),
        to=MolecularTumorBoard,
        related_name="therapeutic_recommendations",
        on_delete=models.CASCADE,
    )
    expected_effect = termfields.CodedConceptField(
        verbose_name=_("Expected medication action"),
        help_text=_("Classification of the expected effect of the drug"),
        terminology=terminologies.ExpectedDrugAction,
        null=True,
        blank=True,
    )
    clinical_trial = models.CharField(
        verbose_name=_("Recommended clinical trial"),
        help_text=_(
            "Clinical trial (NCT-Iddentifier) recommended by the board for enrollment"
        ),
        validators=[RegexValidator(r"^NCT\d{8}$")],
        max_length=15,
        null=True,
        blank=True,
    )
    drugs = termfields.CodedConceptField(
        verbose_name=_("Drug(s)"),
        help_text=_("Drugs(s) being recommended"),
        terminology=terminologies.AntineoplasticAgent,
        multiple=True,
        null=True,
        blank=True,
    )
    off_label_use = models.BooleanField(
        verbose_name=_("Off-label use"),
        help_text=_("Whether the medication(s) recommended were off-label"),
        null=True,
        blank=True,
    )
    within_soc = models.BooleanField(
        verbose_name=_("Within SOC"),
        help_text=_(
            "Whether the medication(s) recommended were within standard of care"
        ),
        null=True,
        blank=True,
    )
    supporting_genomic_variants = models.ManyToManyField(
        verbose_name=_("Supporting genomic variants"),
        help_text=_("Genomic variants that support the recommendation"),
        to=GenomicVariant,
        related_name="+",
        blank=True,
    )
    supporting_genomic_signatures = models.ManyToManyField(
        verbose_name=_("Supporting genomic signatures"),
        help_text=_("Genomic signatures that support the recommendation"),
        to=GenomicSignature,
        related_name="+",
        blank=True,
    )
    supporting_tumor_markers = models.ManyToManyField(
        verbose_name=_("Supporting tumor markers"),
        help_text=_("Tumor markers that support the recommendation"),
        to=TumorMarker,
        related_name="+",
        blank=True,
    )

    @property
    def supporting(self):
        return (
            list(self.supporting_genomic_variants.all())
            + list(self.supporting_genomic_signatures.all())
            + list(self.supporting_tumor_markers)
        )

    @property
    def description(self):
        drugs = [med.display for med in self.drugs.all()]
        expected_effect = ""
        if self.expected_effect:
            expected_effect == f"due to expected {self.expected_effect.display.lower()}"
        return f'Recommended {" and ".join(drugs)}{expected_effect}'
