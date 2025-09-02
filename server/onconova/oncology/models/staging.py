import re

import pghistory
from django.db import models
from django.db.models import Case, OuterRef, Value, When
from django.utils.translation import gettext_lazy as _
from queryable_properties.properties import AnnotationProperty, SubqueryObjectProperty

import onconova.terminology.fields as termfields
import onconova.terminology.models as terminologies
from onconova.core.measures import MeasurementField, measures
from onconova.core.models import BaseModel
from onconova.oncology.models import NeoplasticEntity, PatientCase


class StagingDomain(models.TextChoices):
    """
    Enumeration of cancer staging domains used in oncology.

    Each member represents a specific staging system or classification used to describe the extent or severity of cancer.
    The available staging domains include:

    - TNM: Tumor, Node, Metastasis staging system.
    - FIGO: International Federation of Gynecology and Obstetrics staging.
    - BINET: Binet staging for chronic lymphocytic leukemia.
    - RAI: Rai staging for chronic lymphocytic leukemia.
    - BRESLOW: Breslow thickness for melanoma.
    - CLARK: Clark level for melanoma.
    - ISS: International Staging System for multiple myeloma.
    - RISS: Revised International Staging System for multiple myeloma.
    - INSS: International Neuroblastoma Staging System.
    - INRGSS: International Neuroblastoma Risk Group Staging System.
    - GLEASON: Gleason grading for prostate cancer.
    - RHABDO: Staging for rhabdomyosarcoma.
    - WILMS: Staging for Wilms tumor.
    - LYMPHOMA: Staging for lymphoma.

    This enumeration is used to standardize staging domain references throughout the application.
    """
    TNM = "tnm"
    FIGO = "figo"
    BINET = "binet"
    RAI = "rai"
    BRESLOW = "breslow"
    CLARK = "clark"
    ISS = "iss"
    RISS = "riss"
    INSS = "inss"
    INRGSS = "inrgss"
    GLEASON = "gleason"
    RHABDO = "rhabdomyosarcoma"
    WILMS = "wilms"
    LYMPHOMA = "lymphoma"


@pghistory.track(
    obj_field=pghistory.ObjForeignKey(
        related_name="parent_events",
        related_query_name="parent_events",
    )
)
class Staging(BaseModel):
    """
    Represents a staging record for a patient's cancer case, encapsulating the domain-specific staging information.

    Attributes:
        case (models.ForeignKey[PatientCase]): Reference to the PatientCase being staged.
        date (models.DateField): Date when the staging was performed and recorded.
        staged_entities (models.ManyToManyField[NeoplasticEntity]): References to neoplastic entities involved in the staging.
        description (str): Human-readable description of the staging, combining domain and stage value.
        stage_value (str | None): Extracted stage value from the domain-specific staging display string.
        staging_domain (str | None): The domain key corresponding to the staging information present.
    """

    STAGING_DOMAINS = {
        StagingDomain.TNM.value: "TNM Stage",
        StagingDomain.FIGO.value: "FIGO Stage",
        StagingDomain.BINET.value: "Binet Stage",
        StagingDomain.RAI.value: "RAI Stage",
        StagingDomain.BRESLOW.value: "Breslow Stage",
        StagingDomain.CLARK.value: "Clark Level",
        StagingDomain.ISS.value: "ISS Stage",
        StagingDomain.RISS.value: "RISS Stage",
        StagingDomain.INSS.value: "INSS Stage",
        StagingDomain.INRGSS.value: "Neuroblastoma INRGSS Stage",
        StagingDomain.GLEASON.value: "Prostate Gleason Group",
        StagingDomain.RHABDO.value: "Rhabdomyosarcoma Clinical Group",
        StagingDomain.WILMS.value: "Wilms Tumor Stage",
        StagingDomain.LYMPHOMA.value: "Lymphoma Stage",
    }

    case = models.ForeignKey(
        verbose_name=_("Patient case"),
        help_text=_("Indicates the case of the patient who's cancer is staged"),
        to=PatientCase,
        related_name="stagings",
        on_delete=models.CASCADE,
    )
    date = models.DateField(
        verbose_name=_("Staging date"),
        help_text=_(
            "Clinically-relevant date at which the staging was performed and recorded."
        ),
    )
    staged_entities = models.ManyToManyField(
        verbose_name=_("Staged neoplastic entities"),
        help_text=_(
            "References to the neoplastic entities that were the focus of the staging."
        ),
        to=NeoplasticEntity,
        related_name="stagings",
    )

    @property
    def description(self):
        if self.staging_domain:
            staging = self.STAGING_DOMAINS.get(self.staging_domain)
        else:
            staging = "Staging"
        return f"{staging} {self.stage_value}"

    @property
    def stage_value(self):
        regex = r"(?i).+(?:Stage| Level| Group Stage| Group )\s*([a-z0-9]+)(?:.*)"
        if not self.staging_domain:
            return None
        stage_string = getattr(self, self.staging_domain).stage.display
        matched = re.match(regex, stage_string)
        if matched:
            stage_value = matched.group(1)
        else:
            stage_value = stage_string
        return stage_value

    @property
    def staging_domain(self):
        for domain in self.STAGING_DOMAINS.keys():
            try:
                getattr(self, domain)
                return domain
            except:
                continue

    def get_domain_staging(self) -> type["Staging"] | None:
        if self.staging_domain:
            return getattr(self, self.staging_domain)
        else:
            return None


@pghistory.track()
class TNMStaging(Staging):
    """
    Model representing TNM cancer staging information.

    Attributes:
        staging (models.OneToOneField[Staging]): Link to the base Staging instance.
        stage (termfields.CodedConceptField[terminologies.TNMStage]): TNM stage classification.
        methodology (termfields.CodedConceptField[terminologies.TNMStagingMethod]): Methodology used for TNM staging.
        pathological (models.BooleanField): Indicates if staging is pathological (True) or clinical (False).
        primaryTumor (termfields.CodedConceptField[terminologies.TNMPrimaryTumorCategory]): T stage (extent of the primary tumor).
        regionalNodes (termfields.CodedConceptField[terminologies.TNMRegionalNodesCategory]): N stage (spread to regional lymph nodes).
        distantMetastases (termfields.CodedConceptField[terminologies.TNMDistantMetastasesCategory]): M stage (presence of distant metastasis).
        grade (termfields.CodedConceptField[terminologies.TNMGradeCategory]): G stage (grade of cancer cells).
        residualTumor (termfields.CodedConceptField[terminologies.TNMResidualTumorCategory]): R stage (extent of residual tumor cells post-operation).
        lymphaticInvasion (termfields.CodedConceptField[terminologies.TNMLymphaticInvasionCategory]): L stage (lymphatic vessel invasion).
        venousInvasion (termfields.CodedConceptField[terminologies.TNMVenousInvasionCategory]): V stage (venous vessel invasion).
        perineuralInvasion (termfields.CodedConceptField[terminologies.TNMPerineuralInvasionCategory]): Pn stage (adjunct nerve invasion).
        serumTumorMarkerLevel (termfields.CodedConceptField[terminologies.TNMSerumTumorMarkerLevelCategory]): S stage (serum tumor marker level).
    """

    staging = models.OneToOneField(
        to=Staging,
        on_delete=models.CASCADE,
        related_name=StagingDomain.TNM.value,
        parent_link=True,
        primary_key=True,
    )
    stage = termfields.CodedConceptField(
        verbose_name=_("TNM Stage"),
        help_text=_("The classification of the TNM stage"),
        terminology=terminologies.TNMStage,
    )
    methodology = termfields.CodedConceptField(
        verbose_name=_("TNM Staging methodology"),
        help_text=_("Methodology used for TNM staging"),
        terminology=terminologies.TNMStagingMethod,
        blank=True,
        null=True,
    )
    pathological = models.BooleanField(
        verbose_name=_("Pathological staging"),
        help_text=_(
            "Whether the staging was based on pathological (true) or clinical (false) evidence."
        ),
        null=True,
        blank=True,
    )
    primaryTumor = termfields.CodedConceptField(
        verbose_name=_("T Stage"),
        help_text=_("T stage (extent of the primary tumor)"),
        terminology=terminologies.TNMPrimaryTumorCategory,
        blank=True,
        null=True,
    )
    regionalNodes = termfields.CodedConceptField(
        verbose_name=_("N Stage"),
        help_text=_("N stage (degree of spread to regional lymph nodes)"),
        terminology=terminologies.TNMRegionalNodesCategory,
        blank=True,
        null=True,
    )
    distantMetastases = termfields.CodedConceptField(
        verbose_name=_("M Stage"),
        help_text=_("M stage (presence of distant metastasis)"),
        terminology=terminologies.TNMDistantMetastasesCategory,
        blank=True,
        null=True,
    )
    grade = termfields.CodedConceptField(
        verbose_name=_("G Stage"),
        help_text=_("G stage (grade of the cancer cells)"),
        terminology=terminologies.TNMGradeCategory,
        blank=True,
        null=True,
    )
    residualTumor = termfields.CodedConceptField(
        verbose_name=_("R Stage"),
        help_text=_("R stage (extent of residual tumor cells after operation)"),
        terminology=terminologies.TNMResidualTumorCategory,
        blank=True,
        null=True,
    )
    lymphaticInvasion = termfields.CodedConceptField(
        verbose_name=_("L Stage"),
        help_text=_("L stage (invasion into lymphatic vessels)"),
        terminology=terminologies.TNMLymphaticInvasionCategory,
        blank=True,
        null=True,
    )
    venousInvasion = termfields.CodedConceptField(
        verbose_name=_("V Stage"),
        help_text=_("V stage (invasion into venous vessels)"),
        terminology=terminologies.TNMVenousInvasionCategory,
        blank=True,
        null=True,
    )
    perineuralInvasion = termfields.CodedConceptField(
        verbose_name=_("Pn Stage"),
        help_text=_("Pn stage (invasion into adjunct nerves)"),
        terminology=terminologies.TNMPerineuralInvasionCategory,
        blank=True,
        null=True,
    )
    serumTumorMarkerLevel = termfields.CodedConceptField(
        verbose_name=_("S Stage"),
        help_text=_("S stage (serum tumor marker level)"),
        terminology=terminologies.TNMSerumTumorMarkerLevelCategory,
        blank=True,
        null=True,
    )


@pghistory.track()
class FIGOStaging(Staging):

    staging = models.OneToOneField(
        to=Staging,
        on_delete=models.CASCADE,
        related_name=StagingDomain.FIGO.value,
        parent_link=True,
        primary_key=True,
    )
    stage = termfields.CodedConceptField(
        verbose_name=_("FIGO Stage"),
        help_text=_("The value of the FIGO stage"),
        terminology=terminologies.FIGOStage,
    )
    methodology = termfields.CodedConceptField(
        verbose_name=_("FIGO staging methodology"),
        help_text=_("Methodology used for the FIGO staging"),
        terminology=terminologies.FIGOStagingMethod,
        null=True,
        blank=True,
    )


@pghistory.track()
class BinetStaging(Staging):
    """
    Model representing the Binet staging system for oncology.

    Attributes:
        staging (models.OneToOneField[Staging]): A one-to-one relationship to the base Staging model
        stage (termfields.CodedConceptField[terminologies.BinetStage]): The Binet stage value, represented as a coded concept field.
    """

    staging = models.OneToOneField(
        to=Staging,
        on_delete=models.CASCADE,
        related_name=StagingDomain.BINET.value,
        parent_link=True,
        primary_key=True,
    )
    stage = termfields.CodedConceptField(
        verbose_name=_("Binet Stage"),
        help_text=_("The value of the Binet stage"),
        terminology=terminologies.BinetStage,
    )


@pghistory.track()
class RaiStaging(Staging):
    """
    Model representing Rai staging for oncology patients.

    Attributes:
        staging (models.OneToOneField[Staging]): Links to the base Staging model, ensuring a one-to-one relationship.
        stage (termfields.CodedConceptField[terminologies.RaiStage]): Stores the Rai stage value using a coded concept field.
        methodology (termfields.CodedConceptField[terminologies.RaiStagingMethod]): Optionally records the methodology used for Rai staging.
    """

    staging = models.OneToOneField(
        to=Staging,
        on_delete=models.CASCADE,
        related_name=StagingDomain.RAI.value,
        parent_link=True,
        primary_key=True,
    )
    stage = termfields.CodedConceptField(
        verbose_name=_("Rai Stage"),
        help_text=_("The value of the Rai stage"),
        terminology=terminologies.RaiStage,
    )
    methodology = termfields.CodedConceptField(
        verbose_name=_("Rai staging methodology"),
        help_text=_("Methodology used for the Rai staging"),
        terminology=terminologies.RaiStagingMethod,
        null=True,
        blank=True,
    )


@pghistory.track()
class BreslowDepth(Staging):
    """
    Model representing Breslow depth staging for oncology.

    Attributes:
        staging (models.OneToOneField[Staging]): Links to the parent Staging instance, using Breslow staging domain.
        depth (MeasurementField[measures.Distance]): Breslow depth measurement of the tumor, in millimeters.
        is_ulcered (models.BooleanField): Indicates whether the primary tumor presents ulceration.
        _stage_code (AnnotationProperty): Annotated SNOMED code based on Breslow depth thresholds.
        stage (SubqueryObjectProperty[terminologies.BreslowDepthStage]): Related BreslowDepthStage object, resolved by SNOMED code.
    """

    staging = models.OneToOneField(
        to=Staging,
        on_delete=models.CASCADE,
        related_name=StagingDomain.BRESLOW.value,
        parent_link=True,
        primary_key=True,
    )
    depth = MeasurementField(
        verbose_name=_("Breslow depth"),
        help_text=_("Breslow depth"),
        measurement=measures.Distance,
        default_unit="mm",
    )
    is_ulcered = models.BooleanField(
        verbose_name="Ulcered",
        help_text=_("Whether the primary tumour presents ulceration"),
        null=True,
        blank=True,
    )
    _stage_code = AnnotationProperty(
        annotation=Case(
            When(depth__lt=0.76 / 1000, then=Value("86069005")),
            When(depth__gte=1.75 / 1000, then=Value("44815009")),
            default=Value("17456000"),
        )
    )
    stage = SubqueryObjectProperty(
        model=terminologies.BreslowDepthStage,
        queryset=lambda: terminologies.BreslowDepthStage.objects.filter(
            code=OuterRef("_stage_code")
        ),
        cached=True,
    )


@pghistory.track()
class ClarkStaging(Staging):
    """
    Represents the Clark staging model for oncology, extending the base Staging model.

    Attributes:
        staging (models.OneToOneField[Staging]): Links to the base Staging instance, using a one-to-one relationship.
        stage (termfields.CodedConceptField[terminologies.ClarkLevel]): Stores the Clark level stage as a coded concept, referencing the ClarkLevel terminology.
    """

    staging = models.OneToOneField(
        to=Staging,
        on_delete=models.CASCADE,
        related_name=StagingDomain.CLARK.value,
        parent_link=True,
        primary_key=True,
    )
    stage = termfields.CodedConceptField(
        verbose_name=_("Clark Level Stage"),
        help_text=_("The value of the Clark level stage"),
        terminology=terminologies.ClarkLevel,
    )


@pghistory.track()
class ISSStaging(Staging):
    """
    ISSStaging model represents the International Staging System (ISS) staging information for oncology cases.

    Attributes:
        staging (models.OneToOneField[Staging]): One-to-one relationship to the base Staging model, serving as the primary key.
        stage (termfields.CodedConceptField[terminologies.MyelomaISSStage]): Field storing the ISS stage value, using the Myeloma ISS terminology.
    """

    staging = models.OneToOneField(
        to=Staging,
        on_delete=models.CASCADE,
        related_name=StagingDomain.ISS.value,
        parent_link=True,
        primary_key=True,
    )
    stage = termfields.CodedConceptField(
        verbose_name=_("ISS Stage"),
        help_text=_("The value of theISS stage"),
        terminology=terminologies.MyelomaISSStage,
    )


@pghistory.track()
class RISSStaging(Staging):
    """
    Represents the Revised International Staging System (RISS) staging for oncology.

    Attributes:
        staging (models.OneToOneField[Staging]): Links to the base `Staging` model, using a one-to-one relationship.
        stage (termfields.CodedConceptField[terminologies.MyelomaRISSStage]): Stores the RISS stage as a coded concept, using the Myeloma RISS terminology.
    """

    staging = models.OneToOneField(
        to=Staging,
        on_delete=models.CASCADE,
        related_name=StagingDomain.RISS.value,
        parent_link=True,
        primary_key=True,
    )
    stage = termfields.CodedConceptField(
        verbose_name=_("RISS Stage"),
        help_text=_("The value of the RISS stage"),
        terminology=terminologies.MyelomaRISSStage,
    )


@pghistory.track()
class INSSStage(Staging):
    """
    Represents the International Neuroblastoma Staging System (INSS) stage for a neuroblastoma case.

    Attributes:
        staging (models.OneToOneField[Staging]): Link to the parent `Staging` instance.
        stage (termfields.CodedConceptField[terminologies.NeuroblastomaINSSStage]): The INSS stage value, coded using the Neuroblastoma INSS terminology.
    """

    staging = models.OneToOneField(
        to=Staging,
        on_delete=models.CASCADE,
        related_name=StagingDomain.INSS.value,
        parent_link=True,
        primary_key=True,
    )
    stage = termfields.CodedConceptField(
        verbose_name=_("INSS Stage"),
        help_text=_("The value of the INSS stage"),
        terminology=terminologies.NeuroblastomaINSSStage,
    )


@pghistory.track()
class INRGSSStage(Staging):
    """
    Represents the INRGSS (International Neuroblastoma Risk Group Staging System) stage for neuroblastoma patients.

    Attributes:
        staging (models.OneToOneField[Staging]): Links to the base Staging model, with cascade deletion and a custom related name.
        stage (termfields.CodedConceptField[terminologies.NeuroblastomaINRGSSStage]): Stores the INRGSS stage value, with terminology support for Neuroblastoma INRGSS stages.
    """

    staging = models.OneToOneField(
        to=Staging,
        on_delete=models.CASCADE,
        related_name=StagingDomain.INRGSS.value,
        parent_link=True,
        primary_key=True,
    )
    stage = termfields.CodedConceptField(
        verbose_name=_("INRGSS Stage"),
        help_text=_("The value of the INRGSS stage"),
        terminology=terminologies.NeuroblastomaINRGSSStage,
    )


@pghistory.track()
class GleasonGrade(Staging):
    """
    Represents the Gleason Grade staging model for oncology.

    Attributes:
        staging (models.OneToOneField[Staging]): Links to the parent `Staging` instance, using a one-to-one relationship.
        stage (termfields.CodedConceptField[terminologies.GleasonGradeGroupStage]): Stores the Gleason grade stage as a coded concept, using the GleasonGradeGroupStage terminology.
    """

    staging = models.OneToOneField(
        to=Staging,
        on_delete=models.CASCADE,
        related_name=StagingDomain.GLEASON.value,
        parent_link=True,
        primary_key=True,
    )
    stage = termfields.CodedConceptField(
        verbose_name=_("Gleason grade Stage"),
        help_text=_("The value of the Gleason grade stage"),
        terminology=terminologies.GleasonGradeGroupStage,
    )


@pghistory.track()
class WilmsStage(Staging):
    """
    Model representing the staging information for Wilms tumor.

    Attributes:
        staging (models.OneToOneField[Staging]): Links to the base `Staging` model, with cascade deletion and a custom related name.
        stage (termfields.CodedConceptField[terminologies.WilmsTumorStage]): Stores the Wilms tumor stage, using a controlled terminology.

    """

    staging = models.OneToOneField(
        to=Staging,
        on_delete=models.CASCADE,
        related_name=StagingDomain.WILMS.value,
        parent_link=True,
        primary_key=True,
    )
    stage = termfields.CodedConceptField(
        verbose_name=_("Wilms Stage"),
        help_text=_("The value of the Wilms stage"),
        terminology=terminologies.WilmsTumorStage,
    )


@pghistory.track()
class RhabdomyosarcomaClinicalGroup(Staging):
    """
    Model representing the clinical group staging for Rhabdomyosarcoma.

    Attributes:
        staging (models.OneToOneField[Staging]): Links to the base Staging model, ensuring a unique staging record per clinical group.
        stage (termfields.CodedConceptField[terminologies.RhabdomyosarcomaClinicalGroup]): Stores the clinical group classification for Rhabdomyosarcoma, using controlled terminology.
    """

    staging = models.OneToOneField(
        to=Staging,
        on_delete=models.CASCADE,
        related_name=StagingDomain.RHABDO.value,
        parent_link=True,
        primary_key=True,
    )
    stage = termfields.CodedConceptField(
        verbose_name=_("Rhabdomyosarcoma clinical group"),
        help_text=_("The value of the rhabdomyosarcoma clinical group"),
        terminology=terminologies.RhabdomyosarcomaClinicalGroup,
    )


@pghistory.track()
class LymphomaStaging(Staging):
    """
    Model representing the staging information for lymphoma.

    Attributes:
        staging (models.OneToOneField[Staging]): Link to the base Staging model, establishing a one-to-one relationship.
        stage (termfields.CodedConceptField[terminologies.LymphomaStage]): The specific stage of lymphoma, coded using a controlled terminology.
        methodology (termfields.CodedConceptField[terminologies.LymphomaStagingMethod]): The methodology used for determining the lymphoma stage, optional.
        bulky (models.BooleanField): Indicates the presence of bulky disease as a modifier, optional.
        pathological (models.BooleanField): Specifies whether staging was based on clinical or pathological evidence, optional.
        modifiers (termfields.CodedConceptField[terminologies.LymphomaStageValueModifier]): Additional coded qualifiers acting as modifiers for the lymphoma stage.
    """

    staging = models.OneToOneField(
        to=Staging,
        on_delete=models.CASCADE,
        related_name=StagingDomain.LYMPHOMA.value,
        parent_link=True,
        primary_key=True,
    )
    stage = termfields.CodedConceptField(
        verbose_name=_("Lymphoma Stage"),
        help_text=_("The value of the Lymphoma stage"),
        terminology=terminologies.LymphomaStage,
    )
    methodology = termfields.CodedConceptField(
        verbose_name=_("Lymphoma staging methodology"),
        help_text=_("Methodology used for the Lymphoma staging"),
        terminology=terminologies.LymphomaStagingMethod,
        null=True,
        blank=True,
    )
    bulky = models.BooleanField(
        verbose_name=_("Bulky disease modifier"),
        help_text=_(
            "Bulky modifier indicating if the lymphoma has the presence of bulky disease."
        ),
        null=True,
        blank=True,
    )
    pathological = models.BooleanField(
        verbose_name=_("Pathological staging"),
        help_text=_(
            "Whether the staging was based on clinical or pathologic evidence."
        ),
        null=True,
        blank=True,
    )
    modifiers = termfields.CodedConceptField(
        verbose_name=_("Lymphoma stage modifier"),
        help_text=_("Qualifier acting as modifier for the lymphoma stage"),
        terminology=terminologies.LymphomaStageValueModifier,
        multiple=True,
    )
