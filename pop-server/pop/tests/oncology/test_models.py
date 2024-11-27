from datetime import datetime, date, timedelta

from django.test import TestCase
from django.db.utils import IntegrityError

from pop.oncology.models import CancerPatient
from pop.tests.factories import CancerPatientFactory

class CancerPatientModelTest(TestCase):
    def setUp(self):
        self.patient = CancerPatientFactory()
    
    def test_pseudoidentifier_created_on_save(self):
        self.assertIsNotNone(self.patient.pseudoidentifier) 
        self.assertRegex(self.patient.pseudoidentifier, r'^[A-Z]\.[0-9]{4}\.[0-9]{3}\.[0-9]{2}$')
    
    def test_pseudoidentifier_must_be_unique(self):
        patient2 = CancerPatientFactory()
        patient2.pseudoidentifier = self.patient.pseudoidentifier
        self.assertRaises(IntegrityError, patient2.save)

    def test_is_deceased_assigned_based_on_date_of_death(self):
        self.assertEqual(self.patient.is_deceased, self.patient.date_of_death is not None)

    def test_age_calculated_based_on_birthdate_and_today(self):
        self.patient.date_of_death = None 
        self.patient.save()
        delta = date.today() - self.patient.birthdate
        self.assertLess(self.patient.age - delta.days/365, 1)

    def test_age_calculated_based_on_birthdate_and_date_of_death(self):
        self.patient.date_of_death = date.today() - timedelta(days=5*365)
        self.patient.save()
        delta = self.patient.date_of_death - self.patient.birthdate
        self.assertLess(self.patient.age - delta.days/365, 1)
