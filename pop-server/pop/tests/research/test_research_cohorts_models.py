import unittest
from collections import Counter, OrderedDict
from datetime import datetime
from random import random, seed
from unittest.mock import MagicMock

from django.core.exceptions import FieldError
from django.test import TestCase
from pop.core.utils import average, percentile, std
from pop.research.models.cohort import Cohort
from pop.tests.factories import PatientCaseFactory, UserFactory


class TestGetCohortPopulation(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.population = 4
        cls.cohort = Cohort.objects.create(name="Test Cohort")
        cls.cohort.cases.set(
            [
                PatientCaseFactory.create(consent_status="valid")
                for _ in range(cls.population)
            ]
        )

    def test_no_cases(self):
        self.cohort.cases.set([])
        self.assertEqual(self.cohort.population, 0)

    def test_population(self):
        self.assertEqual(self.cohort.population, self.population)


class TestGetCohortTraitAverage(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.cohort = Cohort.objects.create(name="Test Cohort")
        cls.cohort.cases.set(
            [PatientCaseFactory.create(consent_status="valid") for _ in range(4)]
        )

    def test_no_cases(self):
        self.cohort.cases.set([])
        self.assertIsNone(
            self.cohort.get_cohort_trait_average(self.cohort.cases.all(), "age")
        )

    def test_average_and_standard_deviation_values(self):
        ages = [c.age for c in self.cohort.cases.all()]
        avg, stddev = self.cohort.get_cohort_trait_average(
            self.cohort.cases.all(), "age"
        )
        self.assertAlmostEqual(avg, average(ages))
        self.assertAlmostEqual(stddev, std(ages))

    def test_invalid_trait(self):
        with self.assertRaises(FieldError):
            self.cohort.get_cohort_trait_average(
                self.cohort.cases.all(), "invalid_trait"
            )


class TestGetCohortTraitMedian(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.cohort = Cohort.objects.create(name="Test Cohort")
        cls.cohort.cases.set(
            [
                PatientCaseFactory.create(
                    consent_status="valid",
                    vital_status='alive',
                    date_of_birth=datetime(2000 + i, 1, 1).date(),
                    date_of_death=None,
                )
                for i in range(10)
            ]
        )

    def test_no_cases(self):
        self.cohort.cases.set([])
        self.assertIsNone(
            self.cohort.get_cohort_trait_median(self.cohort.cases.all(), "age")
        )

    def test_median_and_iqr_values(self):
        ages = [c.age for c in self.cohort.cases.all()]
        median, iqr = self.cohort.get_cohort_trait_median(
            self.cohort.cases.all(), "age"
        )
        interp_diff = 0.5
        self.assertAlmostEqual(median, percentile(ages, 50) - interp_diff)
        self.assertAlmostEqual(iqr[0], percentile(ages, 25) - interp_diff)
        self.assertAlmostEqual(iqr[1], percentile(ages, 75) - interp_diff)

    def test_invalid_trait(self):
        with self.assertRaises(FieldError):
            self.cohort.get_cohort_trait_average(
                self.cohort.cases.all(), "invalid_trait"
            )


class TestGetCohortTraitCounts(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.cohort = Cohort.objects.create(name="Test Cohort")
        cls.user1 = UserFactory()
        cls.user2 = UserFactory()
        cls.cohort.cases.set(
            [
                PatientCaseFactory.create(
                    clinical_center=(
                        "centerA" if not seed(n) and random() > 0.25 else "centerB"
                    ),
                )
                for n in range(10)
            ]
        )

    def test_no_cases(self):
        self.cohort.cases.set([])
        result = self.cohort.get_cohort_trait_counts(
            self.cohort.cases.all(), "clinical_center"
        )
        self.assertEqual(result, OrderedDict())

    def test_trait_counts(self):
        counter = dict(Counter([c.clinical_center for c in self.cohort.cases.all()]))
        result = self.cohort.get_cohort_trait_counts(
            self.cohort.cases.all(), "clinical_center"
        )
        expected = dict(
            OrderedDict(
                [
                    (
                        "centerA",
                        (
                            counter["centerA"],
                            counter["centerA"] / self.cohort.cases.count() * 100,
                        ),
                    ),
                    (
                        "centerB",
                        (
                            counter["centerB"],
                            counter["centerB"] / self.cohort.cases.count() * 100,
                        ),
                    ),
                ]
            )
        )
        self.assertEqual(result, expected)

    def test_invalid_trait(self):
        with self.assertRaises(FieldError):
            self.cohort.get_cohort_trait_average(
                self.cohort.cases.all(), "invalid_trait"
            )
