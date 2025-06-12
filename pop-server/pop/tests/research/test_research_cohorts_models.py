from django.test import TestCase
from django.core.exceptions import FieldError
from pop.core.utils import average, std, percentile
from pop.research.models.cohort import Cohort  
from pop.tests.factories import PatientCaseFactory, UserFactory
from random import random, seed


class TestGetCohortPopulation(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.population = 4
        cls.cohort = Cohort.objects.create(name='Test Cohort')
        cls.cohort.cases.set([PatientCaseFactory.create() for _ in range(cls.population)])

    def test_no_cases(self):
        self.cohort.cases.set([])
        self.assertEqual(self.cohort.population, 0)

    def test_population(self):
        self.assertEqual(self.cohort.population, self.population)

class TestGetCohortTraitAverage(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.cohort = Cohort.objects.create(name='Test Cohort')
        cls.cohort.cases.set([PatientCaseFactory.create() for _ in range(4)])

    def test_no_cases(self):
        self.cohort.cases.set([])
        self.assertIsNone(self.cohort.get_cohort_trait_average('age'))

    def test_average_and_standard_deviation_values(self):
        ages = [c.age for c in self.cohort.cases.all()]
        avg, stddev = self.cohort.get_cohort_trait_average('age')
        self.assertAlmostEqual(avg, average(ages))
        self.assertAlmostEqual(stddev, std(ages))

    def test_invalid_trait(self):
        with self.assertRaises(FieldError):
            self.cohort.get_cohort_trait_average('invalid_trait')


class TestGetCohortTraitMedian(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.cohort = Cohort.objects.create(name='Test Cohort')
        cls.cohort.cases.set([PatientCaseFactory.create() for _ in range(10)])

    def test_no_cases(self):
        self.cohort.cases.set([])
        self.assertIsNone(self.cohort.get_cohort_trait_median('age'))

    def test_median_and_iqr_values(self):
        ages = [c.age for c in self.cohort.cases.all()]
        avg, iqr = self.cohort.get_cohort_trait_median('age')
        self.assertAlmostEqual(avg, percentile(ages, 50))
        self.assertAlmostEqual(iqr[0], percentile(ages, 25))
        self.assertAlmostEqual(iqr[1], percentile(ages, 75))

    def test_invalid_trait(self):
        with self.assertRaises(FieldError):
            self.cohort.get_cohort_trait_average('invalid_trait')

import unittest
from unittest.mock import MagicMock
from collections import OrderedDict
from collections import Counter

class TestGetCohortTraitCounts(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.cohort = Cohort.objects.create(name='Test Cohort')
        cls.user1 = UserFactory()
        cls.user2 = UserFactory()
        cls.cohort.cases.set([PatientCaseFactory.create(clinical_center='centerA' if not seed(n) and random() > 0.25 else 'centerB') for n in range(10)])
        

    def test_no_cases(self):
        self.cohort.cases.set([])
        result = self.cohort.get_cohort_trait_counts('clinical_center')
        self.assertIsNone(result)

    def test_trait_counts(self):
        counter = dict(Counter([c.clinical_center for c in self.cohort.cases.all()]))
        result = self.cohort.get_cohort_trait_counts('clinical_center')
        expected = dict(OrderedDict([
            ('centerA', (counter['centerA'], counter['centerA']/self.cohort.cases.count()*100)),
            ('centerB', (counter['centerB'], counter['centerB']/self.cohort.cases.count()*100))
        ]))
        self.assertEqual(result, expected)

    def test_invalid_trait(self):
        with self.assertRaises(FieldError):
            self.cohort.get_cohort_trait_average('invalid_trait')