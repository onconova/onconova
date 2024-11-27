import factory
import faker
import random 

from django.contrib.auth.models import Group, User
from django.contrib.auth.hashers import make_password

import pop.oncology.models as models
import pop.terminology.models as terminology

faker = faker.Faker()

def make_terminology_factory(terminology):
    return factory.make_factory(terminology,
        code = factory.Sequence(lambda n: f"{terminology.__name__.lower()}-code-{n+1}"),
        display = factory.Sequence(lambda n: f"{terminology.__name__} Concept {n+1}"),
        system = f'http://test.org/codesystem/{terminology.__name__.lower()}',
        FACTORY_CLASS=factory.django.DjangoModelFactory,
    )

class GroupFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Group

    name = factory.Sequence(lambda n: "Group #%s" % n)

class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: 'user%d' % n)
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


