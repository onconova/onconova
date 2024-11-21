import factory
import faker

from django.contrib.auth.models import Group, User

import pop.core.models as models
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
    email = factory.LazyAttribute(lambda obj: '%s@example.com' % obj.username)

class CancerPatientFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.CancerPatient
    
    birthdate = factory.LazyFunction(faker.date_of_birth)
    gender = factory.SubFactory(make_terminology_factory(terminology.AdministrativeGender))
    race = factory.SubFactory(make_terminology_factory(terminology.RaceCategory))
    birthsex = factory.SubFactory(make_terminology_factory(terminology.BirthSex))
    is_deceased = factory.LazyFunction(faker.boolean)

