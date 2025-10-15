import pghistory
from django.db import models
from django.db.models import OuterRef
from django.db.models.functions import Left
from django.utils.translation import gettext_lazy as _
from queryable_properties.managers import QueryablePropertiesManager
from queryable_properties.properties import SubqueryObjectProperty

import onconova.terminology.fields as termfields
import onconova.terminology.models as terminologies
from onconova.core.models import BaseModel
from onconova.oncology.models import PatientCase

PRIMARY = "primary"
METASTATIC = "metastatic"
LOCAL_RECURRENCE = "local_recurrence"
REGIONAL_RECURRENCE = "regional_recurrence"


class NeoplasticEntityRelationshipChoices(models.TextChoices):
    """
    An enumeration of possible relationships between neoplastic entities.

    Attributes:
        PRIMARY: Indicates the neoplastic entity is a primary tumor.
        METASTATIC: Indicates the neoplastic entity is a metastasis.
        LOCAL_RECURRENCE: Indicates the neoplastic entity is a local recurrence of a previous tumor.
        REGIONAL_RECURRENCE: Indicates the neoplastic entity is a regional recurrence of a previous tumor.
    """
    PRIMARY = PRIMARY
    METASTATIC = METASTATIC
    LOCAL_RECURRENCE = LOCAL_RECURRENCE
    REGIONAL_RECURRENCE = REGIONAL_RECURRENCE


@pghistory.track()
class NeoplasticEntity(BaseModel):
    """
    Represents a neoplastic entity (tumor or neoplasm) associated with a patient case, including its anatomical location, morphology, relationship to other neoplasms, and additional qualifiers.

    Attributes:
        objects (QueryablePropertiesManager): Manager for queryable properties.
        case (models.ForeignKey[PatientCase]): Reference to the patient case associated with the neoplasm.
        relationship (models.CharField[NeoplasticEntityRelationship]): Relationship linking secondary and recurrent tumors to their primary origin or distinguishing disease phases.
        related_primary (models.ForeignKey[NeoplasticEntity]): Reference to the primary neoplasm from which this neoplasm originated (nullable).
        assertion_date (models.DateField): Date when the existence of the neoplasm was first asserted.
        topography (termfields.CodedConceptField[terminologies.CancerTopography]): Anatomical location of the neoplasm.
        morphology (termfields.CodedConceptField[terminologies.CancerMorphology]): Cell type and biologic activity of the tumor.
        topography_group (SubqueryObjectProperty[terminologies.CancerTopography]): Grouping of topography codes for classification.
        differentiation (termfields.CodedConceptField[terminologies.CancerDifferentiation]): Morphologic differentiation characteristics (nullable).
        laterality (termfields.CodedConceptField[terminologies.CancerLaterality]): Laterality qualifier for the neoplasm's location (nullable).
        description (str): Human-readable description of the neoplastic entity, including morphology, topography, laterality, differentiation, and relationship.

    Constraints:
        Ensures that a primary neoplasm cannot have a related primary.
    """

    objects = QueryablePropertiesManager()

    case = models.ForeignKey(
        verbose_name=_("Patient case"),
        help_text=_("Indicates the case of the patient who's neoplasm(s) are recorded"),
        to=PatientCase,
        related_name="neoplastic_entities",
        on_delete=models.CASCADE,
    )
    relationship = models.CharField(
        verbose_name=_("Neoplastic relationship"),
        help_text=_(
            "Relationship linking secondary and recurrent tumors to their primary origin or for distinguishing between different phases of the disease."
        ),
        max_length=30,
        choices=NeoplasticEntityRelationshipChoices,
    )
    related_primary = models.ForeignKey(
        verbose_name=_("Related primary neoplasm"),
        help_text=_(
            "Reference to the primary neoplasm of which the neoplasm(s) originated from."
        ),
        to="self",
        related_name="recurrences",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    assertion_date = models.DateField(
        verbose_name=_("Assertion date"),
        help_text=_(
            "The date on which the existence of the neoplasm(s) was first asserted or acknowledged"
        ),
    )
    topography = termfields.CodedConceptField(
        verbose_name=_("Topography"),
        help_text=_("Anatomical location of the neoplasm(s)"),
        terminology=terminologies.CancerTopography,
    )
    morphology = termfields.CodedConceptField(
        verbose_name=_("Morphology"),
        help_text=_(
            "Describes the cell type of the tumor and its biologic activity, in other words, the characteristics of the tumor itself"
        ),
        terminology=terminologies.CancerMorphology,
    )
    topography_group = SubqueryObjectProperty(
        model=terminologies.CancerTopographyGroup,
        queryset=lambda: terminologies.CancerTopographyGroup.objects.filter(
            code=Left(OuterRef("topography__code"), 3)  # type: ignore
        ),
        cached=True,
    )
    differentitation = termfields.CodedConceptField(
        verbose_name=_("Differentiation"),
        help_text=_("Morphologic differentitation characteristics of the neoplasm(s)"),
        terminology=terminologies.HistologyDifferentiation,
        null=True,
        blank=True,
    )
    laterality = termfields.CodedConceptField(
        verbose_name=_("Laterality"),
        help_text=_("Laterality qualifier for the location of the neoplasm(s)"),
        terminology=terminologies.LateralityQualifier,
        null=True,
        blank=True,
    )

    @property
    def description(self):
        """
        Human-readable description of the neoplastic entity
        """
        # Get core information
        morphology = (
            str(self.morphology)
            .lower()
            .replace(", nos", "")
            .replace(", metastatic", "")
        )
        topography = (
            str(self.topography)
            .lower()
            .replace(", nos", "")
            .replace(", metastatic", "")
        )
        # If the neoplasm has specified laterality, add it to the topography
        if self.laterality:
            laterality = str(self.laterality).lower().replace(" (qualifier value)", "")
            topography = f"{laterality} {topography}"
        # If the neoplasm has a specified differentations, categorize it into grading
        if self.differentitation:
            diff_code = self.differentitation.code
            grading = (
                "Low-grade"
                if diff_code in ["1", "2"]
                else (
                    "High-grade"
                    if diff_code in ["3", "4"]
                    else str(self.differentitation).split(",")[-1]
                )
            )
            morphology = f"{grading} {morphology}"
        # Adapt the word composition to whether the topography is described by a single word or not
        if len(topography.split()) == 1:
            description = f"{topography} {morphology}"
        else:
            description = f"{morphology} of the {topography}"
        # Add the relationship/role of the neoplasm
        description = f"{self.relationship.replace('_',' ')} {description}"
        return description.capitalize()

    class Meta:
        verbose_name = "Neoplastic Entity"
        verbose_name_plural = "Neoplastic Entities"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(relationship="primary", related_primary=None)
                | ~models.Q(relationship="primary"),
                name="primary_cannot_have_a_related_primary",
                violation_error_message="A primary neoplasm cannot have a related primary",
            )
        ]
