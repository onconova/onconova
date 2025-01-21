from django.db import models
from django.contrib.postgres import fields as postgres
from django.utils.translation import gettext_lazy as _    

from pop.core.models import BaseModel
from pop.terminology.utils import CodedConcept as CodedConceptSchema

class CodedConcept(BaseModel):
    code = models.CharField(
        verbose_name='Code',
        help_text=_('Code as defined in the code syste,'),
        max_length=200,
    )
    display = models.CharField(
        verbose_name='Text',
        help_text=_('Human-readable representation defined by the system'),
        max_length=2000,
        blank=True, null=True,
    )
    system = models.CharField(
        verbose_name='Codesystem',
        help_text=_('Canonical URL of the code system'),
        blank=True, null=True,
    )
    version = models.CharField(
        verbose_name='Version',
        help_text=_('Version of the code system'),
        max_length=200,
        blank=True, null=True,
    )
    synonyms = postgres.ArrayField(
        base_field=models.CharField(
            max_length=2000,
        ),
        default=list
    )
    parent = models.ForeignKey(
        to='self',
        on_delete=models.CASCADE,
        related_name='children',
        null=True, blank=True,
    )
    definition = models.TextField(
        blank=True, null=True,        
    )
    properties = models.JSONField(
        null=True, blank=True
    )
 
    extension_concepts = []

    class Meta:
        unique_together=['code', 'system']
        abstract = True 
    
    def __str__(self):
        return f"{self.display}"
    

class FamilyMemberType(CodedConcept):
    valueset = 'http://terminology.hl7.org/ValueSet/v3-FamilyMember'
    description = 'A relationship between two people characterizing their "familial" relationship'
    def __str__(self):
        return f"{self.display.title()}"


class AlcoholConsumptionFrequency(CodedConcept):
    valueset = 'https://loinc.org/LL2179-1/'
    description = 'Codes representing how often alcohol is consumed'
    def __str__(self):
        return f"{self.display.title()}"


class AdministrativeGender(CodedConcept):
    valueset = 'http://hl7.org/fhir/ValueSet/administrative-gender'
    description = 'A relationship between two people characterizing their "familial" relationship'


class ProcedureOutcome(CodedConcept):
    valueset = 'http://hl7.org/fhir/ValueSet/procedure-outcome'
    description = 'Procedure Outcome code: A selection of relevant SNOMED CT codes.'


class LateralityQualifier(CodedConcept):
    valueset = 'http://hl7.org/fhir/us/mcode/ValueSet/mcode-laterality-qualifier-vs'
    description = 'Qualifiers to specify laterality.'
    def __str__(self):
        return self.display.replace(' (qualifier value)','')


class CancerTopography(CodedConcept):
    codesystem = 'http://terminology.hl7.org/CodeSystem/icd-o-3-topography'
    description = 'Codes describing the location(s) of primary or secondary cancer.'


class CancerMorphology(CodedConcept):
    codesystem = 'http://terminology.hl7.org/CodeSystem/icd-o-3-morphology'
    description = 'Codes representing the structure, arrangement, and behavioral characteristics of malignant neoplasms, and cancer cells. Inclusion criteria: in situ neoplasms and malignant neoplasms.'

class HistologyDifferentiation(CodedConcept):
    codesystem = 'http://terminology.hl7.org/CodeSystem/icd-o-3-differentiation'
    description = 'Codes representing the differentitation characteristics of neoplasms, and cancer cells.'

class BodyLocationQualifier(CodedConcept):
    valueset = 'http://hl7.org/fhir/us/mcode/ValueSet/mcode-body-location-qualifier-vs'
    description = 'Qualifiers to refine a body structure or location including qualifiers for relative location, directionality, number, and plane, and excluding qualifiers for laterality.'

class GenderIdentity(CodedConcept):
    valueset =  'https://loinc.org/LL3322-6/'
    description = 'Gender identity answers as specified by the Office of the National Coordinator for Health IT (ONC).'

class ECOGPerformanceStatusInterpretation(CodedConcept):
    valueset =  'https://loinc.org/LL529-9/'
    description = 'ECOG performance status interpretation.'

class KarnofskyPerformanceStatusInterpretation(CodedConcept):
    valueset =  'https://loinc.org/LL4986-7/'
    description = 'Karnofsky performance status interpretation.'

class ProcedureIntent(CodedConcept):
    valueset =  'http://hl7.org/fhir/us/mcode/ValueSet/mcode-procedure-intent-vs'
    description = 'The purpose of a procedure.'
    
    def __str__(self):
        return f"{self.display.split(' ')[0]}"


class TreatmentTerminationReason(CodedConcept):
    valueset =  'http://hl7.org/fhir/us/mcode/ValueSet/mcode-treatment-termination-reason-vs'
    description = 'Values used to describe the reasons for stopping a treatment or episode of care.'
    extension_concepts = [
        CodedConceptSchema(code='182992009', system='http://snomed.info/sct',display='Treatment completed', version='http://snomed.info/sct/900000000000207008'),
    ] 
    
    def __str__(self):
        return f"{self.display.split(' (')[0]}"
    

class AntineoplasticAgent(CodedConcept):
    valueset =  None
    description = 'NCIT Antineoplastic agents'

    drugCategory = models.CharField(
        verbose_name=_('Drug class'),
        help_text=_('NCT-POT drug classification'),
        max_length=50, null=True, blank=True,
    )
    drugDomain = models.CharField(
        verbose_name=_('Drug domain'),
        help_text=_('NCT-POT drug classification'),
        max_length=50, null=True, blank=True,
    )
    therapyCategory = models.CharField(
        verbose_name=_('Drug class'),
        help_text=_('NCT-POT drug classification'),
        max_length=50, null=True, blank=True,
    )
    atc = models.CharField(
        verbose_name=_('ATC code'),
        max_length=50, null=True, blank=True,
    )
    snomed = models.CharField(
        verbose_name=_('SNOMED CT code'),
        max_length=50, null=True, blank=True,
    )
    rxnorm = models.CharField(
        verbose_name=_('RxNorm code'),
        max_length=50, null=True, blank=True,
    )
    drugbank = models.CharField(
        verbose_name=_('Drugbank code'),
        max_length=50, null=True, blank=True,
    )
    extension_concepts = [
        CodedConceptSchema(code='C128784', display='Bempegaldesleukin', system='http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl')
    ]
    def __str__(self):
        return self.display.capitalize()

class AdditionalDosageInstruction(CodedConcept):
    valueset =  'http://hl7.org/fhir/ValueSet/additional-instruction-codes'
    description = 'Supplemental instruction or warnings to the patient for medication'


class DosageRoute(CodedConcept):
    valueset =  'http://hl7.org/fhir/ValueSet/route-codes'
    description = 'A coded concept describing the route or physiological path of administration of a therapeutic agent into or onto the body of a subject.'


class AdministrationMethod(CodedConcept):
    valueset =  'http://hl7.org/fhir/ValueSet/administration-method-codes'
    description = 'A coded concept describing the technique by which the medicine is administered.'


class SurgicalProcedure(CodedConcept):
    valueset =  'https://simplifier.net/pop/ValueSets/pop-surgical-procedures'
    description = 'Surgical Procedure'


class RadiotherapyModality(CodedConcept):
    valueset =  'http://hl7.org/fhir/us/mcode/ValueSet/mcode-radiotherapy-modality-vs'
    description = 'Codes describing the modalities of external beam and brachytherapy radiation procedures, for use with radiotherapy summaries.'
    def __str__(self):
        return self.display.replace(' (procedure)','')

class RadiotherapyTechnique(CodedConcept):
    valueset =  'http://hl7.org/fhir/us/mcode/ValueSet/mcode-radiotherapy-technique-vs'
    description = 'Codes describing the techniques of external beam and brachytherapy radiation procedures, for use with radiotherapy summaries.'
    def __str__(self):
        return self.display.replace(' (procedure)','')

class RadiotherapyVolumeType(CodedConcept):
    valueset =  'http://hl7.org/fhir/us/mcode/ValueSet/mcode-radiotherapy-volume-type-vs'
    description = 'Codes describing the types of body volumes used in radiotherapy planning and treatment.'
    
    def __str__(self):
        return f"{self.display.replace(' (observable entity)','')}"

class ObservationBodySite(CodedConcept):
    valueset =  'https://simplifier.net/pop/ValueSets/pop-observation-bodysites'
    description = 'Bodysites related to an observation.'


class RadiotherapyTreatmentLocation(CodedConcept):
    valueset =  'http://hl7.org/fhir/us/mcode/ValueSet/mcode-radiotherapy-treatment-location-vs'
    description = 'Codes describing the body locations where radiotherapy treatments can be directed.'
    
    def __str__(self):
        return f"{self.display.replace(' (body structure)','')}"

class RadiotherapyTreatmentLocationQualifier(CodedConcept):
    valueset =  'http://hl7.org/fhir/us/mcode/ValueSet/mcode-radiotherapy-treatment-location-qualifier-vs'
    description = 'Various modifiers that can be applied to body locations where radiotherapy treatments can be directed.'
    
    def __str__(self):
        return f"{self.display.replace(' (qualifier value)','')}"
    
class TNMStageGroupStagingType(CodedConcept):
    valueset =  'https://build.fhir.org/ig/HL7/fhir-mCODE-ig/ValueSet-mcode-tnm-stage-group-staging-type-vs.json'
    description = 'Identifying codes for the type of cancer staging performed, i.e., clinical, pathological, or other, for the stage group observation.'


class CancerStagingType(CodedConcept):
    valueset = 'http://hl7.org/fhir/us/mcode/ValueSet/mcode-cancer-stage-type-vs'
    description = 'Identifying codes for the type of cancer staging performed. In terms of the SNOMED CT hierarchy, these codes represent observables.'


class CancerStagingMethod(CodedConcept):
    valueset =  'http://hl7.org/fhir/us/mcode/ValueSet/mcode-cancer-staging-method-vs'
    description = 'System or method used for staging cancers. The terms in this value set describe staging systems, not specific stages or descriptors used within those systems.'
    
    def __str__(self):
        label = self.display
        label = label.replace('American Joint Commission on Cancer','AJCC')
        return f'{label}'
    


class TNMStage(CodedConcept):
    valueset =  'https://build.fhir.org/ig/HL7/fhir-mCODE-ig/ValueSet-mcode-tnm-stage-group-vs.json'
    description = 'Result values for cancer stage group using TNM staging. This value set contains SNOMED-CT equivalents of AJCC codes for Stage Group, according to TNM staging rules.'
    
    @classmethod
    def transform(cls, concept):
        label = concept.display
        label = label.replace('(American Joint Committee on Cancer)','')
        label = label.replace('American Joint Committee on Cancer','')
        label = label.replace('stage','')
        label = label.replace('(qualifier value)','')
        label = label.replace('AJCC','')
        label = label.replace(' ','')
        if label[0].isnumeric() and not label.startswith('0'):
            label = {'1':'I','2':'II','3':'III','4':'IV','5':'V',}[label[0]] + ':' + label[1:]
        if label[-1]==":":
            label=label[:-1]    
        concept.display = f'AJCC Stage {label}'
        return concept
    


class TNMStagingMethod(CodedConcept):
    valueset =  'https://build.fhir.org/ig/HL7/fhir-mCODE-ig/ValueSet-mcode-tnm-staging-method-vs.json'
    description = 'Method used for TNM staging, e.g., AJCC 6th, 7th, or 8th edition.'
    # Additional codes for an extensible valuset
    extension_concepts = [
        CodedConceptSchema(code='1287211007',system='http://snomed.info/sct', display='No information available', version='http://snomed.info/sct/900000000000207008')
    ]
    @classmethod
    def transform(cls, concept):
        label = concept.display
        label = label.replace('American Joint Committee on Cancer,','AJCC').replace(' (tumor staging)','').replace(' neoplasm staging system','')
        label = label.replace('Union for International Cancer Control Stage','UICC Staging')
        concept.display = label
        return concept
    


class TNMPrimaryTumorCategory(CodedConcept):
    valueset =  'https://simplifier.net/pop/ValueSets/pop-tnm-primary-tumor-category'
    description = 'Result values for T category. This value set contains SNOMED-CT equivalents of AJCC codes for the T category, according to TNM staging rules.'
    
    @classmethod
    def transform(cls, concept):
        label = concept.display
        label = label.replace('(American Joint Committee on Cancer)','')
        label = label.replace('American Joint Committee on Cancer','')
        label = label.replace('stage','')
        label = label.replace('AJCC','')
        label = label.replace(' ','')
        concept.display = label
        return concept
    


class TNMPrimaryTumorStagingType(CodedConcept):
    valueset =  'https://build.fhir.org/ig/HL7/fhir-mCODE-ig/ValueSet-mcode-tnm-primary-tumor-staging-type-vs.json'
    description = 'Identifying codes for the type of cancer staging performed, i.e., clinical, pathological, or other, for primary tumor (T) staging observation.'


class TNMDistantMetastasesCategory(CodedConcept):
    valueset =  'https://simplifier.net/pop/ValueSets/pop-tnm-distant-metastases-category'
    description = 'Result values for M category. This value set contains SNOMED-CT equivalents of AJCC codes for the M category, according to TNM staging rules.'
    
    @classmethod
    def transform(cls, concept):
        label = concept.display
        label = label.replace('(American Joint Committee on Cancer)','')
        label = label.replace('American Joint Committee on Cancer','')
        label = label.replace('stage','')
        label = label.replace('AJCC','')
        label = label.replace(' ','')
        concept.display = label
        return concept
    


class TNMDistantMetastasesStagingType(CodedConcept):
    valueset =  'https://build.fhir.org/ig/HL7/fhir-mCODE-ig/ValueSet-mcode-tnm-distant-metastases-staging-type-vs.json'
    description = 'Identifying codes for the type of cancer staging performed, i.e., clinical, pathological, or other, for distant metastases (M) staging observation.'


class TNMRegionalNodesCategory(CodedConcept):
    valueset =  'https://simplifier.net/pop/ValueSets/pop-tnm-regional-nodes-category'
    description = 'Result values for N category. This value set contains SNOMED-CT equivalents of AJCC codes for the N category, according to TNM staging rules.'
    
    @classmethod
    def transform(cls, concept):
        label = concept.display
        label = label.replace('(American Joint Committee on Cancer)','')
        label = label.replace('American Joint Committee on Cancer','')
        label = label.replace('stage','')
        label = label.replace('AJCC','')
        label = label.replace(' ','')
        concept.display = label
        return concept
    

class TNMRegionalNodesStagingType(CodedConcept):
    valueset =  'https://build.fhir.org/ig/HL7/fhir-mCODE-ig/ValueSet-mcode-tnm-regional-nodes-staging-type-vs.json'
    description = 'Identifying codes for the type of cancer staging performed, i.e., clinical, pathological, or other, for regional nodes (N) staging observation.'


class TNMGradeCategory(CodedConcept):
    valueset =  'https://simplifier.net/pop/ValueSets/pop-tnm-grade-category'
    description = 'Result values for N category. This value set contains SNOMED-CT equivalents of AJCC codes for the G category, according to TNM staging rules.'
    
    @classmethod
    def transform(cls, concept):
        label = concept.display
        label = label.replace('(American Joint Committee on Cancer)','')
        label = label.replace('American Joint Committee on Cancer','')
        label = label.replace('stage','')
        label = label.replace('AJCC','')
        label = label.replace(' ','')
        concept.display = label
        return concept
    
class TNMResidualTumorCategory(CodedConcept):
    valueset =  'https://simplifier.net/pop/ValueSets/pop-tnm-residual-tumor-category'
    description = 'Result values for N category. This value set contains SNOMED-CT equivalents of AJCC codes for the R category, according to TNM staging rules.'
    
    @classmethod
    def transform(cls, concept):
        label = concept.display
        label = label.replace('(American Joint Committee on Cancer)','')
        label = label.replace('American Joint Committee on Cancer','')
        label = label.replace('stage','')
        label = label.replace('AJCC','')
        label = label.replace(' ','')
        concept.display = label
        return concept

class TNMLymphaticInvasionCategory(CodedConcept):
    valueset =  'https://simplifier.net/pop/ValueSets/pop-tnm-lymphatic-invasion-category'
    description = 'Result values for N category. This value set contains SNOMED-CT equivalents of AJCC codes for the L category, according to TNM staging rules.'
    
    @classmethod
    def transform(cls, concept):
        label = concept.display
        label = label.replace('(American Joint Committee on Cancer)','')
        label = label.replace('American Joint Committee on Cancer','')
        label = label.replace('stage','')
        label = label.replace('AJCC','')
        label = label.replace(' ','')
        concept.display = label
        return concept

class TNMVenousInvasionCategory(CodedConcept):
    valueset =  'https://simplifier.net/pop/ValueSets/pop-tnm-venous-invasion-category'
    description = 'Result values for N category. This value set contains SNOMED-CT equivalents of AJCC codes for the V category, according to TNM staging rules.'
    
    @classmethod
    def transform(cls, concept):
        label = concept.display
        label = label.replace('(American Joint Committee on Cancer)','')
        label = label.replace('American Joint Committee on Cancer','')
        label = label.replace('stage','')
        label = label.replace('AJCC','')
        label = label.replace(' ','')
        concept.display = label
        return concept

class TNMPerineuralInvasionCategory(CodedConcept):
    valueset =  'https://simplifier.net/pop/ValueSets/pop-tnm-perineural-invasion-category'
    description = 'Result values for N category. This value set contains SNOMED-CT equivalents of AJCC codes for the Pn category, according to TNM staging rules.'
    
    @classmethod
    def transform(cls, concept):
        label = concept.display
        label = label.replace('(American Joint Committee on Cancer)','')
        label = label.replace('American Joint Committee on Cancer','')
        label = label.replace('stage','')
        label = label.replace('AJCC','')
        label = label.replace(' ','')
        concept.display = label
        return concept

class TNMSerumTumorMarkerLevelCategory(CodedConcept):
    valueset =  'https://simplifier.net/pop/ValueSets/pop-tnm-serum-tumor-marker-level-category'
    description = 'Result values for N category. This value set contains SNOMED-CT equivalents of AJCC codes for the S category, according to TNM staging rules.'
    
    @classmethod
    def transform(cls, concept):
        label = concept.display
        label = label.replace('(American Joint Committee on Cancer)','')
        label = label.replace('American Joint Committee on Cancer','')
        label = label.replace('stage','')
        label = label.replace('AJCC','')
        label = label.replace(' ','')
        concept.display = label
        return concept



class FIGOStage(CodedConcept):
    valueset =  'http://hl7.org/fhir/us/mcode/ValueSet/mcode-figo-stage-value-vs'
    description = 'Values for International Federation of Gynecology and Obstetrics (FIGO) Staging System.'


class FIGOStagingMethod(CodedConcept):
    valueset =  'http://hl7.org/fhir/us/mcode/ValueSet/mcode-figo-staging-method-vs'
    description = 'Staging methods from International Federation of Gynecology and Obstetrics (FIGO).'

    @classmethod
    def transform(cls, concept):
        label = concept.display 
        label = label.replace("Federation of Gynecology and Obstetrics",'FIGO').replace(' (tumor staging)','')
        concept.display = label
        return concept

class BinetStage(CodedConcept):
    valueset =  'http://hl7.org/fhir/us/mcode/ValueSet/mcode-binet-stage-value-vs'
    description = 'Codes in the Binet staging system representing Chronic Lymphocytic Leukemia (CLL) stage.'


class RaiStage(CodedConcept):
    valueset =  'http://hl7.org/fhir/us/mcode/ValueSet/mcode-rai-stage-value-vs'
    description = 'Codes in the Rai staging system representing Chronic Lymphocytic Leukemia (CLL) stage.'


class RaiStagingMethod(CodedConcept):
    valueset =  'http://hl7.org/fhir/us/mcode/ValueSet/mcode-rai-staging-method-vs'
    description = 'Rai Staging Systems used to stage chronic lymphocytic leukemia (CLL).'


class LymphomaStage(CodedConcept):
    valueset =  'http://hl7.org/fhir/us/mcode/ValueSet/mcode-lymphoma-stage-value-vs'
    description = 'Stage values used in lymphoma staging systems.'


class LymphomaStagingMethod(CodedConcept):
    valueset =  'http://hl7.org/fhir/us/mcode/ValueSet/mcode-lymphoma-staging-method-vs'
    description = 'Staging Systems used to stage lymphomas (Hodgkin’s and non-Hodgkin’s).'


class LymphomaStageValueModifier(CodedConcept):
    valueset =  'http://hl7.org/fhir/us/mcode/ValueSet/mcode-lymphoma-stage-value-modifier-vs'
    description = 'Staging modifiers indicating symptoms and extent for lymphomas.'


class ClinOrPathModifier(CodedConcept):
    valueset =  'http://hl7.org/fhir/us/mcode/ValueSet/mcode-clin-or-path-modifier-vs'
    description = 'Stage value modifier indicating if staging was based on clinical or pathologic evidence.'
    def __str__(self):
        label = self.display 
        label = label.replace("staging (qualifier value)",'')
        return label


class BreslowDepthStage(CodedConcept):
    valueset =  'http://hl7.org/fhir/us/mcode/ValueSet/mcode-breslow-depth-stage-value-vs'
    description = 'Codes in the Breslow staging system representing melanoma depth.'


class ClarkLevel(CodedConcept):
    valueset =  'http://hl7.org/fhir/us/mcode/ValueSet/mcode-clark-level-value-vs'
    description = 'Levels for Clark staging of melanoma'


class MyelomaISSStage(CodedConcept):
    valueset =  'http://hl7.org/fhir/us/mcode/ValueSet/mcode-myeloma-iss-stage-value-vs'
    description = 'Codes in ISS staging system representing plasma cell or multiple myeloma stage.'


class MyelomaRISSStage(CodedConcept):
    valueset =  'http://hl7.org/fhir/us/mcode/ValueSet/mcode-myeloma-riss-stage-value-vs'
    description = 'Codes in RISS staging system representing plasma cell or multiple myeloma stage.'


class NeuroblastomaINSSStage(CodedConcept):
    valueset =  'http://hl7.org/fhir/us/mcode/ValueSet/mcode-neuroblastoma-inss-value-vs'
    description = 'Codes in INSS staging system representing neuroblastoma stage.'


class NeuroblastomaINRGSSStage(CodedConcept):
    valueset =  'http://hl7.org/fhir/us/mcode/ValueSet/mcode-neuroblastoma-INRGSS-value-vs'
    description = 'Codes in the INRGSS system representing neuroblastoma stage.'


class GleasonGradeGroupStage(CodedConcept):
    valueset =  'http://hl7.org/fhir/us/mcode/ValueSet/mcode-gleason-grade-group-value-vs'
    description = 'Gleason grade for prostatic cancer, with values that explicitly reference the Gleason score.'


class WilmsTumorStage(CodedConcept):
    valueset =  'http://hl7.org/fhir/us/mcode/ValueSet/mcode-wilms-tumor-stage-value-vs'
    description = 'Codes in the National Wilms Tumor Study Group representing Wilms Tumor stage.'


class RhabdomyosarcomaClinicalGroup(CodedConcept):
    valueset =  'http://hl7.org/fhir/us/mcode/ValueSet/mcode-rhabdomyosarcoma-clinical-group-value-vs'
    description = 'Intergroup code indicating whether the rhabdomyosarcoma is confined to its primary location or has extended beyond the site of origin.'

    
class TumorMarkerAnalyte(CodedConcept):
    valueset = 'https://simplifier.net/pop/ValueSets/pop-tumor-marker-analytes'
    description = 'Codes representing analytes for tumor markers.'

    @classmethod
    def transform(cls, concept):
        from pop.oncology.models.TumorMarker import ANALYTES_DATA
        analyte_data = ANALYTES_DATA.get(concept.code)
        concept.properties = analyte_data.model_dump(mode='json') if analyte_data else None
        return concept
    
class TumorMarkerTest(CodedConcept):
    valueset = 'https://simplifier.net/pop/ValueSets/pop-tumor-marker-test-codes'
    description = 'Codes representing tests for tumor markers. Extends the base valueset for tumor marker tests required for mCODE based on LOINC codes.'
    analyte = models.CharField(
     verbose_name=_('Analyte'),
     help_text=_('Analyte Name'),
     max_length=100,
     null=True, blank=True,
    )
    sample = models.CharField(
     verbose_name=_('Sample type'),
     help_text=_('System (Sample) Type'),
     max_length=100,
     null=True, blank=True,
    )
    method = models.CharField(
     verbose_name=_('Method type'),
     help_text=_('Type of Method'),
     max_length=100,
     null=True, blank=True,
    )
    type = models.CharField(
     verbose_name=_('Result type'),
     help_text=_('Type of unit'),
     max_length=100,
     null=True, blank=True,
    )  
    scale = models.CharField(
     verbose_name=_('Result scale'),
     help_text=_('Type of Scale'),
     max_length=20,
     null=True, blank=True,
    )  


class RaceCategory(CodedConcept):
    valueset =  'http://hl7.org/fhir/us/core/ValueSet/omb-race-category'
    description = 'Concepts classifying the person into a named category of humans sharing common history, traits, geographical origin or nationality.'
    def __str__(self):
        return self.display.title()


class BirthSex(CodedConcept):
    valueset =  'http://hl7.org/fhir/us/core/ValueSet/birthsex'
    description = 'Codes for assigning sex at birth as specified by the Office of the National Coordinator for Health IT (ONC).'


class BodyLocationAndLateralityQualifier(CodedConcept):
    valueset =  'http://hl7.org/fhir/us/mcode/ValueSet/mcode-body-location-and-laterality-qualifier-vs'
    description = 'Qualifiers to refine a body structure or location including qualifiers for relative location, directionality, number, plane, and laterality.'


class HumanSpecimenCollectionSite(CodedConcept):
    valueset =  None
    description = 'Anatomical or acquired body sites (body structure)'


class SmokingStatus(CodedConcept):
    valueset =  'https://vsac.nlm.nih.gov/valueset/2.16.840.1.113883.11.20.9.38/expansion'
    description = 'Current Smoking Status - IPS'
    @classmethod
    def transform(cls, concept):
        concept.display = concept.display.replace(' (finding)','')
        return concept


class CauseOfDeath(CodedConcept):
    valueset =  'https://simplifier.net/pop/ValueSets/pop-causes-of-death'
    description = 'Cause of death for oncology patients'


class TumorMorphology(CodedConcept):
    valueset =  'http://hl7.org/fhir/us/mcode/ValueSet/mcode-tumor-morphology-code-vs'
    description = 'Contains the preferred preferred (active) code for tumor morphology.'

 

class TumorSizeMethod(CodedConcept):
    valueset =  'http://hl7.org/fhir/us/mcode/ValueSet/mcode-tumor-size-method-vs'
    description = 'Code for methods of measuring tumor size, including physical examination, pathology, and imaging.'
    def __str__(self):
        return self.display.replace(' (procedure)','')
 

class MeasurementSetting(CodedConcept):
    valueset =  'http://hl7.org/fhir/us/vitals/ValueSet/MeasSettingVS'
    description = 'SELECT SNOMED CT code system values that contains terms that indicate the surroundings the individual was in during the measurement (i.e. home, clinic, hospital, etc.).'


class AdverseEventExpectation(CodedConcept):
    valueset =  'https://build.fhir.org/ig/standardhealth/fsh-ae/ValueSet-adverse-event-expectation-value-set.json'
    description = 'An expected adverse event is one whose nature and severity have been previously observed, identified in nature, severity, or frequency, and documented in the investigator brochure, investigational plan, protocol, current consent form, scientific publication, or in other relevant and reliable document. '


class AdverseEventSeriousnessOutcome(CodedConcept):
    valueset =  'https://build.fhir.org/ig/standardhealth/fsh-ae/ValueSet-adverse-event-seriousness-outcome-value-set.json'
    description = 'The outcome of a serious adverse event'


class AdverseEventSeriousness(CodedConcept):
    valueset =  'https://build.fhir.org/ig/standardhealth/fsh-ae/ValueSet-adverse-event-seriousness-value-set.json'
    description = 'An adverse event is classified as serious or non-serious.'


class AdverseEventTerm(CodedConcept):
    description = 'The NCI Common Terminology Criteria for Adverse Events (CTCAE) is utilized for Adverse Event (AE) reporting.'

class AdverseEventRelatedness(CodedConcept):
    valueset =  'https://build.fhir.org/ig/standardhealth/fsh-ae/ValueSet-adverse-event-relatedness-value-set.json'
    description = 'Codes qualifying the adverse event’s relationship to the medical intervention, according to WHO causality assessment criteria'
    def __str__(self):
        label = self.display
        label = label.replace('Adverse Event ','')
        label = label.replace(' to Intervention','')
        return f'{label}'


class HighLowInterpretation(CodedConcept):
    valueset =  'http://hl7.org/fhir/uv/genomics-reporting/ValueSet/high-low-codes-vs'
    description = 'This value set includes high/low codes for Observation Interpretations'


class GeneticVariantAssessment(CodedConcept):
    valueset =  'https://loinc.org/LL1971-2/'
    description = 'Genetic variant assessment codes'


class StructuralVariantAnalysisMethod(CodedConcept):
    valueset =  'https://loinc.org/LL4048-6/'
    description = 'Structural variant analysis methods'


class Gene(CodedConcept):
    valueset =  'http://hl7.org/fhir/uv/genomics-reporting/ValueSet/hgnc-vs'
    description = 'HUGO Gene Nomenclature Committee Gene Names (HGNC)'


class ReferenceGenomeBuild(CodedConcept):
    valueset =  'https://loinc.org/LL1040-6/'
    description = 'Human reference sequence NCBI build ID'


class DnaChangeType(CodedConcept):
    valueset =  'http://hl7.org/fhir/uv/genomics-reporting/ValueSet/dna-change-type-vs'
    description = 'DNA Change Type of a variant'
    def __str__(self):
        return self.display.replace('_',' ').capitalize()


class GeneticVariantSource(CodedConcept):
    valueset =  'https://loinc.org/LL378-1/'
    description = 'Genomic source class'


class Zygosity(CodedConcept):
    valueset =  'https://loinc.org/LL381-5/'
    description = 'Genetic variant allelic state'


class VariantInheritance(CodedConcept):
    valueset =  'http://hl7.org/fhir/uv/genomics-reporting/ValueSet/variant-inheritance-vs'
    description = 'By which parent the variant was inherited in the patient, if known.'


class ChromosomeIdentifier(CodedConcept):
    valueset =  'https://loinc.org/LL2938-0/'
    description = 'List of human chromosomes'


class AminoAcidChangeType(CodedConcept):
    valueset =  'https://loinc.org/LL380-7/'
    description = 'Amino acid change types'


class VariantConfidenceStatus(CodedConcept):
    valueset =  'http://hl7.org/fhir/uv/genomics-reporting/ValueSet/variant-confidence-status-vs'
    description = 'A code that classifies the confidence for calling this variant.'


class MolecularConsequence(CodedConcept):
    valueset =  'http://hl7.org/fhir/uv/genomics-reporting/ValueSet/molecular-consequence-vs'
    description = 'The calculated or observed effect of a variant on its downstream transcript and, if applicable, ensuing protein sequence.'
    def __str__(self):
        return self.display.replace('_',' ').capitalize()


class GenomicCoordinateSystem(CodedConcept):
    valueset =  'https://loinc.org/LL5323-2/'
    description = 'Genomic coordinate system'


class MicrosatelliteInstabilityState(CodedConcept):
    valueset =  'https://loinc.org/LL3994-2/'
    description = 'Microsatellite instability in Cancer specimen Qualitative'


class GeneticFollowupRecommendation(CodedConcept):
    valueset =  'https://loinc.org/LL1037-2/'
    description = 'Genetic follow up recommendations'


class MedicationUsageSuggestion(CodedConcept):
    valueset =  'https://loinc.org/LL4049-4/'
    description = 'Medication usage suggestion'


class VariantClinicalSignificance(CodedConcept):
    valueset =  'https://loinc.org/LL4034-6/'
    description = 'ACMG_Clinical significance of genetic variation '
    # Additional codes for an extensible valuset
    extension_concepts = [
        CodedConceptSchema(code='LA20926-4', system='http://loinc.org/', display='Ambiguous')
    ]


class FunctionalEffect(CodedConcept):
    valueset =  'http://hl7.org/fhir/uv/genomics-reporting/ValueSet/functional-effect-vs'
    description = 'The effect of a variant on downstream biological products or pathways.'
    def __str__(self):
        return self.display.replace('_',' ').capitalize()


class GeneticTherapeuticImplication(CodedConcept):
    valueset =  'http://hl7.org/fhir/uv/genomics-reporting/ValueSet/genetic-therapeutic-implications-vs'
    description = 'Value Set for terms that describe a predicted ramification based on the presence of associated molecular finding(s).'


class TreatmentCategory(CodedConcept):
    valueset =  'https://simplifier.net/pop/ValueSets/pop-treatment-categories'
    description = 'Codes representing the order in which different therapies are given to people as their disease progresses.'
    # Additional codes
    extension_concepts = [
        CodedConceptSchema(code='1287211007', system='http://snomed.info/sct', display='No information available', version='http://snomed.info/sct/900000000000207008')
    ]
    def __str__(self):
        return self.display.replace('therapy','').replace('care','').replace(' Therapy','').replace('treatment','').replace('drug','').replace('antineoplastic','')

class CancerTreatmentResponseObservationMethod(CodedConcept):
    valueset =  'https://simplifier.net/pop/ValueSets/pop-cancer-treatment-response-observation-methods'
    description = 'Codes representing the observation methods to study the response of a cancer to treatment'
    extension_concepts = [
        CodedConceptSchema(code='1287211007',system='http://snomed.info/sct', display='No information available', version='http://snomed.info/sct/900000000000207008')
    ]


class TreatmentResponseInterpretation(CodedConcept):
    valueset =  'https://simplifier.net/pop/ValueSets/pop-treatment-response-interpretations'
    description = 'Codes representing whether the RECIST results where interpreted or directly reported.'


class CancerTreatmentResponse(CodedConcept):
    valueset =  'https://loinc.org/LL4721-8/'
    description = 'Codes representing the RECIST results'


class MolecularTumorBoardRecommendation(CodedConcept):
    valueset =  'https://simplifier.net/pop/ValueSets/pop-molecular-tumor-board-recommendations'
    description = 'Codes representing molecular tumor board recommendations'

class TumorBoardRecommendation(CodedConcept):
    valueset =  'https://simplifier.net/pop/ValueSets/pop-tumor-board-recommendations'
    description = 'Codes representing  tumor board  recommendations'


class ICD10Condition(CodedConcept):
    valueset =  'http://hl7.org/fhir/ValueSet/icd-10'
    description = 'Codes representing comorbid conditions in the ICD-10 system'

class PDL1TumorCellScore(CodedConcept):
    valueset =  'https://simplifier.net/pop/ValueSets/pop-pdl1-tumor-cell-scores'
    description = 'Score values for classification of the expression evidence for PD-L1 immunihistochemistry analyses measuring tumor cells'


class PDL1ImmuneCellScore(CodedConcept):
    valueset =  'https://simplifier.net/pop/ValueSets/pop-pdl1-immune-cell-scores'
    description = 'Score values for classification of the expression evidence for PD-L1 immunihistochemistry analyses'


class HistoryOfMetastaticMalignantNeoplasm(CodedConcept):
    valueset =  'http://hl7.org/fhir/us/mcode/ValueSet/mcode-history-of-metastatic-malignant-neoplasm-vs'
    description = 'Codes representing different scores to quantify the expression of PD-L1 obtained from immunohistochemistry tests'


class MedicationRequestIntent(CodedConcept):
    valueset =  'http://hl7.org/fhir/ValueSet/medicationrequest-intent'
    description = 'Intent for a given medication request.'


class MedicationRequestCategory(CodedConcept):
    valueset =  'http://hl7.org/fhir/ValueSet/medicationrequest-category'
    description = 'Category of a given medication request.'


class DoseAndRateType(CodedConcept):
    valueset =  'http://terminology.hl7.org/CodeSystem/dose-rate-type'
    description = 'The kind of dose or rate specified.'


class HumanSpecimenType(CodedConcept):
    valueset =  'http://hl7.org/fhir/us/mcode/ValueSet/mcode-human-specimen-type-vs'
    description = 'Concepts that describe the precise nature of an entity that may be used as the source material for an observation.'
    PathoProCode = models.CharField(
        help_text=_('Deprecated SNOMED (pre1998) codes used by PathoPro'),
        max_length=100,
        null=True,
    )
    extension_concepts = [
        CodedConceptSchema(code='1285453009', system='http://snomed.info/sct', display='Liquid biopsy'),
    ] 


class AdverseEventActuality(CodedConcept):
    valueset =  'http://hl7.org/fhir/ValueSet/adverse-event-actuality'
    description = 'Overall nature of the adverse event, e.g. real or potential.'


class CTCAEGrade(CodedConcept):
    valueset =  'https://build.fhir.org/ig/standardhealth/fsh-ae/CodeSystem-ctcae-grade-code-system.json'
    description = 'CTCAE Grades 0 through 5. The grade of the adverse event, determined by CTCAE criteria, where 0 represents confirmation that the given adverse event did NOT occur, and 5 represents death. Note that grade 0 events are generally not reportable, but may be created to give positive confirmation that the clinician assessed or considered a particular AE.'


class AdverseEventSeverity(CodedConcept):
    valueset =  'http://hl7.org/fhir/ValueSet/adverse-event-severity'
    description = 'The severity of the adverse event itself, in direct relation to the subject.'


class AdverseEventOutcome(CodedConcept):
    valueset =  'http://hl7.org/fhir/ValueSet/adverse-event-outcome'
    description = 'N/A'


class ResearchStudyPhase(CodedConcept):
    valueset = 'http://hl7.org/fhir/ValueSet/research-study-phase'
    description = 'Codes for the stage in the progression of a therapy from initial experimental use in humans in clinical trials to post-market evaluation.'


class ResearchStudyStatus(CodedConcept):
    valueset =  'http://hl7.org/fhir/ValueSet/research-study-status'
    description = 'Codes that convey the current status of the research study.'


class ResearchStudyPrimaryPurposeType(CodedConcept):
    valueset =  'http://hl7.org/fhir/ValueSet/research-study-prim-purp-type'
    description = 'Codes for the main intent of the study'


class ConsentState(CodedConcept):
    valueset = 'http://hl7.org/fhir/ValueSet/consent-state-codes'
    description = 'Indicates the state of the consent.'


class ConsentScope(CodedConcept):
    valueset = 'http://hl7.org/fhir/ValueSet/consent-scope'
    description = 'This value set includes the four Consent scope codes.'


class ExpectedDrugAction(CodedConcept):
    valueset = 'https://simplifier.net/pop/ValueSets/pop-expected-drug-action'
    description = 'Expected action of a drug'


class TumorMarkerTestResult(CodedConcept):
    valueset = 'https://simplifier.net/pop/ValueSets/pop-tumor-marker-test-results'
    description = 'Collection of LOINC codes that represent results of tumor marker tests'


class RecreationalDrug(CodedConcept):
    valueset = 'https://simplifier.net/pop/ValueSets/pop-recreational-drugs'
    description = 'Substances that people use to alter their mental state, often for pleasure or leisure, with effects ranging from relaxation and euphoria to hallucinations and altered perceptions.'


class ExposureAgent(CodedConcept):
    valueset = 'https://simplifier.net/pop/ValueSets/pop-exposure-agents'
    description = 'Agents to which a person is exposed as part of their occupation or environment'


class AdverseEventMitigationTreatmentAdjustment(CodedConcept):
    valueset = 'https://simplifier.net/pop/ValueSets/pop-adverse-event-mitigation-treatment-adjustment'
    description = "Adjustments made to a patient's treatment plan in response to an adverse event."


class AdverseEventMitigationDrug(CodedConcept):
    valueset = 'https://simplifier.net/pop/ValueSets/pop-adverse-event-mitigation-drugs'
    description = "Drug or medication categories used in the mitigation process of an adverse event."


class AdverseEventMitigationProcedure(CodedConcept):
    valueset = 'https://simplifier.net/pop/ValueSets/pop-adverse-event-mitigation-procedures'
    description = "Procedures undertaken to mitigate the impact of an adverse event on a patient's health."


class AdverseEventMitigationManagement(CodedConcept):
    valueset = 'https://simplifier.net/pop/ValueSets/pop-adverse-event-mitigation-management'
    description = "Classification of actions to mitigate adverse events affecting a patient's health."
    def __str__(self):
        return self.display.replace('management','')

class CancerRiskAssessmentMethod(CodedConcept):
    valueset = 'https://simplifier.net/pop/ValueSets/pop-cancer-risk-assessment-methods'
    description = "Methods used to assess the risk in cancer"

class CancerRiskAssessmentClassification(CodedConcept):
    valueset = 'https://simplifier.net/pop/ValueSets/pop-cancer-risk-assessment-values'
    description = "Classification of cancer risk assessment"

class NCITCancerClassification(CodedConcept):
    valueset = None
    description = "Cancer classification by the NCIT"

class OncoTreeCancerClassification(CodedConcept):
    codesystem = 'http://oncotree.mskcc.org/fhir/CodeSystem/snapshot'
    description = "Cancer classification by OncoTree"
