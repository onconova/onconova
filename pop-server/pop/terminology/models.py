from django.db import models
from django.db.models.functions import Concat
from django.contrib.postgres import fields as postgres
from django.contrib.postgres.fields import IntegerRangeField
from django.utils.translation import gettext_lazy as _
from typing import ClassVar, List
from queryable_properties.properties import AnnotationProperty
from queryable_properties.managers import QueryablePropertiesManager

from pop.core.models import BaseModel
from pop.terminology.utils import CodedConcept as CodedConceptSchema


class CodedConcept(BaseModel):
    code = models.CharField(
        verbose_name="Code",
        help_text=_("Code as defined in the code syste,"),
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
    valueset = "http://terminology.hl7.org/ValueSet/v3-FamilyMember"
    
    @classmethod
    def _concept_display_postprocessing(cls, display: str) -> str:
        return display.title()


class AlcoholConsumptionFrequency(CodedConcept):
    valueset = "https://loinc.org/LL2179-1/"
    
    @classmethod
    def _concept_display_postprocessing(cls, display: str) -> str:
        return display.title()


class AdministrativeGender(CodedConcept):
    valueset = "http://hl7.org/fhir/ValueSet/administrative-gender"

class ProcedureOutcome(CodedConcept):
    valueset = "http://hl7.org/fhir/ValueSet/procedure-outcome"

class LateralityQualifier(CodedConcept):
    valueset = "http://hl7.org/fhir/us/mcode/ValueSet/mcode-laterality-qualifier-vs"

    @classmethod
    def _concept_display_postprocessing(cls, display: str) -> str:
        return display.replace(" (qualifier value)", "")


class CancerTopography(CodedConcept):
    codesystem = "http://terminology.hl7.org/CodeSystem/icd-o-3-topography"

class CancerTopographyGroup(CancerTopography):
    class QuerysetManager(models.Manager):
        def get_queryset(self):
            return super().get_queryset().exclude(code__contains=".")

    objects = QuerysetManager()

    class Meta:
        proxy = True


class CancerMorphology(CodedConcept):
    codesystem = "http://terminology.hl7.org/CodeSystem/icd-o-3-morphology"

class CancerMorphologyPrimary(CancerMorphology):
    class QuerysetManager(models.Manager):
        def get_queryset(self):
            return super().get_queryset().filter(code__endswith="/3")

    objects = QuerysetManager()

    class Meta:
        proxy = True


class CancerMorphologyMetastatic(CancerMorphology):
    class QuerysetManager(models.Manager):
        def get_queryset(self):
            return super().get_queryset().filter(code__endswith="/6")

    objects = QuerysetManager()

    class Meta:
        proxy = True


class HistologyDifferentiation(CodedConcept):
    codesystem = "http://terminology.hl7.org/CodeSystem/icd-o-3-differentiation"

class BodyLocationQualifier(CodedConcept):
    valueset = "http://hl7.org/fhir/us/mcode/ValueSet/mcode-body-location-qualifier-vs"

class GenderIdentity(CodedConcept):
    valueset = "https://loinc.org/LL3322-6/"

class ECOGPerformanceStatusInterpretation(CodedConcept):
    valueset = "https://loinc.org/LL529-9/"

class KarnofskyPerformanceStatusInterpretation(CodedConcept):
    valueset = "https://loinc.org/LL4986-7/"

class TreatmentTerminationReason(CodedConcept):
    valueset = (
        "https://simplifier.net/pop/ValueSets/pop-treatment-termination-reason"
    )

    @classmethod
    def _concept_display_postprocessing(cls, display: str) -> str:
        return display.split(' (')[0]


class AntineoplasticAgent(CodedConcept):

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
    """A coded concept describing the route or physiological path of administration of a therapeutic agent into or onto the body of a subject."""
    valueset = "http://hl7.org/fhir/ValueSet/route-codes"


class SurgicalProcedure(CodedConcept):
    valueset = "https://simplifier.net/pop/ValueSets/pop-surgical-procedures"


class RadiotherapyModality(CodedConcept):
    valueset = "http://hl7.org/fhir/us/mcode/ValueSet/mcode-radiotherapy-modality-vs"

    @classmethod
    def _concept_display_postprocessing(cls, display: str) -> str:
        return display.replace(" (procedure)", "")

class RadiotherapyTechnique(CodedConcept):
    valueset = "http://hl7.org/fhir/us/mcode/ValueSet/mcode-radiotherapy-technique-vs"

    @classmethod
    def _concept_display_postprocessing(cls, display: str) -> str:
        return display.replace(" (procedure)", "")

class RadiotherapyVolumeType(CodedConcept):
    valueset = "http://hl7.org/fhir/us/mcode/ValueSet/mcode-radiotherapy-volume-type-vs"

    @classmethod
    def _concept_display_postprocessing(cls, display: str) -> str:
        return display.replace(" (observable entity)", "")


class ObservationBodySite(CodedConcept):
    valueset = "https://simplifier.net/pop/ValueSets/pop-observation-bodysites"


class RadiotherapyTreatmentLocation(CodedConcept):
    valueset = (
        "http://hl7.org/fhir/us/mcode/ValueSet/mcode-radiotherapy-treatment-location-vs"
    )

    @classmethod
    def _concept_display_postprocessing(cls, display: str) -> str:
        return display.replace(" (body structure)", "")


class RadiotherapyTreatmentLocationQualifier(CodedConcept):
    valueset = "http://hl7.org/fhir/us/mcode/ValueSet/mcode-radiotherapy-treatment-location-qualifier-vs"

    @classmethod
    def _concept_display_postprocessing(cls, display: str) -> str:
        return display.replace(" (qualifier value)", "")


class TNMStage(CodedConcept):
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
    valueset = "https://build.fhir.org/ig/HL7/fhir-mCODE-ig/ValueSet-mcode-tnm-staging-method-vs.json"
    # Additional codes for an extensible valuset
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
    valueset = "https://simplifier.net/pop/ValueSets/pop-tnm-primary-tumor-category"

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
    valueset = "https://build.fhir.org/ig/HL7/fhir-mCODE-ig/ValueSet-mcode-tnm-primary-tumor-staging-type-vs.json"

class TNMDistantMetastasesCategory(CodedConcept):
    valueset = (
        "https://simplifier.net/pop/ValueSets/pop-tnm-distant-metastases-category"
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

class TNMDistantMetastasesStagingType(CodedConcept):
    valueset = "https://build.fhir.org/ig/HL7/fhir-mCODE-ig/ValueSet-mcode-tnm-distant-metastases-staging-type-vs.json"

class TNMRegionalNodesCategory(CodedConcept):
    valueset = "https://simplifier.net/pop/ValueSets/pop-tnm-regional-nodes-category"

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
    valueset = "https://build.fhir.org/ig/HL7/fhir-mCODE-ig/ValueSet-mcode-tnm-regional-nodes-staging-type-vs.json"

class TNMGradeCategory(CodedConcept):
    valueset = "https://simplifier.net/pop/ValueSets/pop-tnm-grade-category"

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
    valueset = "https://simplifier.net/pop/ValueSets/pop-tnm-residual-tumor-category"

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
    valueset = (
        "https://simplifier.net/pop/ValueSets/pop-tnm-lymphatic-invasion-category"
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

class TNMVenousInvasionCategory(CodedConcept):
    valueset = "https://simplifier.net/pop/ValueSets/pop-tnm-venous-invasion-category"

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
    valueset = (
        "https://simplifier.net/pop/ValueSets/pop-tnm-perineural-invasion-category"
    )

    @classmethod
    def _concept_display_postprocessing(cls, display: str) -> str:
        return (
            display.replace("No perineural invasion by tumor", "Pn0")
                .replace("Perineural invasion by tumor", "Pn1")
        )

class TNMSerumTumorMarkerLevelCategory(CodedConcept):
    valueset = (
        "https://simplifier.net/pop/ValueSets/pop-tnm-serum-tumor-marker-level-category"
    )

    @classmethod
    def _concept_display_postprocessing(cls, display: str) -> str:
        return (
            display.replace("Serum tumor marker stage", "")
                .replace("Serum tumour marker stage", "")
        )

class FIGOStage(CodedConcept):
    valueset = "http://hl7.org/fhir/us/mcode/ValueSet/mcode-figo-stage-value-vs"

class FIGOStagingMethod(CodedConcept):
    valueset = "http://hl7.org/fhir/us/mcode/ValueSet/mcode-figo-staging-method-vs"

    @classmethod
    def _concept_display_postprocessing(cls, display: str) -> str:
        return ( 
            display.replace("Federation of Gynecology and Obstetrics", "FIGO")
                .replace(" (tumor staging)", "")
        )


class BinetStage(CodedConcept):
    valueset = "http://hl7.org/fhir/us/mcode/ValueSet/mcode-binet-stage-value-vs"

class RaiStage(CodedConcept):
    valueset = "http://hl7.org/fhir/us/mcode/ValueSet/mcode-rai-stage-value-vs"

class RaiStagingMethod(CodedConcept):
    valueset = "http://hl7.org/fhir/us/mcode/ValueSet/mcode-rai-staging-method-vs"

class LymphomaStage(CodedConcept):
    valueset = "http://hl7.org/fhir/us/mcode/ValueSet/mcode-lymphoma-stage-value-vs"

class LymphomaStagingMethod(CodedConcept):
    valueset = "http://hl7.org/fhir/us/mcode/ValueSet/mcode-lymphoma-staging-method-vs"

class LymphomaStageValueModifier(CodedConcept):
    valueset = (
        "http://hl7.org/fhir/us/mcode/ValueSet/mcode-lymphoma-stage-value-modifier-vs"
    )

class ClinOrPathModifier(CodedConcept):
    valueset = "http://hl7.org/fhir/us/mcode/ValueSet/mcode-clin-or-path-modifier-vs"

    @classmethod
    def _concept_display_postprocessing(cls, display: str) -> str:
        return display.replace("staging (qualifier value)", "")


class BreslowDepthStage(CodedConcept):
    valueset = (
        "http://hl7.org/fhir/us/mcode/ValueSet/mcode-breslow-depth-stage-value-vs"
    )

class ClarkLevel(CodedConcept):
    valueset = "http://hl7.org/fhir/us/mcode/ValueSet/mcode-clark-level-value-vs"

class MyelomaISSStage(CodedConcept):
    valueset = "http://hl7.org/fhir/us/mcode/ValueSet/mcode-myeloma-iss-stage-value-vs"

class MyelomaRISSStage(CodedConcept):
    valueset = "http://hl7.org/fhir/us/mcode/ValueSet/mcode-myeloma-riss-stage-value-vs"

class NeuroblastomaINSSStage(CodedConcept):
    valueset = "http://hl7.org/fhir/us/mcode/ValueSet/mcode-neuroblastoma-inss-value-vs"
    
    @classmethod
    def _concept_display_postprocessing(cls, display: str) -> str:
        return display.replace("International neuroblastoma staging system", "IN")


class NeuroblastomaINRGSSStage(CodedConcept):
    valueset = "http://hl7.org/fhir/us/mcode/ValueSet/mcode-neuroblastoma-INRGSS-value-vs"

class GleasonGradeGroupStage(CodedConcept):
    valueset = "http://hl7.org/fhir/us/mcode/ValueSet/mcode-gleason-grade-group-value-vs"

class WilmsTumorStage(CodedConcept):
    valueset = "http://hl7.org/fhir/us/mcode/ValueSet/mcode-wilms-tumor-stage-value-vs"

class RhabdomyosarcomaClinicalGroup(CodedConcept):
    valueset = "http://hl7.org/fhir/us/mcode/ValueSet/mcode-rhabdomyosarcoma-clinical-group-value-vs"

    @classmethod
    def _concept_display_postprocessing(cls, display: str) -> str:
        if "clinical group" in display:
            group = display.split("clinical group ")[1].split(":")[0]
        else:
            group = display.split("Group ")[1]
        return f"Group {group}"
        
class TumorMarkerAnalyte(CodedConcept):
    valueset = "https://simplifier.net/pop/ValueSets/pop-tumor-marker-analytes"

    @classmethod
    def _concept_postprocessing(cls, concept: CodedConceptSchema) -> CodedConceptSchema:
        from pop.oncology.models.tumor_marker import ANALYTES_DATA

        analyte_data = ANALYTES_DATA.get(concept.code)
        concept.properties = (  # type: ignore
            analyte_data.model_dump(mode="json") if analyte_data else None # type: ignore
        )
        return concept

class Race(CodedConcept):
    valueset = "http://hl7.org/fhir/us/core/ValueSet/omb-race-category"
    
    @classmethod
    def _concept_display_postprocessing(cls, display: str) -> str:
        return display.title()

class BirthSex(CodedConcept):
    valueset = "http://hl7.org/fhir/ValueSet/administrative-gender"

class SmokingStatus(CodedConcept):
    valueset = "https://simplifier.net/pop/ValueSets/pop-smoking-status"
    
    @classmethod
    def _concept_display_postprocessing(cls, display: str) -> str:
        return display.replace(" (finding)", "")

class CauseOfDeath(CodedConcept):
    valueset = "https://simplifier.net/pop/ValueSets/pop-causes-of-death"

class AdverseEventTerm(CodedConcept):
    pass

class StructuralVariantAnalysisMethod(CodedConcept):
    valueset = "https://loinc.org/LL4048-6/"
    
class Gene(CodedConcept):
    valueset = "http://hl7.org/fhir/uv/genomics-reporting/ValueSet/hgnc-vs"

class GeneExon(BaseModel):
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
    valueset = "https://loinc.org/LL1040-6/"


class DnaChangeType(CodedConcept):
    valueset = "http://hl7.org/fhir/uv/genomics-reporting/ValueSet/dna-change-type-vs"

    @classmethod
    def _concept_display_postprocessing(cls, display: str) -> str:
        return display.replace("_", " ").capitalize()

class GeneticVariantSource(CodedConcept):
    valueset = "https://loinc.org/LL378-1/"

class Zygosity(CodedConcept):
    valueset = "https://loinc.org/LL381-5/"

class VariantInheritance(CodedConcept):
    valueset = (
        "http://hl7.org/fhir/uv/genomics-reporting/ValueSet/variant-inheritance-vs"
    )

class ChromosomeIdentifier(CodedConcept):
    valueset = "https://loinc.org/LL2938-0/"

class AminoAcidChangeType(CodedConcept):
    valueset = "https://loinc.org/LL380-7/"

class MolecularConsequence(CodedConcept):
    valueset = (
        "http://hl7.org/fhir/uv/genomics-reporting/ValueSet/molecular-consequence-vs"
    )
    
    @classmethod
    def _concept_display_postprocessing(cls, display: str) -> str:
        return display.replace("_", " ").capitalize()

class GenomicCoordinateSystem(CodedConcept):
    valueset = "https://loinc.org/LL5323-2/"

class MicrosatelliteInstabilityState(CodedConcept):
    valueset = "https://loinc.org/LL3994-2/"

class AdjunctiveTherapyRole(CodedConcept):
    valueset = "https://simplifier.net/pop/ValueSets/pop-adjunctive-therapy-roles"
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
    valueset = "https://simplifier.net/pop/ValueSets/pop-cancer-treatment-response-observation-methods"
    extension_concepts = [
        CodedConceptSchema(
            code="1287211007",
            system="http://snomed.info/sct",
            display="No information available",
            version="http://snomed.info/sct/900000000000207008",
        )
    ]

class CancerTreatmentResponse(CodedConcept):
    valueset = "https://loinc.org/LL4721-8/"

class TumorBoardRecommendation(CodedConcept):
    valueset = "https://simplifier.net/pop/ValueSets/pop-tumor-board-recommendations"

class MolecularTumorBoardRecommendation(TumorBoardRecommendation):
    class MolecularTumorBoardRecommendationManager(models.Manager):
        def get_queryset(self):
            return (
                super()
                .get_queryset()
                .filter(
                    code__in=["LA14020-4", "LA14021-2", "LA14022-0"]
                )
            )

    objects = MolecularTumorBoardRecommendationManager()

    class Meta:
        proxy = True


class ICD10Condition(CodedConcept):
    valueset = "http://hl7.org/fhir/ValueSet/icd-10"

class ExpectedDrugAction(CodedConcept):
    valueset = "https://simplifier.net/pop/ValueSets/pop-expected-drug-action"

class RecreationalDrug(CodedConcept):
    valueset = "https://simplifier.net/pop/ValueSets/pop-recreational-drugs"

class ExposureAgent(CodedConcept):
    valueset = "https://simplifier.net/pop/ValueSets/pop-exposure-agents"

class AdverseEventMitigationTreatmentAdjustment(CodedConcept):
    valueset = "https://simplifier.net/pop/ValueSets/pop-adverse-event-mitigation-treatment-adjustment"

class AdverseEventMitigationDrug(CodedConcept):
    valueset = "https://simplifier.net/pop/ValueSets/pop-adverse-event-mitigation-drugs"

class AdverseEventMitigationProcedure(CodedConcept):
    valueset = (
        "https://simplifier.net/pop/ValueSets/pop-adverse-event-mitigation-procedures"
    )

class AdverseEventMitigationManagement(CodedConcept):
    valueset = (
        "https://simplifier.net/pop/ValueSets/pop-adverse-event-mitigation-management"
    )
    
    @classmethod
    def _concept_display_postprocessing(cls, display: str) -> str:
        return display.replace("management", "")


class CancerRiskAssessmentMethod(CodedConcept):
    valueset = "https://simplifier.net/pop/ValueSets/pop-cancer-risk-assessment-methods"

class CancerRiskAssessmentClassification(CodedConcept):
    valueset = "https://simplifier.net/pop/ValueSets/pop-cancer-risk-assessment-values"
