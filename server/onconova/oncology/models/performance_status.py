import pghistory
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Case, ExpressionWrapper, OuterRef, Q, Value, When
from django.utils.translation import gettext_lazy as _
from queryable_properties.managers import QueryablePropertiesManager
from queryable_properties.properties import SubqueryObjectProperty

import onconova.terminology.models as terminologies
from onconova.core.models import BaseModel
from onconova.oncology.models import PatientCase

ECOG_INTEPRETATION = {
    0: "LA9622-7",
    1: "LA9623-5",
    2: "LA9624-3",
    3: "LA9625-0",
    4: "LA9626-8",
    5: "LA9627-6",
}

KARNOFSKY_INTEPRETATION = {
    0: "LA9627-6",
    10: "LA29184-1",
    20: "LA29183-3",
    30: "LA29182-5",
    40: "LA29181-7",
    50: "LA29180-9",
    60: "LA29179-1",
    70: "LA29178-3",
    80: "LA29177-5",
    90: "LA29176-7",
    100: "LA29175-9",
}


@pghistory.track()
class PerformanceStatus(BaseModel):
    """Model representing a patient's performance status assessment, supporting both ECOG and Karnofsky scoring systems.

    Attributes:
        objects (QueryablePropertiesManager): Custom manager for queryable properties.
        case (models.ForeignKey[PatientCase]): Reference to the patient case being assessed.
        date (models.DateField): Date of the performance status assessment.
        ecog_score (models.PositiveSmallIntegerField): ECOG Performance Status Score (0-5).
        karnofsky_score (models.PositiveSmallIntegerField): Karnofsky Performance Status Score (0-100).
        ecog_interpretation (SubqueryObjectProperty[terminologies.ECOGPerformanceStatusInterpretation]): Interpretation of the ECOG score using standardized terminology.
        karnofsky_interpretation (SubqueryObjectProperty[terminologies.KarnofskyPerformanceStatusInterpretation]): Interpretation of the Karnofsky score using standardized terminology.
        description (str): Returns a string description of the performance status based on available score.

    Constraints: 
        Ensures at least one of ECOG or Karnofsky scores is set.

    References:
        - Oken et al., Am. J. Clin. Oncol. 5(6):649-655, 1982.
    """

    objects = QueryablePropertiesManager()

    case = models.ForeignKey(
        verbose_name=_("Patient case"),
        help_text=_(
            "Indicates the case of the patient who's performance status is assesed"
        ),
        to=PatientCase,
        related_name="performance_status",
        on_delete=models.CASCADE,
    )
    date = models.DateField(
        verbose_name=_("Assessment date"),
        help_text=_(
            "Clinically-relevant date at which the performance score was performed and recorded."
        ),
    )
    ecog_score = models.PositiveSmallIntegerField(
        verbose_name=_("ECOG Score"),
        help_text=_("ECOG Performance Status Score"),
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        blank=True,
        null=True,
    )
    karnofsky_score = models.PositiveSmallIntegerField(
        verbose_name=_("Karnofsky Score"),
        help_text=_("Karnofsky Performance Status Score"),
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        blank=True,
        null=True,
    )
    ecog_interpretation = SubqueryObjectProperty(
        model=terminologies.ECOGPerformanceStatusInterpretation,
        queryset=lambda: terminologies.ECOGPerformanceStatusInterpretation.objects.annotate(
            ecog=ExpressionWrapper(
                OuterRef("ecog_score"), output_field=models.PositiveSmallIntegerField()
            )
        ).filter(
            code=Case(
                When(ecog=0, then=Value("LA9622-7")),
                When(ecog=1, then=Value("LA9623-5")),
                When(ecog=2, then=Value("LA9624-3")),
                When(ecog=3, then=Value("LA9625-0")),
                When(ecog=4, then=Value("LA9626-8")),
                When(ecog=5, then=Value("LA9627-6")),
                default=None,
            )
        ),
        cached=True,
    )
    karnofsky_interpretation = SubqueryObjectProperty(
        model=terminologies.KarnofskyPerformanceStatusInterpretation,
        queryset=lambda: terminologies.KarnofskyPerformanceStatusInterpretation.objects.annotate(
            karnofsky=ExpressionWrapper(
                OuterRef("karnofsky_score"),
                output_field=models.PositiveSmallIntegerField(),
            )
        ).filter(
            code=Case(
                When(karnofsky=0, then=Value("LA9627-6")),
                When(karnofsky=10, then=Value("LA29184-1")),
                When(karnofsky=20, then=Value("LA29183-3")),
                When(karnofsky=30, then=Value("LA29182-5")),
                When(karnofsky=40, then=Value("LA29181-7")),
                When(karnofsky=50, then=Value("LA29180-9")),
                When(karnofsky=60, then=Value("LA29179-1")),
                When(karnofsky=70, then=Value("LA29178-3")),
                When(karnofsky=80, then=Value("LA29177-5")),
                When(karnofsky=90, then=Value("LA29176-7")),
                When(karnofsky=100, then=Value("LA29175-9")),
                default=None,
            )
        ),
        cached=True,
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=models.Q(ecog_score__isnull=False)
                | models.Q(karnofsky_score__isnull=False),
                name="at_least_one_score_must_be_set",
            )
        ]

    @property
    def description(self):
        if self.ecog_score is not None:
            return f"ECOG: {self.ecog_score}"
        elif self.karnofsky_score is not None:
            return f"Karnofsky: {self.karnofsky_score}"

    def convert_karnofsky_to_ecog(self) -> int:
        """
        Reference
        ---------
        [1] Oken et al., Am. J. Clin. Oncol. 5(6):649-655, 1982.
        """
        if self.ecog_score is not None:
            return self.ecog_score
        if self.karnofsky_score:
            if self.karnofsky_score == 100:
                return 0
            elif self.karnofsky_score >= 80:
                return 1
            elif self.karnofsky_score >= 60:
                return 2
            elif self.karnofsky_score >= 40:
                return 3
            elif self.karnofsky_score >= 20:
                return 4
            elif self.karnofsky_score == 0:
                return 5
        raise ValueError("Neither an ECOG nor Karnofksy value exist.")
