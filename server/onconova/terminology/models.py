from typing import ClassVar, List

from django.contrib.postgres import fields as postgres
from django.contrib.postgres.fields import IntegerRangeField
from django.db import models
from django.db.models.functions import Concat
from django.utils.translation import gettext_lazy as _
from queryable_properties.managers import QueryablePropertiesManager
from queryable_properties.properties import AnnotationProperty

from onconova.core.models import BaseModel
from onconova.terminology.utils import CodedConcept as CodedConceptSchema


class CodedConcept(BaseModel):
    """
    Abstract Django model representing a coded concept from a terminology system.

    Attributes:
        code (models.CharField): The code as defined in the code system.
        display (models.CharField): Human-readable representation defined by the system.
        system (models.CharField): Canonical URL of the code system.
        version (models.CharField): Version of the code system.
        synonyms (models.ArrayField[models.CharField]): List of synonyms for the concept.
        parent (models.ForeignKey[CodedConcept]): Reference to a parent concept (self-referential).
        definition (models.TextField): Optional detailed definition of the concept.
        properties (models.JSONField): Additional properties as a JSON object.
        valueset (str): Class variable for the associated value set (to be defined in subclasses).
        codesystem (str): Class variable for the associated code system (to be defined in subclasses).
        extension_concepts (list): List of extension concepts.


    Constraints:
        
        - unique_together: Ensures uniqueness for code and system pairs.

    """
    code = models.CharField(
        verbose_name="Code",
        help_text=_("Code as defined in the code system"),
        max_length=200,
    )
    display = models.CharField(
        verbose_name="Text",
        help_text=_("Human-readable representation defined by the system"),
        max_length=2000,
        blank=True,
        null=True,
    )
    system = models.CharField(
        verbose_name="Codesystem",
        help_text=_("Canonical URL of the code system"),
        blank=True,
        null=True,
    )
    version = models.CharField(
        verbose_name="Version",
        help_text=_("Version of the code system"),
        max_length=200,
        blank=True,
        null=True,
    )
    synonyms = postgres.ArrayField(
        base_field=models.CharField(
            max_length=2000,
        ),
        default=list,
    )
    parent = models.ForeignKey(
        to="self",
        on_delete=models.CASCADE,
        related_name="children",
        null=True,
        blank=True,
    )
    definition = models.TextField(
        blank=True,
        null=True,
    )
    properties = models.JSONField(null=True, blank=True)

    valueset: ClassVar[str]
    codesystem: ClassVar[str]
    extension_concepts = []

    @classmethod
    def _concept_display_postprocessing(cls, display: str) -> str:
        return display

    @classmethod
    def _concept_postprocessing(cls, concept: CodedConceptSchema) -> CodedConceptSchema:
        return concept

    class Meta:
        unique_together = ["code", "system"]
        abstract = True

    def __str__(self):
        if self.display:
            return self.display
        else:
            return f"{self.__class__.__name__}: {self.code}"


class FamilyMemberType(CodedConcept):
    """
    Represents a coded concept for family member types based on the HL7 v3 FamilyMember ValueSet.

    Attributes:
        valueset (str): The URI for the HL7 v3 FamilyMember ValueSet.

    Methods:
        _concept_display_postprocessing(display: str) -> str:
            Post-processes the display string for a concept by converting it to title case.
    """
    valueset = "http://terminology.hl7.org/ValueSet/v3-FamilyMember"

    @classmethod
    def _concept_display_postprocessing(cls, display: str) -> str:
        return display.title()


class AlcoholConsumptionFrequency(CodedConcept):
    """
    Represents the frequency of alcohol consumption as a coded concept.

    This class uses the LOINC valueset "https://loinc.org/LL2179-1/" to standardize
    the representation of alcohol consumption frequency. The display string for each
    concept is post-processed to use title case formatting.

    Attributes:
        valueset (str): URL of the LOINC valueset for alcohol consumption frequency.

    Methods:
        _concept_display_postprocessing(display: str) -> str:
            Converts the display string to title case.
    """
    valueset = "https://loinc.org/LL2179-1/"

    @classmethod
    def _concept_display_postprocessing(cls, display: str) -> str:
        return display.title()


class AdministrativeGender(CodedConcept):
    """
    Represents a coded concept for administrative gender.

    Attributes:
        valueset (str): The URI for the administrative gender ValueSet.
    """
    valueset = "http://hl7.org/fhir/ValueSet/administrative-gender"


class ProcedureOutcome(CodedConcept):
    """
    Represents a coded concept for procedure outcome.

    Attributes:
        valueset (str): The URI for the procedure outcome ValueSet.
    """
    valueset = "http://hl7.org/fhir/ValueSet/procedure-outcome"


class LateralityQualifier(CodedConcept):
    """
    Represents a laterality qualifier concept, typically used in medical coding to specify the side (left, right, bilateral) of a body part or condition.

    Attributes:
        valueset (str): The URL of the HL7 FHIR value set for laterality qualifiers.

    Methods:
        _concept_display_postprocessing(display: str) -> str:
            Removes the suffix " (qualifier value)" from the concept display string for cleaner presentation.
    """
    valueset = "http://hl7.org/fhir/us/mcode/ValueSet/mcode-laterality-qualifier-vs"

    @classmethod
    def _concept_display_postprocessing(cls, display: str) -> str:
        return display.replace(" (qualifier value)", "")


class CancerTopography(CodedConcept):
    """
    Represents a coded concept for cancer topography based on ICD-O-3.

    Attributes:
        codesystem (str): The URI for the ICD-O-3 topography code system.
    """
    codesystem = "http://terminology.hl7.org/CodeSystem/icd-o-3-topography"


class CancerTopographyGroup(CancerTopography):
    """
    Proxy model for cancer topography groups, excluding codes containing a period.

    Attributes:
        objects (Manager): Custom manager to filter topography groups.
    """
    class QuerysetManager(models.Manager):
        def get_queryset(self):
            return super().get_queryset().exclude(code__contains=".")

    objects = QuerysetManager()

    class Meta:
        proxy = True


class CancerMorphology(CodedConcept):
    """
    Represents a coded concept for cancer morphology based on ICD-O-3.

    Attributes:
        codesystem (str): The URI for the ICD-O-3 morphology code system.
    """
    codesystem = "http://terminology.hl7.org/CodeSystem/icd-o-3-morphology"


class CancerMorphologyPrimary(CancerMorphology):
    """
    Proxy model for primary cancer morphology (codes ending with /3).

    Attributes:
        objects (Manager): Custom manager to filter primary morphologies.
    """
    class QuerysetManager(models.Manager):
        def get_queryset(self):
            return super().get_queryset().filter(code__endswith="/3")

    objects = QuerysetManager()

    class Meta:
        proxy = True


class CancerMorphologyMetastatic(CancerMorphology):
    """
    Proxy model for metastatic cancer morphology (codes ending with /6).

    Attributes:
        objects (Manager): Custom manager to filter metastatic morphologies.
    """
    class QuerysetManager(models.Manager):
        def get_queryset(self):
            return super().get_queryset().filter(code__endswith="/6")

    objects = QuerysetManager()

    class Meta:
        proxy = True


class HistologyDifferentiation(CodedConcept):
    """
    Represents a coded concept for histology differentiation.

    Attributes:
        codesystem (str): The URI for the ICD-O-3 differentiation code system.
    """
    codesystem = "http://terminology.hl7.org/CodeSystem/icd-o-3-differentiation"


class BodyLocationQualifier(CodedConcept):
    """
    Represents a coded concept for body location qualifier.

    Attributes:
        valueset (str): The URI for the body location qualifier ValueSet.
    """
    valueset = "http://hl7.org/fhir/us/mcode/ValueSet/mcode-body-location-qualifier-vs"


class GenderIdentity(CodedConcept):
    """
    Represents a coded concept for gender identity.

    Attributes:
        valueset (str): The URI for the gender identity ValueSet.
    """
    valueset = "https://loinc.org/LL3322-6/"


class ECOGPerformanceStatusInterpretation(CodedConcept):
    """
    Represents a coded concept for ECOG performance status interpretation.

    Attributes:
        valueset (str): The URI for the ECOG performance status ValueSet.
    """
    valueset = "https://loinc.org/LL529-9/"


class KarnofskyPerformanceStatusInterpretation(CodedConcept):
    """
    Represents a coded concept for Karnofsky performance status interpretation.

    Attributes:
        valueset (str): The URI for the Karnofsky performance status ValueSet.
    """
    valueset = "https://loinc.org/LL4986-7/"


class TreatmentTerminationReason(CodedConcept):
    """
    Represents a coded concept for reasons why a treatment was terminated.

    Attributes:
        valueset (str): URL to the FHIR ValueSet defining valid treatment termination reasons.

    Methods:
        _concept_display_postprocessing(display: str) -> str:
            Processes the display string for a concept by removing any text following ' ('.
    """
    valueset = "https://simplifier.net/onconova/ValueSets/onconova-treatment-termination-reason"

    @classmethod
    def _concept_display_postprocessing(cls, display: str) -> str:
        return display.split(" (")[0]


class AntineoplasticAgent(CodedConcept):
    """
    Represents a coded concept for antineoplastic agents.

    Attributes:
        therapy_category (CharField): Classification of therapy.
    """
    class TherapyCategory(models.TextChoices):
        CHEMOTHERAPY = "chemotherapy"
        IMMUNOTHERAPY = "immunotherapy"
        HORMONE_THERAPY = "hormone-therapy"
        TARGETED_THERAPY = "targeted-therapy"
        ANTIMETASTATIC_THERAPY = "antimetastatic_therapy"
        METABOLIC_THERAPY = "metabolic-therapy"
        RADIOPHARMACEUTICAL_THERAPY = "radiopharmaceutical-therapy"
        UNCLASSIFIED = "unclassified"

    therapy_category = models.CharField(
        verbose_name=_("Therapy classification"),
        help_text=_("Therapy classification"),
        choices=TherapyCategory,
        default=TherapyCategory.UNCLASSIFIED,
        max_length=50,
        null=True,
        blank=True,
    )

    @classmethod
    def _concept_display_postprocessing(cls, display: str) -> str:
        return display.capitalize()


class DosageRoute(CodedConcept):
    """
    Represents a coded concept for dosage route.

    Attributes:
        valueset (str): The URI for the route codes ValueSet.
    """
    valueset = "http://hl7.org/fhir/ValueSet/route-codes"


class SurgicalProcedure(CodedConcept):
    """
    Represents a coded concept for surgical procedures.

    Attributes:
        valueset (str): The URI for the surgical procedures ValueSet.
    """
    valueset = "https://simplifier.net/onconova/ValueSets/onconova-surgical-procedures"



class RadiotherapyModality(CodedConcept):
    """
    Represents a coded concept for radiotherapy modality.

    Attributes:
        valueset (str): The URL of the radiotherapy modality value set.

    Methods:
        _concept_display_postprocessing(display: str) -> str:
            Removes the " (procedure)" suffix from the display name of the concept.
    """
    valueset = "http://hl7.org/fhir/us/mcode/ValueSet/mcode-radiotherapy-modality-vs"

    @classmethod
    def _concept_display_postprocessing(cls, display: str) -> str:
        return display.replace(" (procedure)", "")


class RadiotherapyTechnique(CodedConcept):
    """
    Represents a coded concept for a radiotherapy technique.

    Attributes:
        valueset (str): The canonical URL for the radiotherapy technique value set, 
            as defined by HL7 FHIR mCODE.

    Methods:
        _concept_display_postprocessing(display: str) -> str:
            Removes the suffix " (procedure)" from the concept display string.
    """
    valueset = "http://hl7.org/fhir/us/mcode/ValueSet/mcode-radiotherapy-technique-vs"

    @classmethod
    def _concept_display_postprocessing(cls, display: str) -> str:
        return display.replace(" (procedure)", "")


class RadiotherapyVolumeType(CodedConcept):
    """
    Represents a coded concept for radiotherapy volume types.

    Attributes:
        valueset (str): The canonical URL of the mCODE radiotherapy volume type ValueSet.

    Methods:
        _concept_display_postprocessing(display: str) -> str:
            Removes the suffix " (observable entity)" from the display string for improved readability.
    """
    valueset = "http://hl7.org/fhir/us/mcode/ValueSet/mcode-radiotherapy-volume-type-vs"

    @classmethod
    def _concept_display_postprocessing(cls, display: str) -> str:
        return display.replace(" (observable entity)", "")


class ObservationBodySite(CodedConcept):
    """
    Represents a coded concept for the body site of an observation.

    Attributes:
        valueset (str): URL pointing to the FHIR ValueSet that defines the allowed body site codes for observations.
    """
    valueset = (
        "https://simplifier.net/onconova/ValueSets/onconova-observation-bodysites"
    )


class RadiotherapyTreatmentLocation(CodedConcept):
    """
    Represents a coded concept for radiotherapy treatment location.

    Attributes:
        valueset (str): The URI for the radiotherapy treatment location ValueSet.

    Methods:
        _concept_display_postprocessing(display: str) -> str:
            Removes the suffix " (body structure)" from the display string for improved readability.
    """
    valueset = (
        "http://hl7.org/fhir/us/mcode/ValueSet/mcode-radiotherapy-treatment-location-vs"
    )

    @classmethod
    def _concept_display_postprocessing(cls, display: str) -> str:
        return display.replace(" (body structure)", "")


class RadiotherapyTreatmentLocationQualifier(CodedConcept):
    """
    Represents a coded concept for radiotherapy treatment location qualifier.

    Attributes:
        valueset (str): The URI for the radiotherapy treatment location qualifier ValueSet.

    Methods:
        _concept_display_postprocessing(display: str) -> str:
            Removes the suffix " (qualifier value)" from the display string for improved readability.
    """
    valueset = "http://hl7.org/fhir/us/mcode/ValueSet/mcode-radiotherapy-treatment-location-qualifier-vs"

    @classmethod
    def _concept_display_postprocessing(cls, display: str) -> str:
        return display.replace(" (qualifier value)", "")


class TNMStage(CodedConcept):
    """
    Represents a coded concept for TNM stage group.

    Attributes:
        valueset (str): The URI for the TNM stage group ValueSet.

    Methods:
        _concept_display_postprocessing(display: str) -> str:
            Cleans and formats the display string for AJCC stage representation.
    """
    valueset = "https://build.fhir.org/ig/HL7/fhir-mCODE-ig/ValueSet-mcode-tnm-stage-group-vs.json"

    @classmethod
    def _concept_display_postprocessing(cls, display: str) -> str:
        display = (
            display.replace("(American Joint Committee on Cancer)", "")
            .replace("American Joint Committee on Cancer", "")
            .replace("stage", "")
            .replace("(qualifier value)", "")
            .replace("AJCC", "")
            .replace(" ", "")
        )
        if display[0].isnumeric() and not display.startswith("0"):
            display = (
                {
                    "1": "I",
                    "2": "II",
                    "3": "III",
                    "4": "IV",
                    "5": "V",
                }[display[0]]
                + ":"
                + display[1:]
            )
        if display[-1] == ":":
            display = display[:-1]
        return f"AJCC Stage {display}"


class TNMStagingMethod(CodedConcept):
    """
    Represents a coded concept for TNM staging method.

    Attributes:
        valueset (str): The URI for the TNM staging method ValueSet.
        extension_concepts (list): List of extension concepts for additional codes.

    Methods:
        _concept_display_postprocessing(display: str) -> str:
            Cleans and formats the display string for TNM staging method representation.
    """
    valueset = "https://build.fhir.org/ig/HL7/fhir-mCODE-ig/ValueSet-mcode-tnm-staging-method-vs.json"
    extension_concepts = [
        CodedConceptSchema(
            code="1287211007",
            system="http://snomed.info/sct",
            display="No information available",
            version="http://snomed.info/sct/900000000000207008",
        )
    ]

    @classmethod
    def _concept_display_postprocessing(cls, display: str) -> str:
        return (
            display.replace("American Joint Committee on Cancer", "AJCC")
            .replace("American Joint Commission on Cancer", "AJCC")
            .replace(", ", " ")
            .replace("Cancer Staging Manual", "Staging Manual")
            .replace(" (tumor staging)", "")
            .replace(" version", "edition")
            .replace(" tumor staging system", "")
            .replace(" neoplasm staging system", "")
            .replace("Union for International Cancer Control Stage", "UICC Staging")
        )


class TNMPrimaryTumorCategory(CodedConcept):
    """
    Represents a coded concept for TNM primary tumor category.

    Attributes:
        valueset (str): The URI for the TNM primary tumor category ValueSet.

    Methods:
        _concept_display_postprocessing(display: str) -> str:
            Cleans and formats the display string for TNM primary tumor category.
    """
    valueset = (
        "https://simplifier.net/onconova/ValueSets/onconova-tnm-primary-tumor-category"
    )

    @classmethod
    def _concept_display_postprocessing(cls, display: str) -> str:
        return (
            display.replace("(American Joint Committee on Cancer)", "")
            .replace("American Joint Committee on Cancer", "")
            .replace("stage", "")
            .replace("AJCC", "")
            .replace(" ", "")
        )


class TNMPrimaryTumorStagingType(CodedConcept):
    """
    Represents a coded concept for TNM primary tumor staging type.

    Attributes:
        valueset (str): The URI for the TNM primary tumor staging type ValueSet.
    """
    valueset = "https://build.fhir.org/ig/HL7/fhir-mCODE-ig/ValueSet-mcode-tnm-primary-tumor-staging-type-vs.json"


class TNMDistantMetastasesCategory(CodedConcept):
    """
    Represents a coded concept for TNM distant metastases category.

    Attributes:
        valueset (str): The URI for the TNM distant metastases category ValueSet.

    Methods:
        _concept_display_postprocessing(display: str) -> str:
            Cleans and formats the display string for TNM distant metastases category.
    """
    valueset = "https://simplifier.net/onconova/ValueSets/onconova-tnm-distant-metastases-category"

    @classmethod
    def _concept_display_postprocessing(cls, display: str) -> str:
        return (
            display.replace("(American Joint Committee on Cancer)", "")
            .replace("American Joint Committee on Cancer", "")
            .replace("stage", "")
            .replace("AJCC", "")
            .replace(" ", "")
        )


class TNMDistantMetastasesStagingType(CodedConcept):
    """
    Represents a coded concept for TNM distant metastases staging type.

    Attributes:
        valueset (str): The URI for the TNM distant metastases staging type ValueSet.
    """
    valueset = "https://build.fhir.org/ig/HL7/fhir-mCODE-ig/ValueSet-mcode-tnm-distant-metastases-staging-type-vs.json"


class TNMRegionalNodesCategory(CodedConcept):
    """
    Represents a coded concept for TNM regional nodes category.

    Attributes:
        valueset (str): The URI for the TNM regional nodes category ValueSet.

    Methods:
        _concept_display_postprocessing(display: str) -> str:
            Cleans and formats the display string for TNM regional nodes category.
    """
    valueset = (
        "https://simplifier.net/onconova/ValueSets/onconova-tnm-regional-nodes-category"
    )

    @classmethod
    def _concept_display_postprocessing(cls, display: str) -> str:
        return (
            display.replace("(American Joint Committee on Cancer)", "")
            .replace("American Joint Committee on Cancer", "")
            .replace("stage", "")
            .replace("AJCC", "")
            .replace(" ", "")
        )


class TNMRegionalNodesStagingType(CodedConcept):
    """
    Represents a coded concept for TNM regional nodes staging type.

    Attributes:
        valueset (str): The URI for the TNM regional nodes staging type ValueSet.
    """
    valueset = "https://build.fhir.org/ig/HL7/fhir-mCODE-ig/ValueSet-mcode-tnm-regional-nodes-staging-type-vs.json"


class TNMGradeCategory(CodedConcept):
    """
    Represents a coded concept for TNM grade category.

    Attributes:
        valueset (str): The URI for the TNM grade category ValueSet.

    Methods:
        _concept_display_postprocessing(display: str) -> str:
            Cleans and formats the display string for TNM grade category.
    """
    valueset = "https://simplifier.net/onconova/ValueSets/onconova-tnm-grade-category"

    @classmethod
    def _concept_display_postprocessing(cls, display: str) -> str:
        return (
            display.replace("(American Joint Committee on Cancer)", "")
            .replace("American Joint Committee on Cancer", "")
            .replace("grade", "")
            .replace("AJCC", "")
            .replace(" ", "")
        )


class TNMResidualTumorCategory(CodedConcept):
    """
    Represents a coded concept for TNM residual tumor category.

    Attributes:
        valueset (str): The URI for the TNM residual tumor category ValueSet.

    Methods:
        _concept_display_postprocessing(display: str) -> str:
            Cleans and formats the display string for TNM residual tumor category.
    """
    valueset = (
        "https://simplifier.net/onconova/ValueSets/onconova-tnm-residual-tumor-category"
    )

    @classmethod
    def _concept_display_postprocessing(cls, display: str) -> str:
        return (
            display.replace("(American Joint Committee on Cancer)", "")
            .replace("American Joint Committee on Cancer", "")
            .replace("stage", "")
            .replace("AJCC", "")
            .replace(" ", "")
        )


class TNMLymphaticInvasionCategory(CodedConcept):
    """
    Represents a coded concept for TNM lymphatic invasion category.

    Attributes:
        valueset (str): The URI for the TNM lymphatic invasion category ValueSet.

    Methods:
        _concept_display_postprocessing(display: str) -> str:
            Cleans and formats the display string for TNM lymphatic invasion category.
    """
    valueset = "https://simplifier.net/onconova/ValueSets/onconova-tnm-lymphatic-invasion-category"

    @classmethod
    def _concept_display_postprocessing(cls, display: str) -> str:
        return (
            display.replace("(American Joint Committee on Cancer)", "")
            .replace("American Joint Committee on Cancer", "")
            .replace("stage", "")
            .replace("AJCC", "")
            .replace(" ", "")
        )


class TNMVenousInvasionCategory(CodedConcept):
    """
    Represents a coded concept for TNM venous invasion category.

    Attributes:
        valueset (str): The URI for the TNM venous invasion category ValueSet.

    Methods:
        _concept_display_postprocessing(display: str) -> str:
            Cleans and formats the display string for TNM venous invasion category.
    """
    valueset = "https://simplifier.net/onconova/ValueSets/onconova-tnm-venous-invasion-category"

    @classmethod
    def _concept_display_postprocessing(cls, display: str) -> str:
        return (
            display.replace("(American Joint Committee on Cancer)", "")
            .replace("American Joint Committee on Cancer", "")
            .replace("stage", "")
            .replace("AJCC", "")
            .replace(" ", "")
        )


class TNMPerineuralInvasionCategory(CodedConcept):
    """
    Represents a coded concept for TNM perineural invasion category.

    Attributes:
        valueset (str): The URI for the TNM perineural invasion category ValueSet.

    Methods:
        _concept_display_postprocessing(display: str) -> str:
            Converts display string to Pn0 or Pn1 for perineural invasion status.
    """
    valueset = "https://simplifier.net/onconova/ValueSets/onconova-tnm-perineural-invasion-category"

    @classmethod
    def _concept_display_postprocessing(cls, display: str) -> str:
        return display.replace("No perineural invasion by tumor", "Pn0").replace(
            "Perineural invasion by tumor", "Pn1"
        )


class TNMSerumTumorMarkerLevelCategory(CodedConcept):
    """
    Represents a coded concept for TNM serum tumor marker level category.

    Attributes:
        valueset (str): The URI for the TNM serum tumor marker level category ValueSet.

    Methods:
        _concept_display_postprocessing(display: str) -> str:
            Cleans the display string by removing redundant text.
    """
    valueset = "https://simplifier.net/onconova/ValueSets/onconova-tnm-serum-tumor-marker-level-category"

    @classmethod
    def _concept_display_postprocessing(cls, display: str) -> str:
        return display.replace("Serum tumor marker stage", "").replace(
            "Serum tumour marker stage", ""
        )


class FIGOStage(CodedConcept):
    """
    Represents a FIGO stage coded concept for oncology terminology.

    Attributes:
        valueset (str): The URL of the HL7 FHIR ValueSet defining valid FIGO stage codes.
    """
    valueset = "http://hl7.org/fhir/us/mcode/ValueSet/mcode-figo-stage-value-vs"


class FIGOStagingMethod(CodedConcept):
    """
    Represents the FIGO Staging Method as a coded concept.

    Attributes:
        valueset (str): The canonical URL for the FIGO staging method ValueSet.

    Methods:
        _concept_display_postprocessing(display: str) -> str:
            Post-processes the display string by replacing 'Federation of Gynecology and Obstetrics'
            with 'FIGO' and removing ' (tumor staging)' for concise representation.
    """
    valueset = "http://hl7.org/fhir/us/mcode/ValueSet/mcode-figo-staging-method-vs"

    @classmethod
    def _concept_display_postprocessing(cls, display: str) -> str:
        return display.replace(
            "Federation of Gynecology and Obstetrics", "FIGO"
        ).replace(" (tumor staging)", "")


class BinetStage(CodedConcept):
    """
    Represents the Binet staging system for chronic lymphocytic leukemia (CLL).

    Attributes:
        valueset (str): URL of the FHIR ValueSet for Binet stages.
    """
    valueset = "http://hl7.org/fhir/us/mcode/ValueSet/mcode-binet-stage-value-vs"


class RaiStage(CodedConcept):
    """
    Represents the Rai staging system for chronic lymphocytic leukemia (CLL) as a coded concept.

    Attributes:
        valueset (str): The URL of the HL7 FHIR ValueSet defining valid Rai stage codes.
    """
    valueset = "http://hl7.org/fhir/us/mcode/ValueSet/mcode-rai-stage-value-vs"


class RaiStagingMethod(CodedConcept):
    """
    Represents the Rai Staging Method as a coded concept for cancer staging.

    Attributes:
        valueset (str): The URL of the HL7 FHIR ValueSet for Rai staging method.
    """
    valueset = "http://hl7.org/fhir/us/mcode/ValueSet/mcode-rai-staging-method-vs"


class LymphomaStage(CodedConcept):
    """
    Represents a coded concept for lymphoma staging based on the mCODE value set.

    Attributes:
        valueset (str): The URL of the HL7 FHIR mCODE value set for lymphoma stage values.
    """
    valueset = "http://hl7.org/fhir/us/mcode/ValueSet/mcode-lymphoma-stage-value-vs"


class LymphomaStagingMethod(CodedConcept):
    """
    Represents a coded concept for lymphoma staging methods.

    Attributes:
        valueset (str): The URI of the HL7 FHIR mCODE value set for lymphoma staging methods.
    """
    valueset = "http://hl7.org/fhir/us/mcode/ValueSet/mcode-lymphoma-staging-method-vs"


class LymphomaStageValueModifier(CodedConcept):
    """
    Represents a modifier for lymphoma stage values using coded concepts.

    Attributes:
        valueset (str): The URI of the value set defining valid lymphoma stage value modifiers.
    """
    valueset = (
        "http://hl7.org/fhir/us/mcode/ValueSet/mcode-lymphoma-stage-value-modifier-vs"
    )


class ClinOrPathModifier(CodedConcept):
    """
    Represents a clinical or pathological modifier coded concept for staging information.

    Attributes:
        valueset (str): The URL of the HL7 FHIR value set for clinical or pathological modifiers.

    Methods:
        _concept_display_postprocessing(display: str) -> str:
            Removes the substring "staging (qualifier value)" from the provided display string.
    """
    valueset = "http://hl7.org/fhir/us/mcode/ValueSet/mcode-clin-or-path-modifier-vs"

    @classmethod
    def _concept_display_postprocessing(cls, display: str) -> str:
        return display.replace("staging (qualifier value)", "")


class BreslowDepthStage(CodedConcept):
    """
    Represents the Breslow Depth Stage coded concept for melanoma staging.

    Attributes:
        valueset (str): The canonical URL of the Breslow Depth Stage ValueSet.
    """
    valueset = (
        "http://hl7.org/fhir/us/mcode/ValueSet/mcode-breslow-depth-stage-value-vs"
    )


class ClarkLevel(CodedConcept):
    """
    Represents the Clark Level coded concept for melanoma staging.

    Attributes:
        valueset (str): The URL of the HL7 FHIR ValueSet for Clark Level values,
            used to standardize the representation of Clark Level in clinical data.
    """
    valueset = "http://hl7.org/fhir/us/mcode/ValueSet/mcode-clark-level-value-vs"


class MyelomaISSStage(CodedConcept):
    """
    Represents the International Staging System (ISS) stage for multiple myeloma.

    Attributes:
        valueset (str): The canonical URL of the value set defining valid ISS stage codes.
    """
    valueset = "http://hl7.org/fhir/us/mcode/ValueSet/mcode-myeloma-iss-stage-value-vs"


class MyelomaRISSStage(CodedConcept):
    """
    Represents the Revised International Staging System (RISS) stage for multiple myeloma.

    Attributes:
        valueset (str): The canonical URL of the value set defining valid RISS stage codes.
    """
    valueset = "http://hl7.org/fhir/us/mcode/ValueSet/mcode-myeloma-riss-stage-value-vs"


class NeuroblastomaINSSStage(CodedConcept):
    """
    Represents a coded concept for the International Neuroblastoma Staging System (INSS) stage.

    Attributes:
        valueset (str): The canonical URL for the HL7 FHIR ValueSet defining valid INSS stage codes.

    Methods:
        _concept_display_postprocessing(display: str) -> str:
            Post-processes the display string by replacing 'International neuroblastoma staging system'
            with 'IN' for concise representation.
    """
    valueset = "http://hl7.org/fhir/us/mcode/ValueSet/mcode-neuroblastoma-inss-value-vs"

    @classmethod
    def _concept_display_postprocessing(cls, display: str) -> str:
        return display.replace("International neuroblastoma staging system", "IN")


class NeuroblastomaINRGSSStage(CodedConcept):
    """
    Represents the INRGSS stage for neuroblastoma as a coded concept.

    Attributes:
        valueset (str): The URL of the FHIR ValueSet defining valid INRGSS stage codes for neuroblastoma.
    """
    valueset = (
        "http://hl7.org/fhir/us/mcode/ValueSet/mcode-neuroblastoma-INRGSS-value-vs"
    )


class GleasonGradeGroupStage(CodedConcept):
    """
    Represents the Gleason Grade Group Stage as a coded concept.

    Attributes:
        valueset (str): The URI of the HL7 FHIR mCODE value set for Gleason Grade Group.
    """
    valueset = (
        "http://hl7.org/fhir/us/mcode/ValueSet/mcode-gleason-grade-group-value-vs"
    )


class WilmsTumorStage(CodedConcept):
    """
    Represents the staging information for Wilms Tumor using coded concepts.

    Attributes:
        valueset (str): The URL of the HL7 FHIR ValueSet defining valid Wilms Tumor stages.
    """
    valueset = "http://hl7.org/fhir/us/mcode/ValueSet/mcode-wilms-tumor-stage-value-vs"


class RhabdomyosarcomaClinicalGroup(CodedConcept):
    """
    Represents a coded concept for the clinical group classification of Rhabdomyosarcoma.

    Attributes:
        valueset (str): The canonical URL of the FHIR ValueSet for rhabdomyosarcoma clinical group values.

    Methods:
        _concept_display_postprocessing(display: str) -> str:
            Processes the display string to extract and format the clinical group label as 'Group <group>'.
    """
    valueset = "http://hl7.org/fhir/us/mcode/ValueSet/mcode-rhabdomyosarcoma-clinical-group-value-vs"

    @classmethod
    def _concept_display_postprocessing(cls, display: str) -> str:
        if "clinical group" in display:
            group = display.split("clinical group ")[1].split(":")[0]
        else:
            group = display.split("Group ")[1]
        return f"Group {group}"


class TumorMarkerAnalyte(CodedConcept):
    """
    Represents a tumor marker analyte as a coded concept, with additional properties loaded from analyte data.

    Attributes:
        valueset (str): URL to the FHIR ValueSet defining valid tumor marker analytes.

    Methods:
        _concept_postprocessing(concept: CodedConceptSchema) -> CodedConceptSchema:
            Class method that enriches the given concept with additional properties from analyte data,
            if available, by looking up the concept code in ANALYTES_DATA and serializing the result.
    """
    valueset = (
        "https://simplifier.net/onconova/ValueSets/onconova-tumor-marker-analytes"
    )

    @classmethod
    def _concept_postprocessing(cls, concept: CodedConceptSchema) -> CodedConceptSchema:
        from onconova.oncology.models.tumor_marker import ANALYTES_DATA

        analyte_data = ANALYTES_DATA.get(concept.code)
        concept.properties = (  # type: ignore
            analyte_data.model_dump(mode="json") if analyte_data else None  # type: ignore
        )
        return concept


class Race(CodedConcept):
    """
    Represents a coded concept for race categories based on the HL7 FHIR US Core OMB race value set.

    Attributes:
        valueset (str): The URI of the HL7 FHIR US Core OMB race category value set.

    Methods:
        _concept_display_postprocessing(display: str) -> str:
            Post-processes the display string for a race concept by converting it to title case.
    """
    valueset = "http://hl7.org/fhir/us/core/ValueSet/omb-race-category"

    @classmethod
    def _concept_display_postprocessing(cls, display: str) -> str:
        return display.title()


class BirthSex(CodedConcept):
    """
    Represents the birth sex of a patient as a coded concept.

    Attributes:
        valueset (str): The URI of the HL7 FHIR ValueSet for administrative gender.
    """
    valueset = "http://hl7.org/fhir/ValueSet/administrative-gender"


class SmokingStatus(CodedConcept):
    """
    Represents a coded concept for a patient's smoking status, using a predefined ValueSet.

    Attributes:
        valueset (str): URL to the ValueSet defining possible smoking status codes.

    Methods:
        _concept_display_postprocessing(display: str) -> str:
            Removes the substring " (finding)" from the concept display string.
    """
    valueset = "https://simplifier.net/onconova/ValueSets/onconova-smoking-status"

    @classmethod
    def _concept_display_postprocessing(cls, display: str) -> str:
        return display.replace(" (finding)", "")


class CauseOfDeath(CodedConcept):
    """
    Represents a coded concept for the cause of death.

    Attributes:
        valueset (str): URL referencing the FHIR ValueSet containing valid causes of death.

    Inherits from:
        CodedConcept: Base class for coded terminology concepts.
    """
    valueset = "https://simplifier.net/onconova/ValueSets/onconova-causes-of-death"


class AdverseEventTerm(CodedConcept):
    """
    Represents a coded concept for adverse event terms.
    """
    pass


class StructuralVariantAnalysisMethod(CodedConcept):
    """
    Represents a coded concept for structural variant analysis methods.

    Attributes:
        valueset (str): The URI for the structural variant analysis method ValueSet.
    """
    valueset = "https://loinc.org/LL4048-6/"


class Gene(CodedConcept):
    """
    Represents a coded concept for genes.

    Attributes:
        valueset (str): The URI for the HGNC gene ValueSet.
    """
    valueset = "http://hl7.org/fhir/uv/genomics-reporting/ValueSet/hgnc-vs"


class GeneExon(BaseModel):
    """
    Represents an exon of a gene.

    Attributes:
        gene (ForeignKey): Reference to the associated gene.
        name (AnnotationProperty): Name of the exon.
        rank (IntegerField): Rank of the exon.
        coding_dna_region (IntegerRangeField): Coding DNA region.
        coding_genomic_region (IntegerRangeField): Coding genomic region.
    """
    objects = QueryablePropertiesManager()
    gene = models.ForeignKey(
        to=Gene,
        on_delete=models.CASCADE,
        related_name="exons",
    )
    name = AnnotationProperty(
        verbose_name=_("Exon name"),
        annotation=Concat(
            "gene__display",
            models.Value(" exon "),
            "rank",
            output_field=models.CharField(),
        ),
    )
    rank = models.IntegerField()
    coding_dna_region = IntegerRangeField()
    coding_genomic_region = IntegerRangeField()


class ReferenceGenomeBuild(CodedConcept):
    """
    Represents a coded concept for reference genome builds.

    Attributes:
        valueset (str): The URI for the reference genome build ValueSet.
    """
    valueset = "https://loinc.org/LL1040-6/"


class DnaChangeType(CodedConcept):
    valueset = "http://hl7.org/fhir/uv/genomics-reporting/ValueSet/dna-change-type-vs"

    @classmethod
    def _concept_display_postprocessing(cls, display: str) -> str:
        return display.replace("_", " ").capitalize()



class GeneticVariantSource(CodedConcept):
    """
    Represents a coded concept for genetic variant sources.

    Attributes:
        valueset (str): The URI for the genetic variant source ValueSet.
    """
    valueset = "https://loinc.org/LL378-1/"


class Zygosity(CodedConcept):
    """
    Represents a coded concept for zygosity.

    Attributes:
        valueset (str): The URI for the zygosity ValueSet.
    """
    valueset = "https://loinc.org/LL381-5/"


class VariantInheritance(CodedConcept):
    """
    Represents a coded concept for variant inheritance.

    Attributes:
        valueset (str): The URI for the variant inheritance ValueSet.
    """
    valueset = (
        "http://hl7.org/fhir/uv/genomics-reporting/ValueSet/variant-inheritance-vs"
    )


class ChromosomeIdentifier(CodedConcept):
    """
    Represents a coded concept for chromosome identifiers.

    Attributes:
        valueset (str): The URI for the chromosome identifier ValueSet.
    """
    valueset = "https://loinc.org/LL2938-0/"


class AminoAcidChangeType(CodedConcept):
    """
    Represents a coded concept for amino acid change types.

    Attributes:
        valueset (str): The URI for the amino acid change type ValueSet.
    """
    valueset = "https://loinc.org/LL380-7/"


class MolecularConsequence(CodedConcept):
    """
    Represents a molecular consequence concept, inheriting from CodedConcept.

    Attributes:
        valueset (str): URL of the HL7 FHIR molecular consequence value set.

    Methods:
        _concept_display_postprocessing(display: str) -> str:
            Post-processes the display string by replacing underscores with spaces and capitalizing it.
    """
    valueset = (
        "http://hl7.org/fhir/uv/genomics-reporting/ValueSet/molecular-consequence-vs"
    )

    @classmethod
    def _concept_display_postprocessing(cls, display: str) -> str:
        return display.replace("_", " ").capitalize()



class GenomicCoordinateSystem(CodedConcept):
    """
    Represents a coded concept for genomic coordinate systems.

    Attributes:
        valueset (str): The URI for the genomic coordinate system ValueSet.
    """
    valueset = "https://loinc.org/LL5323-2/"


class MicrosatelliteInstabilityState(CodedConcept):
    """
    Represents a coded concept for microsatellite instability state.

    Attributes:
        valueset (str): The URI for the microsatellite instability state ValueSet.
    """
    valueset = "https://loinc.org/LL3994-2/"


class AdjunctiveTherapyRole(CodedConcept):
    """
    Represents adjunctive therapy roles as coded concepts, including additional extension concepts.

    Attributes:
        valueset (str): URL of the value set for adjunctive therapy roles.
        extension_concepts (list): List of additional coded concepts for extension.

    Methods:
        _concept_display_postprocessing(display: str) -> str:
            Cleans up the display string by removing keywords such as 'therapy', 'care', 'treatment', 'drug', and 'antineoplastic'.
    """
    valueset = (
        "https://simplifier.net/onconova/ValueSets/onconova-adjunctive-therapy-roles"
    )
    # Additional codes
    extension_concepts = [
        CodedConceptSchema(
            code="1287211007",
            system="http://snomed.info/sct",
            display="No information available",
            version="http://snomed.info/sct/900000000000207008",
        )
    ]

    @classmethod
    def _concept_display_postprocessing(cls, display: str) -> str:
        return (
            display.replace("therapy", "")
            .replace("care", "")
            .replace(" Therapy", "")
            .replace("treatment", "")
            .replace("drug", "")
            .replace("antineoplastic", "")
        )


class CancerTreatmentResponseObservationMethod(CodedConcept):
    """
    Represents a coded concept for cancer treatment response observation methods.

    Attributes:
        valueset (str): URL of the ValueSet defining valid observation methods.
        extension_concepts (list): List of additional coded concepts, such as 'No information available'.

    Inherits from:
        CodedConcept
    """
    valueset = "https://simplifier.net/onconova/ValueSets/onconova-cancer-treatment-response-observation-methods"
    extension_concepts = [
        CodedConceptSchema(
            code="1287211007",
            system="http://snomed.info/sct",
            display="No information available",
            version="http://snomed.info/sct/900000000000207008",
        )
    ]



class CancerTreatmentResponse(CodedConcept):
    """
    Represents a coded concept for cancer treatment response.

    Attributes:
        valueset (str): The URI for the cancer treatment response ValueSet.
    """
    valueset = "https://loinc.org/LL4721-8/"


class TumorBoardRecommendation(CodedConcept):
    """
    Represents a coded concept for tumor board recommendations.

    Attributes:
        valueset (str): The URI for the tumor board recommendations ValueSet.
    """
    valueset = (
        "https://simplifier.net/onconova/ValueSets/onconova-tumor-board-recommendations"
    )


class MolecularTumorBoardRecommendation(TumorBoardRecommendation):
    """
    A proxy model for TumorBoardRecommendation that restricts queryset to specific molecular codes.

    This model uses a custom manager to filter recommendations to those with codes
    "LA14020-4", "LA14021-2", or "LA14022-0", representing molecular tumor board recommendations.

    Attributes:
        objects (MolecularTumorBoardRecommendationManager): Custom manager that filters recommendations by code.

    Meta:
        proxy (bool): Indicates that this is a proxy model and does not create a new database table.
    """
    class MolecularTumorBoardRecommendationManager(models.Manager):
        def get_queryset(self):
            return (
                super()
                .get_queryset()
                .filter(code__in=["LA14020-4", "LA14021-2", "LA14022-0"])
            )

    objects = MolecularTumorBoardRecommendationManager()

    class Meta:
        proxy = True



class ICD10Condition(CodedConcept):
    """
    Represents a coded concept for ICD-10 conditions.

    Attributes:
        valueset (str): The URI for the ICD-10 ValueSet.
    """
    valueset = "http://hl7.org/fhir/ValueSet/icd-10"


class ExpectedDrugAction(CodedConcept):
    """
    Represents a coded concept for expected drug actions.

    Attributes:
        valueset (str): The URI for the expected drug action ValueSet.
    """
    valueset = "https://simplifier.net/onconova/ValueSets/onconova-expected-drug-action"


class RecreationalDrug(CodedConcept):
    """
    Represents a coded concept for recreational drugs.

    Attributes:
        valueset (str): The URI for the recreational drugs ValueSet.
    """
    valueset = "https://simplifier.net/onconova/ValueSets/onconova-recreational-drugs"


class ExposureAgent(CodedConcept):
    """
    Represents a coded concept for exposure agents.

    Attributes:
        valueset (str): The URI for the exposure agents ValueSet.
    """
    valueset = "https://simplifier.net/onconova/ValueSets/onconova-exposure-agents"


class AdverseEventMitigationTreatmentAdjustment(CodedConcept):
    valueset = "https://simplifier.net/onconova/ValueSets/onconova-adverse-event-mitigation-treatment-adjustment"


class AdverseEventMitigationDrug(CodedConcept):
    valueset = "https://simplifier.net/onconova/ValueSets/onconova-adverse-event-mitigation-drugs"


class AdverseEventMitigationProcedure(CodedConcept):
    valueset = "https://simplifier.net/onconova/ValueSets/onconova-adverse-event-mitigation-procedures"


class AdverseEventMitigationManagement(CodedConcept):
    valueset = "https://simplifier.net/onconova/ValueSets/onconova-adverse-event-mitigation-management"

    @classmethod
    def _concept_display_postprocessing(cls, display: str) -> str:
        return display.replace("management", "")


class CancerRiskAssessmentMethod(CodedConcept):
    valueset = "https://simplifier.net/onconova/ValueSets/onconova-cancer-risk-assessment-methods"


class CancerRiskAssessmentClassification(CodedConcept):
    valueset = "https://simplifier.net/onconova/ValueSets/onconova-cancer-risk-assessment-values"
