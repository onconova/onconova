import factory
import faker
import random 

from django.contrib.auth.models import Group, User
from django.contrib.auth.hashers import make_password

import pop.core.measures as measures
import pop.oncology.models as models
import pop.terminology.models as terminology


faker = faker.Faker()

class TerminologyFactory(factory.django.DjangoModelFactory):
       class Meta:
        django_get_or_create = ('code','system')

def make_terminology_factory(terminology, code_iterator=None):
    if not code_iterator:
        code_iterator = [f"{terminology.__name__.lower()}-code-{n+1}" for n in range(4)]
    display_iterator = [code.replace('-code',' ').replace('-',' ').capitalize() for code in code_iterator]
    return factory.make_factory(terminology,
        code = factory.Iterator(code_iterator),
        display = factory.Iterator(display_iterator),
        system = f'http://test.org/codesystem/{terminology.__name__.lower()}',
        FACTORY_CLASS=TerminologyFactory,
    )

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
    date_of_birth = factory.LazyFunction(lambda: faker.date_of_birth(minimum_age=25, maximum_age=100))
    gender = factory.SubFactory(make_terminology_factory(terminology.AdministrativeGender))
    race = factory.SubFactory(make_terminology_factory(terminology.RaceCategory))
    sex_at_birth = factory.SubFactory(make_terminology_factory(terminology.BirthSex))
    date_of_death = factory.LazyFunction(lambda: faker.date_this_decade() if random.random() > 0.5 else None)
    cause_of_death = factory.SubFactory(make_terminology_factory(terminology.CauseOfDeath))
    created_by =  factory.SubFactory(UserFactory)



class PrimaryNeoplasticEntityFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.NeoplasticEntity
    relationship = 'primary'
    case = factory.SubFactory(PatientCaseFactory)
    assertion_date = factory.LazyFunction(lambda: faker.date())
    topography = factory.SubFactory(make_terminology_factory(terminology.CancerTopography))
    morphology = factory.SubFactory(make_terminology_factory(terminology.CancerMorphology))
    differentitation = factory.LazyFunction(lambda: make_terminology_factory(terminology.HistologyDifferentiation)() if random.random() > 0.75 else None)
    laterality = factory.LazyFunction(lambda: make_terminology_factory(terminology.LateralityQualifier)() if random.random() > 0.75 else None)
    created_by =  factory.SubFactory(UserFactory)


class MetastaticNeoplasticEntityFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.NeoplasticEntity
    relationship = 'metastatic'
    case = factory.SubFactory(PatientCaseFactory)
    assertion_date = factory.LazyFunction(lambda: faker.date())
    related_primary = factory.SubFactory(PrimaryNeoplasticEntityFactory)
    topography = factory.SubFactory(make_terminology_factory(terminology.CancerTopography))
    morphology = factory.SubFactory(make_terminology_factory(terminology.CancerMorphology))
    differentitation = factory.LazyFunction(lambda: make_terminology_factory(terminology.HistologyDifferentiation)() if random.random() > 0.75 else None)
    laterality = factory.LazyFunction(lambda: make_terminology_factory(terminology.LateralityQualifier)() if random.random() > 0.75 else None)
    created_by =  factory.SubFactory(UserFactory)


class TNMStagingFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.TNMStaging
    case = factory.SubFactory(PatientCaseFactory)
    date = factory.LazyFunction(faker.date)    
    stage = factory.SubFactory(make_terminology_factory(terminology.TNMStage, code_iterator=[f"tnm-stage-{n+1}-code" for n in range(5)]))
    methodology = factory.SubFactory(make_terminology_factory(terminology.TNMStagingMethod))
    created_by =  factory.SubFactory(UserFactory)

class FIGOStagingFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.FIGOStaging
    case = factory.SubFactory(PatientCaseFactory)
    date = factory.LazyFunction(faker.date)    
    stage = factory.SubFactory(make_terminology_factory(terminology.FIGOStage, code_iterator=[f"figo-stage-{n+1}-code" for n in range(5)]))
    methodology = factory.SubFactory(make_terminology_factory(terminology.FIGOStagingMethod))
    created_by =  factory.SubFactory(UserFactory)



class CA125TumorMarkerTestFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.TumorMarker
    analyte = 'CA125'
    case = factory.SubFactory(PatientCaseFactory)
    date = factory.LazyFunction(faker.date)    
    mass_concentration = factory.LazyFunction(lambda: measures.MassConcentration(g__l=random.random()))    
    created_by =  factory.SubFactory(UserFactory)



class LDHTumorMarkerTestFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.TumorMarker
    analyte = 'LDH'
    case = factory.SubFactory(PatientCaseFactory)
    date = factory.LazyFunction(faker.date)    
    arbitrary_concentration = factory.LazyFunction(lambda: measures.ArbitraryConcentration(IU__l=1000*random.random()))    
    created_by =  factory.SubFactory(UserFactory)
