
import unittest
from django.db import models
from django.test import TestCase, TransactionTestCase
from pop.core.models.fields import CodedConceptField
from pop.core.models.utils import FakeModel
from pop.terminology.models import AdministrativeGender as MockCodedConcept
from pop.core.schemas.fields import get_schema_field, CodedConcept
from pop.core.schemas.factory import create_schema
from parameterized import parameterized
from typing import List, Optional

class RelatedModel(FakeModel):
    auto_id = models.BigAutoField(primary_key=True)
    id = models.CharField(unique=True)
    char = models.CharField(null=True)
    
class MockModel(FakeModel):
    auto_id = models.BigAutoField(primary_key=True)
    id = models.CharField(unique=True)
    char = models.CharField(null=True)
    integer = models.IntegerField(null=True)
    foreign_key = models.ForeignKey(to=RelatedModel, on_delete=models.CASCADE, null=True)
    many_to_many = models.ManyToManyField(to=RelatedModel)
    coded_concept = CodedConceptField(terminology=MockCodedConcept, null=True)
    many_coded_concepts = CodedConceptField(terminology=MockCodedConcept, multiple=True)


@MockModel.fake_me
@RelatedModel.fake_me        
class TestGetSchemaField(TestCase):

    @parameterized.expand([
        ('char', str), 
        ('integer', int), 
        ('foreign_key', str),
        ('many_to_many', List[str]),
        ('coded_concept', CodedConcept), 
        ('many_coded_concepts', List[CodedConcept]), 
    ])
    def test_converting_model_field_to_schema_field(self, model_field_name, expected_type):
        model_field = MockModel._meta.get_field(model_field_name)
        schema_field = get_schema_field(model_field)
        self.assertEqual(schema_field[0], expected_type)


    def test_serialization(self):
        case,_ = CancerPatient.objects.get_or_create(
            id='POP-CancerPatient-123-456-789',
            birthdate='1995-01-01',
            gender=AdministrativeGender.objects.get_or_create(code='male',system='system', display='male')[0]
        )
        CancerPatientSchema = create_schema(CancerPatient)
        schema = CancerPatientSchema.model_validate(case)
        print(schema.model_dump_json(exclude_unset=True))
        self.assertFalse(True)
        
from django.test import TestCase
from ninja.testing import TestClient
from pop.core.models import CancerPatient
from pop.terminology.models import AdministrativeGender
from pop.core.api import api 

class TestAPI(TestCase):

    def test_get_cancer_patient_by_id(self):
        case,_ = CancerPatient.objects.get_or_create(
            birthdate='1995-01-01',
            gender=AdministrativeGender.objects.get_or_create(code='male',system='system', display='male')[0]
        )
        client = TestClient(api)
        response = client.get(f"/cancer-patients/{case.id}")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"msg": "Hello World"})