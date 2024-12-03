from datetime import datetime, date, timedelta

from django.test import TestCase
from django.db.utils import IntegrityError
import pop.oncology.models as oncology
import pop.terminology.models as terminology

import pop.tests.factories as factories

class PatientCaseModelTest(TestCase):
    
    def setUp(self):
        self.patient = factories.PatientCaseFactory()
    
    def test_pseudoidentifier_created_on_save(self):
        self.assertIsNotNone(self.patient.pseudoidentifier) 
        self.assertRegex(self.patient.pseudoidentifier, r'^[A-Z]\.[0-9]{4}\.[0-9]{3}\.[0-9]{2}$')
    
    def test_pseudoidentifier_must_be_unique(self):
        patient2 = factories.PatientCaseFactory()
        patient2.pseudoidentifier = self.patient.pseudoidentifier
        self.assertRaises(IntegrityError, patient2.save)

    def test_is_deceased_assigned_based_on_date_of_death(self):
        self.assertEqual(self.patient.is_deceased, self.patient.date_of_death is not None or self.patient.cause_of_death is not None)

    def test_age_calculated_based_on_date_of_birth_and_today(self):
        self.patient.date_of_death = None 
        self.patient.save()
        delta = date.today() - self.patient.date_of_birth
        self.assertLess(self.patient.age - delta.days/365, 1)

    def test_age_calculated_based_on_date_of_birth_and_date_of_death(self):
        self.patient.date_of_death = date.today() - timedelta(days=5*365)
        self.patient.save()
        delta = self.patient.date_of_death - self.patient.date_of_birth
        self.assertLess(self.patient.age - delta.days/365, 1)


class NeoplasticEntityModelTest(TestCase):
    
    def setUp(self):
        self.primary_neoplasm = factories.PrimaryNeoplasticEntityFactory()
        self.metastatic_neoplasm = factories.MetastaticNeoplasticEntityFactory()
    
    def test_primary_neoplasm_cannot_have_related_primary(self):
        self.primary_neoplasm.related_primary = factories.PrimaryNeoplasticEntityFactory()
        self.assertRaises(IntegrityError, self.primary_neoplasm.save)
        
    def test_metastatic_neoplasm_can_have_related_primary(self):
        self.metastatic_neoplasm.related_primary = factories.PrimaryNeoplasticEntityFactory()
        self.assertIsNone(self.metastatic_neoplasm.save())