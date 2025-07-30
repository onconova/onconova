from django.test import TestCase

from pop.terminology.models import AdministrativeGender as MockCodedConcept
from pop.tests.factories import make_terminology_factory


class TestDescendsFromLookup(TestCase):

    def setUp(self):
        factory = make_terminology_factory(MockCodedConcept).get_factory()  # type: ignore
        self.concept = factory()
        self.parent = factory()
        self.uncle = factory()
        self.grandparent = factory()
        self.concept.parent = self.parent
        self.concept.save()
        self.parent.parent = self.grandparent
        self.parent.save()
        self.uncle.parent = self.grandparent
        self.uncle.save()

    def test_descendsfrom_lookup_with_instance(self):
        query = MockCodedConcept.objects.filter(parent__descendsfrom=self.grandparent)
        self.assertEqual(query.count(), 3)
        self.assertTrue(self.concept in query)
        self.assertTrue(self.parent in query)
        self.assertTrue(self.uncle in query)
        self.assertTrue(self.grandparent not in query)

    def test_descendsfrom_lookup_with_pk(self):
        query = MockCodedConcept.objects.filter(parent__descendsfrom=self.parent.pk)
        self.assertEqual(query.count(), 1)
        self.assertTrue(self.concept in query)
        self.assertTrue(self.parent not in query)
        self.assertTrue(self.uncle not in query)
        self.assertTrue(self.grandparent not in query)
        self.assertTrue(self.grandparent not in query)
