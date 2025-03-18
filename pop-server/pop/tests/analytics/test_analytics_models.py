from django.test import TestCase
from django.core.exceptions import FieldError
from django.db import models
from django.db.models import Avg, StdDev
from pop.analytics.models import Cohort  # replace with the actual app name
from pop.tests.factories import PatientCaseFactory
import numpy as np

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

    def test_average_and_standard_deviation_values(self):
        ages = [c.age for c in self.cohort.cases.all()]
        avg, iqr = self.cohort.get_cohort_trait_median('age')
        self.assertAlmostEqual(avg, np.percentile(ages, 50))
        self.assertAlmostEqual(iqr[0], np.percentile(ages, 25))
        self.assertAlmostEqual(iqr[1], np.percentile(ages, 75))

    def test_invalid_trait(self):
        with self.assertRaises(FieldError):
            self.cohort.get_cohort_trait_average('invalid_trait')