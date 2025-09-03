import pghistory
from django.contrib.postgres.fields import ArrayField
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

import onconova.terminology.fields as termfields
import onconova.terminology.models as terminologies
from onconova.core.models import BaseModel
from onconova.oncology.models import PatientCase
from onconova.oncology.models.genomic_signature import GenomicSignature
from onconova.oncology.models.genomic_variant import GenomicVariant
from onconova.oncology.models.neoplastic_entity import NeoplasticEntity
from onconova.oncology.models.tumor_marker import TumorMarker


class TumorBoardSpecialties(models.TextChoices):
    """
    An enumeration of specialties relevant to a tumor board.

    Attributes:
        UNSPECIFIED: Represents an unspecified specialty.
        MOLECULAR: Represents the molecular specialty.
    """
    UNSPECIFIED = "unspecified"
    MOLECULAR = "molecular"


@pghistory.track(
    obj_field=pghistory.ObjForeignKey(
        related_name="parent_events",
        related_query_name="parent_events",
    )
)
class TumorBoard(BaseModel):
    """
    Represents a tumor board meeting associated with a patient case.

    Attributes:
        case (models.ForeignKey[PatientCase]): Reference to the patient case discussed at the tumor board.
        date (models.DateField): Date of the tumor board meeting or when recommendations were provided.
        related_entities (models.ManyToManyField[NeoplasticEntity]): Neoplastic entities that were the focus of the tumor board.
        recommendations (termfields.CodedConceptField[terminologies.TumorBoardRecommendation]): Recommendations provided by the board regarding patient care.
        tumor_board_specialty (str): Returns the specialty type of the tumor board, if available.
        specialized_tumor_board (TumorBoard): Returns the specialized tumor board instance based on its specialty.
        description (str): Returns a description of the tumor board, either from the specialized board or a summary of recommendations.
    """

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
    """
    Represents a specialized TumorBoard instance with unspecified specialties.

    This model extends the TumorBoard model using a one-to-one relationship,
    serving as a proxy for tumor boards that do not have a specified specialty.

    Attributes:
        tumor_board (models.OneToOneField[TumorBoard]): The associated TumorBoard instance, acting as the primary key for this model.
    """

    tumor_board = models.OneToOneField(
        to=TumorBoard,
        on_delete=models.CASCADE,
        related_name=TumorBoardSpecialties.UNSPECIFIED.value,
        parent_link=True,
        primary_key=True,
    )


@pghistory.track()
class MolecularTumorBoard(TumorBoard):
    """
    Represents a Molecular Tumor Board, a specialized tumor board focused on molecular diagnostics and characterization.

    Attributes:
        tumor_board (models.OneToOneField[TumorBoard]): Links to the base TumorBoard instance, serving as the primary key.
        conducted_molecular_comparison (models.BooleanField): Indicates if a molecular comparison was conducted during the board meeting.
        molecular_comparison_match (models.ForeignKey[NeoplasticEntity]): References the neoplastic entity matched during molecular comparison.
        conducted_cup_characterization (models.BooleanField): Indicates if a cancer of unknown primary (CUP) characterization was performed.
        characterized_cup (models.BooleanField): Indicates if the CUP characterization was successful.
        reviewed_reports (models.ArrayField[models.CharField]): List of genomic reports reviewed during the board meeting.
        description (str): Returns a summary of the board review, including the number of recommendations.
    """

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
        help_text=_("List of genomic reports reviewed during the board meeting."),
        base_field=models.CharField(
            max_length=500,
        ),
        blank=True,
        default=list,
    )

    @property
    def description(self):
        recommendations = (
            self.therapeutic_recommendations.count() + self.recommendations.count()  # type: ignore
        )
        if recommendations == 0:
            recommendations = "no"
        return f"MTB review with {recommendations} recommendations"


@pghistory.track()
class MolecularTherapeuticRecommendation(BaseModel):
    """
    Represents a therapeutic recommendation issued by a molecular tumor board, including recommended drugs, expected effects, clinical trial enrollment, and supporting molecular evidence.

    Attributes:
        molecular_tumor_board (models.ForeignKey[MolecularTumorBoard]): Reference to the molecular tumor board where the recommendation was issued.
        expected_effect (termfields.CodedConceptField[terminologies.ExpectedDrugAction]): Classification of the expected effect of the recommended drug(s).
        clinical_trial (models.CharField): NCT-Identifier of the recommended clinical trial for patient enrollment.
        drugs (termfields.CodedConceptField[terminologies.AntineoplasticAgent]): Drug(s) being recommended, classified as antineoplastic agents.
        off_label_use (models.BooleanField): Indicates if the recommended medication(s) are off-label.
        within_soc (models.BooleanField): Indicates if the recommended medication(s) are within standard of care.
        supporting_genomic_variants (models.ManyToManyField[GenomicVariant]): Genomic variants supporting the recommendation.
        supporting_genomic_signatures (models.ManyToManyField[GenomicSignature]): Genomic signatures supporting the recommendation.
        supporting_tumor_markers (models.ManyToManyField[TumorMarker]): Tumor markers supporting the recommendation.
        supporting (list): Aggregated supporting genomic variants, signatures, and tumor markers.
        description (str): Human-readable summary of the recommendation, including drugs and expected effect.
    """

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
            expected_effect = f"due to expected {str(self.expected_effect).lower()}"
        return f'Recommended {" and ".join(drugs)}{expected_effect}'
