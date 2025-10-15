import pghistory
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

import onconova.terminology.fields as termfields
import onconova.terminology.models as terminologies
from onconova.core.models import BaseModel
from onconova.oncology.models import PatientCase

class TumorMutationalBurdenStatusChoices(models.TextChoices):
    """
    An enumeration representing the possible statuses of Tumor Mutational Burden (TMB).

    Attributes:
        LOW: Indicates a low tumor mutational burden.
        HIGH: Indicates a high tumor mutational burden.
        INTERMEDIATE: Indicates an intermediate tumor mutational burden.
        INDETERMINATE: Indicates that the tumor mutational burden status cannot be determined.
    """
    LOW = "low"
    HIGH = "high"
    INTERMEDIATE = "intermediate"
    INDETERMINATE = "indeterminate"


class HomologousRecombinationDeficiencyInterpretationChoices(models.TextChoices):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    INDETERMINATE = "indeterminate"

class GenomicSignatureTypes(models.TextChoices):
    """
    Enumeration of genomic signature types used in oncology models.

    Attributes:
        TUMOR_MUTATIONAL_BURDEN: Represents the tumor mutational burden signature.
        LOSS_OF_HETEROZYGOSITY: Represents the loss of heterozygosity signature.
        MICROSATELLITE_INSTABILITY: Represents the microsatellite instability signature.
        HOMOLOGOUS_RECOMBINATION_DEFICIENCY: Represents the homologous recombination deficiency signature.
        TUMOR_NEOANTIGEN_BURDEN: Represents the tumor neoantigen burden signature.
        ANEUPLOID_SCORE: Represents the aneuploid score signature.
    """
    TUMOR_MUTATIONAL_BURDEN = "tumor_mutational_burden"
    LOSS_OF_HETEROZYGOSITY = "loss_of_heterozygosity"
    MICROSATELLITE_INSTABILITY = "microsatellite_instability"
    HOMOLOGOUS_RECOMBINATION_DEFICIENCY = "homologous_recombination_deficiency"
    TUMOR_NEOANTIGEN_BURDEN = "tumor_neoantigen_burden"
    ANEUPLOID_SCORE = "aneuploid_score"


class GenomicSignaturePresence(models.TextChoices):
    """
    An enumeration representing the presence status of a genomic signature.

    Attributes:
        POSITIVE (str): Indicates that the genomic signature is present.
        NEGATIVE (str): Indicates that the genomic signature is absent.
        INDETERMINATE (str): Indicates that the presence of the genomic signature cannot be determined.
    """
    POSITIVE = "positive"
    NEGATIVE = "negative"
    INDETERMINATE = "indeterminate"


@pghistory.track(
    obj_field=pghistory.ObjForeignKey(
        related_name="parent_events",
        related_query_name="parent_events",
    )
)
class GenomicSignature(BaseModel):
    """
    Represents a genomic signature assessment for a patient case.

    Attributes:
        case (ForeignKey): Reference to the PatientCase associated with this genomic signature.
        date (DateField): The date when the genomic signature was assessed.
        genomic_signature_type (str): Returns the type of genomic signature based on available attributes.
        description (str): Returns the description of the discriminated genomic signature, or 'Unknown genomic signature type' if not found.
    """

    case = models.ForeignKey(
        verbose_name=_("Patient case"),
        help_text=_("Indicates the case of the patient who's lifestyle is assesed"),
        to=PatientCase,
        related_name="genomic_signatures",
        on_delete=models.CASCADE,
    )
    date = models.DateField(
        verbose_name=_("Assessment date"),
        help_text=_(
            "Clinically-relevant date at which the patient's genomic signature was assessed."
        ),
    )

    @property
    def genomic_signature_type(self):
        for signature_type in GenomicSignatureTypes.values:
            try:
                getattr(self, signature_type)
                return signature_type
            except:
                continue

    def get_discriminated_genomic_signature(self) -> type["GenomicSignature"] | None:
        """
        Returns the discriminated genomic signature instance based on the value of `genomic_signature_type`.

        If `genomic_signature_type` is set, retrieves the corresponding attribute from the current instance.
        If not set, returns None.

        Returns:
            GenomicSignature | None: The discriminated genomic signature instance or None if not available.
        """
        if self.genomic_signature_type:
            return getattr(self, self.genomic_signature_type)
        return None

    @property
    def description(self):
        if signature := self.get_discriminated_genomic_signature():
            return signature.description
        return "Unknown genomic signature type"


@pghistory.track()
class TumorMutationalBurden(GenomicSignature):
    """
    Represents the Tumor Mutational Burden (TMB) genomic signature.

    Attributes:
        genomic_signature (models.OneToOneField[GenomicSignature]): One-to-one link to the base GenomicSignature.
        value (models.FloatField): The TMB value in mutations/Mb. Must be non-negative.
        status (models.CharField): Classification of the TMB status. Choices are 'low', 'high', 'intermediate', or 'indeterminate'.
        description (str): Returns a human-readable description of the TMB value.
    """
    
    genomic_signature = models.OneToOneField(
        to=GenomicSignature,
        on_delete=models.CASCADE,
        related_name=GenomicSignatureTypes.TUMOR_MUTATIONAL_BURDEN.value,
        parent_link=True,
        primary_key=True,
    )
    value = models.FloatField(
        verbose_name=_("Value"),
        help_text=_("The actual tumor mutational burden (TMB) value in mutations/Mb"),
        validators=[MinValueValidator(0)],
    )
    status = models.CharField(
        verbose_name=_("Status"),
        help_text=_("Cclassification of the tumor mutational burden (TMB) status"),
        choices=TumorMutationalBurdenStatusChoices,
        null=True,
        blank=True,
    )

    @property
    def description(self):
        return f"TMB: {self.value} Muts/Mb"


@pghistory.track()
class LossOfHeterozygosity(GenomicSignature):
    """
    Represents the Loss of Heterozygosity (LOH) genomic signature.

    Attributes:
        genomic_signature (models.OneToOneField[GenomicSignature]): One-to-one link to the base genomic signature.
        value (models.FloatField): LOH value as a percentage (0-100).
        description (str): Returns a human-readable description of the LOH value.
    """

    genomic_signature = models.OneToOneField(
        to=GenomicSignature,
        on_delete=models.CASCADE,
        related_name=GenomicSignatureTypes.LOSS_OF_HETEROZYGOSITY.value,
        parent_link=True,
        primary_key=True,
    )
    value = models.FloatField(
        verbose_name=_("Value"),
        help_text=_("Loss of heterozygosity (LOH) as a percentage"),
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )

    class Meta:
        verbose_name_plural = "Losses of Heterozygosity"

    @property
    def description(self):
        return f"LOH: {self.value} %"


@pghistory.track()
class MicrosatelliteInstability(GenomicSignature):
    """
    Represents the Microsatellite Instability (MSI) genomic signature.

    This model extends `GenomicSignature` and provides a classification for MSI status
    using a coded concept field. MSI is an important biomarker in oncology, indicating
    the presence of genetic hypermutability due to impaired DNA mismatch repair.

    Attributes:
        genomic_signature (models.OneToOneField[GenomicSignature]): One-to-one link to the base genomic signature.
        value (termfields.CodedConceptField[terminologies.MicrosatelliteInstabilityState]): MSI classification, based on a controlled terminology.
        description (str): Human-readable description of the MSI status.
    """

    genomic_signature = models.OneToOneField(
        to=GenomicSignature,
        on_delete=models.CASCADE,
        related_name=GenomicSignatureTypes.MICROSATELLITE_INSTABILITY.value,
        parent_link=True,
        primary_key=True,
    )
    value = termfields.CodedConceptField(
        verbose_name=_("Value"),
        help_text=_("Microsatellite instability (MSI) classification"),
        terminology=terminologies.MicrosatelliteInstabilityState,
    )

    class Meta:
        verbose_name_plural = "Microsatellite Instabilities"

    @property
    def description(self):
        return f"MSI: {self.value.display}"


@pghistory.track()
class HomologousRecombinationDeficiency(GenomicSignature):
    """
    Model representing Homologous Recombination Deficiency (HRD) as a genomic signature.

    Attributes:
        genomic_signature (models.OneToOneField[GenomicSignature]): One-to-one relationship to the base GenomicSignature model.
        value (models.FloatField): HRD score value, must be non-negative. Can be null or blank.
        interpretation (models.CharField[HomologousRecombinationDeficiencyPresence]): Interpretation of HRD status, can be 'positive', 'negative', or 'indeterminate'.
        description (str): Returns a string representation of the HRD value or interpretation.
    """
    
    genomic_signature = models.OneToOneField(
        to=GenomicSignature,
        on_delete=models.CASCADE,
        related_name=GenomicSignatureTypes.HOMOLOGOUS_RECOMBINATION_DEFICIENCY.value,
        parent_link=True,
        primary_key=True,
    )
    value = models.FloatField(
        verbose_name=_("Value"),
        help_text=_("Homologous recombination deficiency (HRD) score value"),
        validators=[MinValueValidator(0)],
        null=True,
        blank=True,
    )
    interpretation = models.CharField(
        verbose_name=_("Interpretation"),
        help_text=_("Homologous recombination deficiency (HRD) interpretation"),
        choices=HomologousRecombinationDeficiencyInterpretationChoices,
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name_plural = "Homologous Recombination Deficiencies"

    @property
    def description(self):
        return f"HRD: {self.value or self.interpretation}"


@pghistory.track()
class TumorNeoantigenBurden(GenomicSignature):
    """
    Represents the Tumor Neoantigen Burden (TNB) genomic signature.

    Attributes:
        genomic_signature (models.OneToOneField[GenomicSignature]): One-to-one relationship to the base GenomicSignature.
        value (models.FloatField): The measured TNB value in neoantigens per megabase. Must be non-negative.
        description (str): Returns a formatted string describing the TNB value.
    """

    genomic_signature = models.OneToOneField(
        to=GenomicSignature,
        on_delete=models.CASCADE,
        related_name=GenomicSignatureTypes.TUMOR_NEOANTIGEN_BURDEN.value,
        parent_link=True,
        primary_key=True,
    )
    value = models.FloatField(
        verbose_name=_("Value"),
        help_text=_("The actual tumor neoantigen burden (TNB) value in neoantigens/Mb"),
        validators=[MinValueValidator(0)],
    )

    @property
    def description(self):
        return f"TNB: {self.value} Neoant/Mb"


@pghistory.track()
class AneuploidScore(GenomicSignature):
    """
    Represents the Aneuploid Score (AS) genomic signature, which quantifies the total number of altered chromosomal arms.

    Attributes:
        genomic_signature (models.OneToOneField[GenomicSignature]): One-to-one relationship to the base GenomicSignature model.
        value (int): The actual aneuploid score, representing the number of altered arms (range: 0-39).
        description (str): Human-readable description of the aneuploid score.
    """

    genomic_signature = models.OneToOneField(
        to=GenomicSignature,
        on_delete=models.CASCADE,
        related_name=GenomicSignatureTypes.ANEUPLOID_SCORE.value,
        parent_link=True,
        primary_key=True,
    )
    value = models.SmallIntegerField(
        verbose_name=_("Value"),
        help_text=_("The actual aneuploid score (AS) value in total altered arms"),
        validators=[MinValueValidator(0), MaxValueValidator(39)],
    )

    @property
    def description(self):
        return f"AS: {self.value} arms"
