import factory
from factory.fuzzy import FuzzyChoice
import faker
import random 

from django.contrib.auth.models import Group, User
from django.contrib.auth.hashers import make_password

import pop.core.measures as measures
import pop.oncology.models as models
import pop.terminology.models as terminology

import sys

def is_running_pytest():
    return "pytest" in sys.modules

faker = faker.Faker()

class TerminologyFactory(factory.django.DjangoModelFactory):
       class Meta:
        django_get_or_create = ('code','system')

def make_terminology_factory(terminology, code_iterator=None):
    if not code_iterator:
        code_iterator = [f"{terminology.__name__.lower()}-code-{n+1}" for n in range(4)]
    display_iterator = [code.replace('-code',' ').replace('-',' ').capitalize() for code in code_iterator]
    if is_running_pytest():
        return factory.SubFactory(factory.make_factory(terminology,
            code = factory.Iterator(code_iterator),
            display = factory.Iterator(display_iterator),
            system = f'http://test.org/codesystem/{terminology.__name__.lower()}',
            FACTORY_CLASS=TerminologyFactory,
        ))
    else:
        return factory.LazyFunction(lambda: terminology.objects.all()[random.randint(0,terminology.objects.count()-1)])

class GroupFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Group
    name = factory.Sequence(lambda n: "Group #%s" % n)


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
    username = factory.LazyFunction(lambda: faker.profile()['username'])
    password = factory.LazyFunction(lambda: make_password(faker.password()))
    email = factory.LazyAttribute(lambda obj: '%s@example.com' % obj.username)


class PatientCaseFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.PatientCase
    created_by =  factory.SubFactory(UserFactory)
    date_of_birth = factory.LazyFunction(lambda: faker.date_of_birth(minimum_age=25, maximum_age=100))
    gender = make_terminology_factory(terminology.AdministrativeGender)
    race = make_terminology_factory(terminology.RaceCategory)
    sex_at_birth = make_terminology_factory(terminology.BirthSex)
    date_of_death = factory.LazyFunction(lambda: faker.date_this_decade() if random.random() > 0.5 else None)
    cause_of_death = make_terminology_factory(terminology.CauseOfDeath)

class PatientCaseDataCompletionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.PatientCaseDataCompletion
    case = factory.SubFactory(PatientCaseFactory)
    category = factory.LazyFunction(lambda: [category for category in list(models.PatientCaseDataCompletion.PatientCaseDataCategories)[0:random.randint(1,3)]])

class PrimaryNeoplasticEntityFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.NeoplasticEntity
    relationship = 'primary'
    case = factory.SubFactory(PatientCaseFactory)
    assertion_date = factory.LazyFunction(lambda: faker.date())
    topography = make_terminology_factory(terminology.CancerTopography)
    morphology = make_terminology_factory(terminology.CancerMorphology)
    differentitation = make_terminology_factory(terminology.HistologyDifferentiation) 
    laterality = make_terminology_factory(terminology.LateralityQualifier)
    created_by =  factory.SubFactory(UserFactory)


class MetastaticNeoplasticEntityFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.NeoplasticEntity
    relationship = 'metastatic'
    case = factory.SubFactory(PatientCaseFactory)
    assertion_date = factory.LazyFunction(lambda: faker.date())
    related_primary = factory.SubFactory(PrimaryNeoplasticEntityFactory)
    topography = make_terminology_factory(terminology.CancerTopography)
    morphology = make_terminology_factory(terminology.CancerMorphology)
    differentitation = make_terminology_factory(terminology.HistologyDifferentiation) 
    laterality = make_terminology_factory(terminology.LateralityQualifier)
    created_by =  factory.SubFactory(UserFactory)


class TNMStagingFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.TNMStaging
    case = factory.SubFactory(PatientCaseFactory)
    date = factory.LazyFunction(faker.date)    
    stage = make_terminology_factory(terminology.TNMStage, code_iterator=[f"tnm-stage-{n+1}-code" for n in range(5)])
    methodology = make_terminology_factory(terminology.TNMStagingMethod)
    created_by =  factory.SubFactory(UserFactory)

class FIGOStagingFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.FIGOStaging
    case = factory.SubFactory(PatientCaseFactory)
    date = factory.LazyFunction(faker.date)    
    stage = make_terminology_factory(terminology.FIGOStage, code_iterator=[f"figo-stage-{n+1}-code" for n in range(5)])
    methodology = make_terminology_factory(terminology.FIGOStagingMethod)
    created_by =  factory.SubFactory(UserFactory)



class TumorMarkerTestFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.TumorMarker
    analyte = make_terminology_factory(terminology.TumorMarkerAnalyte)
    case = factory.SubFactory(PatientCaseFactory)
    date = factory.LazyFunction(faker.date)    
    mass_concentration = factory.LazyFunction(lambda: measures.MassConcentration(g__l=random.random()))    
    created_by =  factory.SubFactory(UserFactory)



class RiskAssessmentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.RiskAssessment
    case = factory.SubFactory(PatientCaseFactory)
    date = factory.LazyFunction(faker.date)    
    methodology = make_terminology_factory(terminology.CancerRiskAssessmentMethod)
    risk = make_terminology_factory(terminology.CancerRiskAssessmentClassification)
    created_by =  factory.SubFactory(UserFactory)


class SystemicTherapyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.SystemicTherapy

    case = factory.SubFactory(PatientCaseFactory)
    period = factory.LazyFunction(lambda: (faker.date_between(start_date='-1y', end_date='today'), faker.date_between(start_date='today', end_date='+1y')))
    cycles = factory.LazyFunction(lambda: random.randint(2,25))
    intent = FuzzyChoice(models.SystemicTherapy.TreatmentIntent)
    role = make_terminology_factory(terminology.TreatmentCategory)

class SystemicTherapyMedicationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.SystemicTherapyMedication    
    systemic_therapy = factory.SubFactory(SystemicTherapyFactory)
    drug = make_terminology_factory(terminology.AntineoplasticAgent)
    route = make_terminology_factory(terminology.DosageRoute)


class SurgeryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Surgery
    case = factory.SubFactory(PatientCaseFactory)
    date = factory.LazyFunction(faker.date)    
    procedure = make_terminology_factory(terminology.SurgicalProcedure)
    intent = FuzzyChoice(models.Surgery.TreatmentIntent)
    bodysite = make_terminology_factory(terminology.CancerTopography)
    bodysite_qualifier = make_terminology_factory(terminology.BodyLocationQualifier)
    bodysite_laterality = make_terminology_factory(terminology.LateralityQualifier)
    outcome = make_terminology_factory(terminology.ProcedureOutcome)


class RadiotherapyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Radiotherapy

    case = factory.SubFactory(PatientCaseFactory)
    period = factory.LazyFunction(lambda: (faker.date_between(start_date='-1y', end_date='today'), faker.date_between(start_date='today', end_date='+1y')))
    sessions = factory.LazyFunction(lambda: random.randint(2,25))
    intent = FuzzyChoice(models.Radiotherapy.TreatmentIntent)

class RadiotherapyDosageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.RadiotherapyDosage    
    radiotherapy = factory.SubFactory(RadiotherapyFactory)
    fractions = factory.LazyFunction(lambda: random.randint(2,25))
    dose = factory.LazyFunction(lambda: measures.RadiationDose(Gy=random.random()))    
    irradiated_volume = make_terminology_factory(terminology.RadiotherapyTreatmentLocation)
    irradiated_volume_morphology = make_terminology_factory(terminology.RadiotherapyVolumeType)

class RadiotherapySettingFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.RadiotherapySetting    
    radiotherapy = factory.SubFactory(RadiotherapyFactory)
    modality = make_terminology_factory(terminology.RadiotherapyModality)
    technique = make_terminology_factory(terminology.RadiotherapyTechnique)


class TreatmentResponseFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.TreatmentResponse
    case = factory.SubFactory(PatientCaseFactory)
    date = factory.LazyFunction(faker.date)    
    recist = make_terminology_factory(terminology.CancerTreatmentResponse)
    recist_interpreted = factory.LazyFunction(lambda: random.randint(0,100)>50)
    methodology = make_terminology_factory(terminology.CancerTreatmentResponseObservationMethod)
    assessed_bodysite = make_terminology_factory(terminology.ObservationBodySite)


class GenomicVariantFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.GenomicVariant    
    case = factory.SubFactory(PatientCaseFactory)
    date = factory.LazyFunction(faker.date)    
    gene_panel = factory.LazyFunction(faker.company)
    assessment = FuzzyChoice(models.GenomicVariant.GenomicVariantAssessment)
    confidence = FuzzyChoice(models.GenomicVariant.GenomicVariantConfidence)
    clinical_relevance = FuzzyChoice(models.GenomicVariant.GenomicVariantClinicalRelevance)
    analysis_method = make_terminology_factory(terminology.StructuralVariantAnalysisMethod)
    cytogenetic_location = factory.LazyFunction(lambda: f'{random.randint(1,22)}p{random.randint(11,22)}')
    genomic_refseq = factory.LazyFunction(lambda: f'NG000{random.randint(100,999)}.{random.randint(1,9)}')
    transcript_refseq = factory.LazyFunction(lambda: f'NM000{random.randint(100,999)}.{random.randint(1,9)}')
    coding_hgvs = factory.LazyFunction(lambda: f'NM000{random.randint(100,999)}.{random.randint(1,9)}:c.{random.randint(10,10000)}C>T')
    protein_hgvs = factory.LazyFunction(lambda: f'NP000{random.randint(100,999)}.{random.randint(1,9)}:p.{random.randint(10,10000)}Lys>Val')
    aminoacid_change_type = make_terminology_factory(terminology.AminoAcidChangeType)
    molecular_consequence = make_terminology_factory(terminology.MolecularConsequence)
    copy_number = factory.LazyFunction(lambda: random.randint(1,9))
    allele_frequency = factory.LazyFunction(lambda: random.randint(0,100)/100)
    allele_depth = factory.LazyFunction(lambda: random.randint(0,99999))
    zygosity = make_terminology_factory(terminology.Zygosity)
    exact_genomic_coordinates = factory.LazyFunction(lambda: (random.randint(0,9999), random.randint(9999,99999999)))

class PerformanceStatusFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.PerformanceStatus
    case = factory.SubFactory(PatientCaseFactory)
    date = factory.LazyFunction(faker.date)    
    ecog_score = factory.LazyFunction(lambda: random.randint(0,5))
    karnofsky_score = factory.LazyFunction(lambda: random.randint(0,100))


class LifestyleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Lifestyle
    case = factory.SubFactory(PatientCaseFactory)
    date = factory.LazyFunction(faker.date)    
    smoking_status = make_terminology_factory(terminology.SmokingStatus)
    smoking_packyears = factory.LazyFunction(lambda: random.random())
    smoking_quited = factory.LazyFunction(lambda: measures.Time(year=random.random()))    
    alcohol_consumption = make_terminology_factory(terminology.AlcoholConsumptionFrequency)
    night_sleep = factory.LazyFunction(lambda: measures.Time(hour=random.random()))    



class FamilyHistoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.FamilyHistory
    case = factory.SubFactory(PatientCaseFactory)
    date = factory.LazyFunction(faker.date)    
    relationship = make_terminology_factory(terminology.FamilyMemberType)
    had_cancer = factory.LazyFunction(lambda: random.randint(0,10) > 5)
    contributed_to_death = factory.LazyFunction(lambda: random.randint(0,10) > 5)
    onset_age = factory.LazyFunction(lambda: random.randint(25,95))
    topography = make_terminology_factory(terminology.CancerTopography)
    morphology = make_terminology_factory(terminology.CancerMorphology)
    

class TumorMutationalBurdenFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.TumorMutationalBurden
    case = factory.SubFactory(PatientCaseFactory)
    date = factory.LazyFunction(faker.date)    
    value = factory.LazyFunction(lambda: random.randint(25,95)/5)
    status = FuzzyChoice(models.TumorMutationalBurden.TumorMutationalBurdenStatus)

class LossOfHeterozygosityFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.LossOfHeterozygosity
    case = factory.SubFactory(PatientCaseFactory)
    date = factory.LazyFunction(faker.date)    
    value = factory.LazyFunction(lambda: float(random.randint(0,100)))

class MicrosatelliteInstabilityFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.MicrosatelliteInstability
    case = factory.SubFactory(PatientCaseFactory)
    date = factory.LazyFunction(faker.date)    
    value = make_terminology_factory(terminology.MicrosatelliteInstabilityState)

class HomologousRecombinationDeficiencyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.HomologousRecombinationDeficiency
    case = factory.SubFactory(PatientCaseFactory)
    date = factory.LazyFunction(faker.date)    
    value = factory.LazyFunction(lambda: random.randint(0,100)*1.0)
    interpretation = FuzzyChoice(models.HomologousRecombinationDeficiency.HomologousRecombinationDeficiencyPresence)

class TumorNeoantigenBurdenFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.TumorNeoantigenBurden
    case = factory.SubFactory(PatientCaseFactory)
    date = factory.LazyFunction(faker.date)    
    value = factory.LazyFunction(lambda: random.randint(0,50)/6)

class AneuploidScoreFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.AneuploidScore
    case = factory.SubFactory(PatientCaseFactory)
    date = factory.LazyFunction(faker.date)    
    value = factory.LazyFunction(lambda: random.randint(0,36))


class ComorbiditiesAssessmentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.ComorbiditiesAssessment
    case = factory.SubFactory(PatientCaseFactory)
    date = factory.LazyFunction(faker.date)    
    indexCondition = factory.SubFactory(PrimaryNeoplasticEntityFactory)
    panel = FuzzyChoice(models.ComorbiditiesPanel)

class VitalsFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Vitals
    case = factory.SubFactory(PatientCaseFactory)
    date = factory.LazyFunction(faker.date)    
    height = factory.LazyFunction(lambda: measures.Distance(m=random.randint(150,190)/100))  
    weight = factory.LazyFunction(lambda: measures.Mass(kg=random.randint(55, 95)))     
    blood_pressure_systolic = factory.LazyFunction(lambda: measures.Pressure(mmHg=random.randint(100, 120)))     
    blood_pressure_diastolic = factory.LazyFunction(lambda: measures.Pressure(mmHg=random.randint(65, 85)))     
    temperature = factory.LazyFunction(lambda: measures.Temperature(c=random.randint(37, 40)))     


def fake_complete_case():
    case = PatientCaseFactory.create()
    PrimaryNeoplasticEntityFactory.create(case=case)
    if random.randint(0,100) > 40:
        MetastaticNeoplasticEntityFactory.create(case=case)
    TNMStagingFactory.create(case=case)
    for _ in range(random.randint(0,4)):
        systemic_therapy = SystemicTherapyFactory.create(case=case)
        for _ in range(random.randint(1,3)):
            SystemicTherapyMedicationFactory.create(systemic_therapy=systemic_therapy)
    for _ in range(random.randint(0,2)):
        radiotherapy = RadiotherapyFactory.create(case=case)
        for _ in range(random.randint(1,3)):
            RadiotherapyDosageFactory.create(radiotherapy=radiotherapy)
    for _ in range(random.randint(0,4)):
        TumorMarkerTestFactory.create(case=case)
    for _ in range(random.randint(0,12)):
        GenomicVariantFactory.create(case=case)
    if random.randint(0,100) > 50:
        TumorMutationalBurdenFactory.create(case=case)
    if random.randint(0,100) > 50:
        LossOfHeterozygosityFactory.create(case=case)
    if random.randint(0,100) > 50:
        MicrosatelliteInstabilityFactory.create(case=case)
    FamilyHistoryFactory.create(case=case)
    return case