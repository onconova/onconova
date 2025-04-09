from django.test import TestCase
from django.core.exceptions import FieldError
from pop.analytics.models import Cohort  
from pop.tests.factories import PatientCaseFactory, UserFactory
import numpy as np
from random import random


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
        self.assertAlmostEqual(avg, np.average(ages))
        self.assertAlmostEqual(stddev, np.std(ages))

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
        self.assertAlmostEqual(avg, np.percentile(ages, 50))
        self.assertAlmostEqual(iqr[0], np.percentile(ages, 25))
        self.assertAlmostEqual(iqr[1], np.percentile(ages, 75))

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
        cls.cohort.cases.set([PatientCaseFactory.create(clinical_center='centerA' if random() > 0.25 else 'centerB') for _ in range(10)])

    def test_no_cases(self):
        self.cohort.cases.set([])
        result = self.cohort.get_cohort_trait_counts('clinical_center')
        self.assertIsNone(result)

    def test_trait_counts(self):
        counter = Counter([c.clinical_center for c in self.cohort.cases.all()])
        result = self.cohort.get_cohort_trait_counts('clinical_center')
        expected = OrderedDict([
            ('centerA', (counter['centerA'], counter['centerA']/self.cohort.cases.count()*100)),
            ('centerB', (counter['centerB'], counter['centerB']/self.cohort.cases.count()*100))

        ])
        self.assertEqual(result, expected)

    def test_invalid_trait(self):
        with self.assertRaises(FieldError):
            self.cohort.get_cohort_trait_average('invalid_trait')