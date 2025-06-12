import pghistory
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator

from pop.core.models import BaseModel
from pop.oncology.models import PatientCase
import pop.terminology.fields as termfields
import pop.terminology.models as terminologies


class GenomicSignatureTypes(models.TextChoices):
    TUMOR_MUTATIONAL_BURDEN = "tumor_mutational_burden"
    LOSS_OF_HETEROZYGOSITY = "loss_of_heterozygosity"
    MICROSATELLITE_INSTABILITY = "microsatellite_instability"
    HOMOLOGOUS_RECOMBINATION_DEFICIENCY = "homologous_recombination_deficiency"
    TUMOR_NEOANTIGEN_BURDEN = "tumor_neoantigen_burden"
    ANEUPLOID_SCORE = "aneuploid_score"


class GenomicSignaturePresence(models.TextChoices):
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

    def get_discriminated_genomic_signature(self):
        return getattr(self, self.genomic_signature_type)

    @property
    def description(self):
        return self.get_discriminated_genomic_signature().description


@pghistory.track()
class TumorMutationalBurden(GenomicSignature):

    class TumorMutationalBurdenStatus(models.TextChoices):
        LOW = "low"
        HIGH = "high"
        INTERMEDIATE = "intermediate"
        INDETERMINATE = "indeterminate"

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
        choices=TumorMutationalBurdenStatus,
        null=True,
        blank=True,
    )

    @property
    def description(self):
        return f"TMB: {self.value} Muts/Mb"


@pghistory.track()
class LossOfHeterozygosity(GenomicSignature):

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

    class HomologousRecombinationDeficiencyPresence(models.TextChoices):
        POSITIVE = "positive"
        NEGATIVE = "negative"
        INDETERMINATE = "indeterminate"

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
        choices=HomologousRecombinationDeficiencyPresence,
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
