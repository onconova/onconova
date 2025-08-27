import random
import string
import sys
from datetime import datetime, timedelta

import factory
import faker as fakerModule
import pghistory
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Group
from factory.fuzzy import FuzzyChoice, FuzzyText
from psycopg.types.range import Range as PostgresRange

import pop.core.measures as measures
import pop.oncology.models as models
import pop.research.models.cohort as cohorts_models
import pop.research.models.project as projects_models
import pop.terminology.models as terminology
from pop.core.auth.models import User
from pop.oncology.models.patient_case import VitalStatus
from pop.oncology.models.comorbidities import ComorbiditiesPanel


def is_running_pytest():
    return "pytest" in sys.modules


faker = fakerModule.Faker()


class TerminologyFactory(factory.django.DjangoModelFactory):
    class Meta:
        django_get_or_create = ("code", "system")


def make_terminology_factory(
    terminology: type[terminology.CodedConcept], code_iterator=None
) -> factory.SubFactory | factory.LazyFunction | None:
    if not code_iterator:
        code_iterator = [f"{terminology.__name__.lower()}-code-{n+1}" for n in range(4)]
    display_iterator = [
        code.replace("-code", " ").replace("-", " ").capitalize()
        for code in code_iterator
    ]
    if is_running_pytest():
        return factory.SubFactory(
            factory.make_factory(
                terminology,
                code=factory.Iterator(code_iterator),
                display=factory.Iterator(display_iterator),
                system=f"http://test.org/codesystem/{terminology.__name__.lower()}",
                FACTORY_CLASS=TerminologyFactory,
            )
        )
    else:
        concepts_count = terminology.objects.count()
        return (
            factory.LazyFunction(
                lambda: terminology.objects.all()[random.randint(0, concepts_count - 1)]
            )
            if concepts_count
            else None
        )


def make_m2m_terminology_factory(field, terminology_model, min=1, max=2):
    def set_m2m_terminology(self, create, extracted, **kwargs):
        if not create:
            # Simple build, or nothing to add, do nothing.
            return
        if extracted is None:
            terminology = make_terminology_factory(terminology_model)
            extracted = [
                (
                    terminology.get_factory()()
                    if isinstance(terminology, factory.SubFactory)
                    else (
                        terminology.function()
                        if isinstance(terminology, factory.LazyFunction)
                        else None
                    )
                )
                for _ in range(random.randint(min, max))
            ]
        # Add the iterable of groups using bulk addition
        getattr(self, field).set(extracted)

    return set_m2m_terminology


def add_m2m_related(
    field, factory, min=1, max=2, get_related_case=lambda self: self.case, post=None
):
    def set_m2m_related(self, create, extracted, **kwargs):
        if not create:
            # Simple build, or nothing to add, do nothing.
            return
        if extracted is None:
            if get_related_case:
                extracted = [
                    factory(case=get_related_case(self))
                    for _ in range(random.randint(min, max))
                ]
            else:
                extracted = [factory.create() for _ in range(random.randint(min, max))]
        # Add the iterable of groups using bulk addition
        getattr(self, field).set(extracted)
        if post:
            post(self)

    return set_m2m_related


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    first_name = factory.LazyFunction(lambda: faker.first_name())
    last_name = factory.LazyFunction(lambda: faker.last_name())
    username = factory.LazyAttribute(
        lambda obj: f"{obj.last_name[:2].lower()}{obj.first_name[:2].lower()}{random.randint(111,999)}"
    )
    password = factory.LazyFunction(lambda: make_password(faker.password()))
    email = factory.LazyAttribute(lambda obj: "%s@outlook.com" % obj.username)
    access_level = factory.LazyFunction(lambda: random.randint(0, 3))


class PatientCaseFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.PatientCase

    date_of_birth = factory.LazyFunction(
        lambda: faker.date_of_birth(minimum_age=35, maximum_age=100)
    )
    gender = make_terminology_factory(terminology.AdministrativeGender)
    sex_at_birth = make_terminology_factory(terminology.BirthSex)
    vital_status = FuzzyChoice(VitalStatus)
    date_of_death = factory.LazyAttribute(
        lambda o: faker.date_this_decade() if o.vital_status == VitalStatus.DECEASED else None
    )
    cause_of_death = factory.Maybe(
        factory.LazyAttribute(lambda o: o.vital_status == VitalStatus.DECEASED),
        make_terminology_factory(terminology.CauseOfDeath), None, # type: ignore
    )
    end_of_records = factory.LazyAttribute(
        lambda o: faker.date_this_decade() if o.vital_status == VitalStatus.UNKNOWN else None
    )
    consent_status = FuzzyChoice(models.PatientCase.ConsentStatus)
    clinical_center = factory.LazyFunction(lambda: faker.company() + " Hospital")
    clinical_identifier = FuzzyText(length=8, prefix="CLIN", chars=string.digits)


class PatientCaseDataCompletionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.PatientCaseDataCompletion

    case = factory.SubFactory(PatientCaseFactory)
    category = factory.LazyFunction(
        lambda: [
            category.value
            for category in list(
                models.PatientCaseDataCompletion.PatientCaseDataCategories
            )[0 : random.randint(1, 6)]
        ]
    )


class PrimaryNeoplasticEntityFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.NeoplasticEntity

    relationship = "primary"
    case = factory.SubFactory(PatientCaseFactory)
    assertion_date = factory.LazyFunction(lambda: faker.date())
    topography = make_terminology_factory(terminology.CancerTopography)
    morphology = make_terminology_factory(terminology.CancerMorphology)
    differentitation = make_terminology_factory(terminology.HistologyDifferentiation)
    laterality = make_terminology_factory(terminology.LateralityQualifier)


class MetastaticNeoplasticEntityFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.NeoplasticEntity

    relationship = "metastatic"
    case = factory.SubFactory(PatientCaseFactory)
    assertion_date = factory.LazyFunction(lambda: faker.date())
    related_primary = factory.SubFactory(PrimaryNeoplasticEntityFactory)
    topography = make_terminology_factory(terminology.CancerTopography)
    morphology = make_terminology_factory(terminology.CancerMorphology)
    differentitation = make_terminology_factory(terminology.HistologyDifferentiation)
    laterality = make_terminology_factory(terminology.LateralityQualifier)


class TNMStagingFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.TNMStaging

    case = factory.SubFactory(PatientCaseFactory)
    date = factory.LazyFunction(faker.date)
    stage = make_terminology_factory(
        terminology.TNMStage, code_iterator=[f"tnm-stage-{n+1}-code" for n in range(5)]
    )
    methodology = make_terminology_factory(terminology.TNMStagingMethod)
    staged_entities = factory.post_generation(
        add_m2m_related("staged_entities", PrimaryNeoplasticEntityFactory, min=1, max=1)
    )


class FIGOStagingFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.FIGOStaging

    case = factory.SubFactory(PatientCaseFactory)
    date = factory.LazyFunction(faker.date)
    stage = make_terminology_factory(
        terminology.FIGOStage,
        code_iterator=[f"figo-stage-{n+1}-code" for n in range(5)],
    )
    methodology = make_terminology_factory(terminology.FIGOStagingMethod)
    staged_entities = factory.post_generation(
        add_m2m_related("staged_entities", PrimaryNeoplasticEntityFactory, min=1, max=1)
    )


class TumorMarkerTestFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.TumorMarker

    analyte = make_terminology_factory(terminology.TumorMarkerAnalyte)
    case = factory.SubFactory(PatientCaseFactory)
    date = factory.LazyFunction(faker.date)
    mass_concentration = factory.LazyFunction(
        lambda: measures.MassConcentration(g__l=random.random())
    )
    related_entities = factory.post_generation(
        add_m2m_related(
            "related_entities", PrimaryNeoplasticEntityFactory, min=1, max=1
        )
    )


class RiskAssessmentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.RiskAssessment

    case = factory.SubFactory(PatientCaseFactory)
    date = factory.LazyFunction(faker.date)
    methodology = make_terminology_factory(terminology.CancerRiskAssessmentMethod)
    risk = make_terminology_factory(terminology.CancerRiskAssessmentClassification)
    assessed_entities = factory.post_generation(
        add_m2m_related(
            "assessed_entities", PrimaryNeoplasticEntityFactory, min=1, max=1
        )
    )


class TherapyLineFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.TherapyLine

    case = factory.SubFactory(PatientCaseFactory)
    intent = FuzzyChoice(models.TherapyLine.TreatmentIntent)
    ordinal = factory.LazyFunction(lambda: random.randint(1, 5))


class SystemicTherapyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.SystemicTherapy

    case = factory.SubFactory(PatientCaseFactory)
    period = factory.LazyFunction(
        lambda: PostgresRange(
            faker.date_between(start_date="-1y", end_date="today"),
            faker.date_between(start_date="today", end_date="+1y"),
        )
    )
    cycles = factory.LazyFunction(lambda: random.randint(2, 25))
    intent = FuzzyChoice(models.SystemicTherapy.TreatmentIntent)
    therapy_line = factory.SubFactory(TherapyLineFactory)
    targeted_entities = factory.post_generation(
        add_m2m_related(
            "targeted_entities", PrimaryNeoplasticEntityFactory, min=1, max=1
        )
    )


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
    therapy_line = factory.SubFactory(TherapyLineFactory)
    targeted_entities = factory.post_generation(
        add_m2m_related(
            "targeted_entities", PrimaryNeoplasticEntityFactory, min=1, max=1
        )
    )


class RadiotherapyFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Radiotherapy

    case = factory.SubFactory(PatientCaseFactory)
    period = factory.LazyFunction(
        lambda: PostgresRange(
            faker.date_between(start_date="-1y", end_date="today"),
            faker.date_between(start_date="today", end_date="+1y"),
        )
    )
    sessions = factory.LazyFunction(lambda: random.randint(2, 25))
    intent = FuzzyChoice(models.Radiotherapy.TreatmentIntent)
    therapy_line = factory.SubFactory(TherapyLineFactory)
    targeted_entities = factory.post_generation(
        add_m2m_related(
            "targeted_entities", PrimaryNeoplasticEntityFactory, min=1, max=1
        )
    )


class RadiotherapyDosageFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.RadiotherapyDosage

    radiotherapy = factory.SubFactory(RadiotherapyFactory)
    fractions = factory.LazyFunction(lambda: random.randint(2, 25))
    dose = factory.LazyFunction(lambda: measures.RadiationDose(Gy=random.random()))
    irradiated_volume = make_terminology_factory(
        terminology.RadiotherapyTreatmentLocation
    )
    irradiated_volume_morphology = make_terminology_factory(
        terminology.RadiotherapyVolumeType
    )


class RadiotherapySettingFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.RadiotherapySetting

    radiotherapy = factory.SubFactory(RadiotherapyFactory)
    modality = make_terminology_factory(terminology.RadiotherapyModality)
    technique = make_terminology_factory(terminology.RadiotherapyTechnique)


class AdverseEventFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.AdverseEvent

    case = factory.SubFactory(PatientCaseFactory)
    date = factory.LazyFunction(faker.date)
    grade = factory.LazyFunction(lambda: random.randint(0, 5))
    event = make_terminology_factory(terminology.AdverseEventTerm)
    outcome = FuzzyChoice(models.AdverseEvent.AdverseEventOutcome)


class AdverseEventSuspectedCauseFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.AdverseEventSuspectedCause

    adverse_event = factory.SubFactory(AdverseEventFactory)
    systemic_therapy = factory.SubFactory(SystemicTherapyFactory)
    causality = FuzzyChoice(models.AdverseEventSuspectedCause.AdverseEventCausality)


class AdverseEventMitigationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.AdverseEventMitigation

    adverse_event = factory.SubFactory(AdverseEventFactory)
    category = FuzzyChoice(models.AdverseEventMitigation.AdverseEventMitigationCategory)
    adjustment = make_terminology_factory(
        terminology.AdverseEventMitigationTreatmentAdjustment
    )
    drug = make_terminology_factory(terminology.AdverseEventMitigationDrug)
    procedure = make_terminology_factory(terminology.AdverseEventMitigationProcedure)
    management = make_terminology_factory(terminology.AdverseEventMitigationManagement)


class TreatmentResponseFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.TreatmentResponse

    case = factory.SubFactory(PatientCaseFactory)
    date = factory.LazyFunction(faker.date)
    recist = make_terminology_factory(terminology.CancerTreatmentResponse)
    recist_interpreted = factory.LazyFunction(lambda: random.randint(0, 100) > 50)
    methodology = make_terminology_factory(
        terminology.CancerTreatmentResponseObservationMethod
    )
    assessed_entities = factory.post_generation(
        add_m2m_related(
            "assessed_entities", PrimaryNeoplasticEntityFactory, min=1, max=1
        )
    )
    assessed_bodysites = factory.post_generation(
        make_m2m_terminology_factory(
            "assessed_bodysites", terminology.ObservationBodySite, min=1, max=1
        )
    )


def _generate_random_refseq(prefix="NG"):
    return f"{prefix}000{random.randint(100,999)}.{random.randint(1,9)}"


def _random_nucbase():
    return ["C", "G", "T", "A"][random.randint(0, 3)]


def _random_aminoacid():
    return ["Ala", "Cys", "Gly", "Thr", "Tyr", "His", "Gln", "Asn", "Leu", "Met"][
        random.randint(0, 9)
    ]


def _random_code_mutation():
    return [
        f"{random.randint(10,1000)}{_random_nucbase()}>{_random_nucbase()}",
        f"{random.randint(10,1000)}del",
        f"{random.randint(10,400)}_{random.randint(401,1000)}ins{_random_nucbase()}{_random_nucbase()}",
        f"{random.randint(10,1000)}dup",
    ][random.randint(0, 3)]


def _random_aminoacid_mutation():
    return [
        f"{_random_aminoacid()}{random.randint(10,1000)}{_random_aminoacid()}",
        f"{_random_aminoacid()}{random.randint(10,1000)}del",
        f"{_random_aminoacid()}{random.randint(10,400)}_{_random_aminoacid()}{random.randint(401,1000)}ins{_random_aminoacid()}{_random_aminoacid()}",
        f"{_random_aminoacid()}{random.randint(10,1000)}dup",
    ][random.randint(0, 3)]


class GenomicVariantFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.GenomicVariant

    case = factory.SubFactory(PatientCaseFactory)
    date = factory.LazyFunction(faker.date)
    gene_panel = factory.LazyFunction(faker.company)
    assessment = FuzzyChoice(models.GenomicVariant.GenomicVariantAssessment)
    confidence = FuzzyChoice(models.GenomicVariant.GenomicVariantConfidence)
    clinical_relevance = FuzzyChoice(
        models.GenomicVariant.GenomicVariantClinicalRelevance
    )
    analysis_method = make_terminology_factory(
        terminology.StructuralVariantAnalysisMethod
    )
    dna_hgvs = factory.LazyFunction(
        lambda: f'{_generate_random_refseq(prefix="NM_")}:c.{_random_code_mutation()}'
    )
    protein_hgvs = factory.LazyFunction(
        lambda: f'{_generate_random_refseq(prefix="NP_")}:p.{_random_aminoacid_mutation()}'
    )
    molecular_consequence = make_terminology_factory(terminology.MolecularConsequence)
    copy_number = factory.LazyFunction(lambda: random.randint(1, 9))
    allele_frequency = factory.LazyFunction(lambda: random.randint(0, 100) / 100)
    allele_depth = factory.LazyFunction(lambda: random.randint(0, 99999))
    zygosity = make_terminology_factory(terminology.Zygosity)
    genes = factory.post_generation(
        make_m2m_terminology_factory("genes", terminology.Gene, min=1, max=2)
    )


class PerformanceStatusFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.PerformanceStatus

    case = factory.SubFactory(PatientCaseFactory)
    date = factory.LazyFunction(faker.date)
    ecog_score = factory.LazyFunction(lambda: random.randint(0, 5))
    karnofsky_score = factory.LazyFunction(lambda: random.randint(0, 100))


class LifestyleFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Lifestyle

    case = factory.SubFactory(PatientCaseFactory)
    date = factory.LazyFunction(faker.date)
    smoking_status = make_terminology_factory(terminology.SmokingStatus)
    smoking_packyears = factory.LazyFunction(lambda: random.random())
    smoking_quited = factory.LazyFunction(lambda: measures.Time(year=random.random()))
    alcohol_consumption = make_terminology_factory(
        terminology.AlcoholConsumptionFrequency
    )
    night_sleep = factory.LazyFunction(lambda: measures.Time(hour=random.random()))
    exposures = factory.post_generation(
        make_m2m_terminology_factory(
            "exposures", terminology.ExposureAgent, min=0, max=3
        )
    )
    recreational_drugs = factory.post_generation(
        make_m2m_terminology_factory(
            "recreational_drugs", terminology.RecreationalDrug, min=0, max=2
        )
    )


class FamilyHistoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.FamilyHistory

    case = factory.SubFactory(PatientCaseFactory)
    date = factory.LazyFunction(faker.date)
    relationship = make_terminology_factory(terminology.FamilyMemberType)
    had_cancer = factory.LazyFunction(lambda: random.randint(0, 10) > 5)
    contributed_to_death = factory.LazyFunction(lambda: random.randint(0, 10) > 5)
    onset_age = factory.LazyFunction(lambda: random.randint(25, 95))
    topography = make_terminology_factory(terminology.CancerTopography)
    morphology = make_terminology_factory(terminology.CancerMorphology)


class TumorMutationalBurdenFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.TumorMutationalBurden

    case = factory.SubFactory(PatientCaseFactory)
    date = factory.LazyFunction(faker.date)
    value = factory.LazyFunction(lambda: random.randint(25, 95) / 5)
    status = FuzzyChoice(models.TumorMutationalBurden.TumorMutationalBurdenStatus)


class LossOfHeterozygosityFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.LossOfHeterozygosity

    case = factory.SubFactory(PatientCaseFactory)
    date = factory.LazyFunction(faker.date)
    value = factory.LazyFunction(lambda: float(random.randint(0, 100)))


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
    value = factory.LazyFunction(lambda: random.randint(0, 100) * 1.0)
    interpretation = FuzzyChoice(
        models.HomologousRecombinationDeficiency.HomologousRecombinationDeficiencyPresence
    )


class TumorNeoantigenBurdenFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.TumorNeoantigenBurden

    case = factory.SubFactory(PatientCaseFactory)
    date = factory.LazyFunction(faker.date)
    value = factory.LazyFunction(lambda: random.randint(0, 50) / 6)


class AneuploidScoreFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.AneuploidScore

    case = factory.SubFactory(PatientCaseFactory)
    date = factory.LazyFunction(faker.date)
    value = factory.LazyFunction(lambda: random.randint(0, 36))


class TumorBoardFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.UnspecifiedTumorBoard

    case = factory.SubFactory(PatientCaseFactory)
    date = factory.LazyFunction(faker.date)
    recommendations = factory.post_generation(
        make_m2m_terminology_factory(
            "recommendations", terminology.TumorBoardRecommendation, min=1, max=3
        )
    )
    related_entities = factory.post_generation(
        add_m2m_related(
            "related_entities", PrimaryNeoplasticEntityFactory, min=1, max=1
        )
    )


class MolecularTumorBoardFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.MolecularTumorBoard

    case = factory.SubFactory(PatientCaseFactory)
    date = factory.LazyFunction(faker.date)
    conducted_molecular_comparison = factory.LazyFunction(
        lambda: random.randint(0, 2) > 1
    )
    conducted_cup_characterization = factory.LazyFunction(
        lambda: random.randint(0, 2) > 1
    )
    characterized_cup = factory.LazyFunction(lambda: random.randint(0, 2) > 1)
    related_entities = factory.post_generation(
        add_m2m_related(
            "related_entities", PrimaryNeoplasticEntityFactory, min=1, max=1
        )
    )


class MolecularTherapeuticRecommendationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.MolecularTherapeuticRecommendation

    molecular_tumor_board = factory.SubFactory(MolecularTumorBoardFactory)
    expected_effect = make_terminology_factory(terminology.ExpectedDrugAction)
    off_label_use = factory.LazyFunction(lambda: random.randint(0, 2) > 1)
    within_soc = factory.LazyFunction(lambda: random.randint(0, 2) > 1)
    clinical_trial = factory.LazyFunction(
        lambda: f"NCT{random.randint(11111111,99999999)}"
    )
    drugs = factory.post_generation(
        make_m2m_terminology_factory(
            "drugs", terminology.AntineoplasticAgent, min=1, max=2
        )
    )
    supporting_genomic_variants = factory.post_generation(
        add_m2m_related(
            "supporting_genomic_variants",
            GenomicVariantFactory,
            min=0,
            max=3,
            get_related_case=lambda self: self.molecular_tumor_board.case,
        )
    )
    supporting_tumor_markers = factory.post_generation(
        add_m2m_related(
            "supporting_tumor_markers",
            TumorMarkerTestFactory,
            min=0,
            max=2,
            get_related_case=lambda self: self.molecular_tumor_board.case,
        )
    )
    supporting_genomic_signatures = factory.post_generation(
        add_m2m_related(
            "supporting_genomic_signatures",
            TumorMutationalBurdenFactory,
            min=0,
            max=1,
            get_related_case=lambda self: self.molecular_tumor_board.case,
        )
    )


class ComorbiditiesAssessmentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.ComorbiditiesAssessment

    case = factory.SubFactory(PatientCaseFactory)
    date = factory.LazyFunction(faker.date)
    index_condition = factory.SubFactory(PrimaryNeoplasticEntityFactory)
    panel = FuzzyChoice(ComorbiditiesPanel)
    absent_conditions = factory.post_generation(
        make_m2m_terminology_factory(
            "absent_conditions", terminology.ICD10Condition, min=0, max=4
        )
    )
    present_conditions = factory.post_generation(
        make_m2m_terminology_factory(
            "present_conditions", terminology.ICD10Condition, min=0, max=4
        )
    )


class VitalsFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Vitals

    case = factory.SubFactory(PatientCaseFactory)
    date = factory.LazyFunction(faker.date)
    height = factory.LazyFunction(
        lambda: measures.Distance(m=random.randint(150, 190) / 100)
    )
    weight = factory.LazyFunction(lambda: measures.Mass(kg=random.randint(55, 95)))
    blood_pressure_systolic = factory.LazyFunction(
        lambda: measures.Pressure(mmHg=random.randint(100, 120))
    )
    blood_pressure_diastolic = factory.LazyFunction(
        lambda: measures.Pressure(mmHg=random.randint(65, 85))
    )
    temperature = factory.LazyFunction(
        lambda: measures.Temperature(celsius=random.randint(37, 40))
    )


class ProjectFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = projects_models.Project

    title = factory.LazyFunction(
        lambda: f"Project #{random.randint(1111,9999)} - {faker.company()}"
    )
    summary = factory.LazyFunction(lambda: faker.text())
    leader = factory.SubFactory(UserFactory, access_level=2)
    members = factory.post_generation(
        add_m2m_related("members", UserFactory, min=2, max=5, get_related_case=None)
    )
    status = FuzzyChoice(projects_models.Project.ProjectStatus)
    clinical_centers = factory.LazyFunction(
        lambda: [faker.company() + " Hospital" for _ in range(1, random.randint(1, 3))]
    )
    ethics_approval_number = factory.LazyFunction(
        lambda: f"Req-{random.randint(1111,9999)}-{random.randint(1111,9999)}"
    )


class CohortFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = cohorts_models.Cohort

    name = factory.LazyFunction(lambda: f"Cohort #{random.randint(1111,9999)}")
    project = factory.SubFactory(ProjectFactory)


class DatasetFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = cohorts_models.Dataset

    name = factory.LazyFunction(lambda: f"Dataset #{random.randint(1111,9999)}")
    project = factory.SubFactory(ProjectFactory)


class ProjectDataManagerGrantFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = projects_models.ProjectDataManagerGrant

    project = factory.SubFactory(ProjectFactory)
    member = factory.SubFactory(UserFactory)
    validity_period = factory.LazyFunction(
        lambda: PostgresRange(
            datetime.now().date(), datetime.now().date() + timedelta(days=30)
        )
    )


def fake_complete_case():
    if User.objects.count() < 20:
        user = UserFactory.create()
    else:
        user = User.objects.all()[random.randint(0, User.objects.count() - 1)]
    with pghistory.context(username=user.username):
        case = PatientCaseFactory.create()
        if case.date_of_death:
            case.date_of_death = faker.date_between(
                case.date_of_birth + timedelta(days=35 * 365),
                case.date_of_birth + timedelta(days=99 * 365),
            )
        case.save()
        event = case.events.get(pgh_label="create")
        event.pgh_created_at = faker.date_between(
            datetime(2020, 1, 1).date(), datetime.now().date()
        )
        event.save()

        basic = dict(case=case)
        # Add neoplastic entities and staging
        initial_diagnosis_date = faker.date_between(
            case.date_of_birth + timedelta(days=25 * 365),
            (case.date_of_death or datetime.now().date()) - timedelta(days=2 * 365),
        )
        primary = PrimaryNeoplasticEntityFactory.create(
            **basic, assertion_date=initial_diagnosis_date
        )
        conditions = [primary]
        if random.randint(0, 100) > 40:
            # Add metastases with 60% probability
            conditions.append(
                MetastaticNeoplasticEntityFactory.create(
                    case=case,
                    related_primary=primary,
                    assertion_date=faker.date_between(
                        initial_diagnosis_date,
                        initial_diagnosis_date + timedelta(days=random.randint(0, 365)),
                    ),
                )
            )
        # Add TNM staging
        TNMStagingFactory.create(
            **basic, staged_entities=conditions, date=initial_diagnosis_date
        )
        # Add therapies
        for _ in range(random.randint(1, 5)):
            # Generate a random therapy period within 35 months of the initial diagnosis
            therapy_start = initial_diagnosis_date + timedelta(
                days=31 * random.randint(0, 35)
            )
            therapy_end = therapy_start + timedelta(days=31 * random.randint(1, 35))
            # Add systemic therapy
            systemic_therapy = SystemicTherapyFactory.create(
                **basic,
                therapy_line=None,
                targeted_entities=conditions,
                period=(therapy_start, therapy_end),
            )
            for _ in range(random.randint(1, 3)):
                SystemicTherapyMedicationFactory.create(
                    systemic_therapy=systemic_therapy,
                )

            # For palliative therapy, add radiotherapy with 60% probability
            if systemic_therapy.intent == "palliative" and random.randint(0, 100) > 40:
                radiotherapy = RadiotherapyFactory.create(
                    **basic,
                    therapy_line=None,
                    targeted_entities=conditions,
                    period=(therapy_start, therapy_end),
                )
                for _ in range(random.randint(1, 3)):
                    RadiotherapyDosageFactory.create(
                        radiotherapy=radiotherapy,
                    )

            # For curative therapy, add surgery with 50% probability
            if systemic_therapy.intent == "curative" and random.randint(0, 100) > 50:
                SurgeryFactory.create(
                    **basic,
                    therapy_line=None,
                    targeted_entities=conditions,
                    date=faker.date_between(therapy_start, therapy_end),
                )

            # Add treatment responses
            for _ in range(random.randint(0, 2)):
                TreatmentResponseFactory.create(
                    **basic,
                    assessed_entities=conditions,
                    date=faker.date_between(therapy_start, therapy_end),
                )

            # Add adverse event for systemic therapy
            for _ in range(random.randint(0, 1)):
                adverse_event = AdverseEventFactory.create(
                    **basic, date=faker.date_between(therapy_start, therapy_end)
                )
                AdverseEventSuspectedCauseFactory.create(
                    adverse_event=adverse_event,
                    systemic_therapy=systemic_therapy,
                    radiotherapy=None,
                )
                for _ in range(random.randint(0, 2)):
                    AdverseEventMitigationFactory.create(
                        adverse_event=adverse_event,
                    )

        # Add observations and lab results
        during_cancer_treatment = lambda: faker.date_between(
            initial_diagnosis_date, case.date_of_death or datetime.now().date()
        )
        for _ in range(random.randint(1, 4)):
            TumorMarkerTestFactory.create(
                **basic, related_entities=conditions, date=during_cancer_treatment()
            )
        genomics_date = during_cancer_treatment()
        for _ in range(random.randint(1, 12)):
            GenomicVariantFactory.create(
                **basic,
                date=genomics_date,
                gene_panel=random.choice(
                    ("FoundationOneCDx", "FoundationOneLiquid", "MelArray", "Oncomine")
                ),
            )
        for _ in range(random.randint(1, 2)):
            TumorMutationalBurdenFactory.create(**basic, date=during_cancer_treatment())
        for _ in range(random.randint(1, 2)):
            LossOfHeterozygosityFactory.create(**basic, date=during_cancer_treatment())
        FamilyHistoryFactory.create(**basic, date=during_cancer_treatment())
        RiskAssessmentFactory.create(
            **basic, assessed_entities=conditions, date=during_cancer_treatment()
        )
        LifestyleFactory.create(**basic)
        ComorbiditiesAssessmentFactory.create(
            **basic, index_condition=primary, date=during_cancer_treatment()
        )
        for _ in range(random.randint(1, 4)):
            VitalsFactory.create(**basic)
        MolecularTumorBoardFactory.create(
            **basic, related_entities=conditions, date=during_cancer_treatment()
        )
        for _ in range(random.randint(2, 5)):
            PerformanceStatusFactory.create(**basic, date=during_cancer_treatment())

        models.TherapyLine.assign_therapy_lines(case)
        for category in list(
            models.PatientCaseDataCompletion.PatientCaseDataCategories
        ):
            if random.randint(0, 100) > 45:
                completion = PatientCaseDataCompletionFactory.create(
                    **basic, category=category.value
                )
                event = completion.events.get(pgh_label="create")
                event.pgh_created_at = faker.date_between(
                    datetime(2020, 1, 1).date(), datetime.now().date()
                )
                event.save()
    return case
