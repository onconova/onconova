from datetime import date, datetime, timedelta

from django.test import TestCase
from django.db.utils import IntegrityError
from psycopg.types.range import Range as PostgresRange
from pop.oncology.models.patient_case import PatientCaseDataCompletion
from pop.oncology.models.therapy_line import TherapyLine
import pop.tests.factories as factories
import pop.terminology.models as terminology
from parameterized import parameterized

class PatientCaseModelTest(TestCase):
    
    @classmethod
    def setUpTestData(cls):
        cls.patient = factories.PatientCaseFactory()
        cls.patient.save()
    
    def test_pseudoidentifier_created_on_save(self):
        self.assertIsNotNone(self.patient.pseudoidentifier) 
        self.assertRegex(self.patient.pseudoidentifier, r'^[A-Z]\.[0-9]{4}\.[0-9]{3}\.[0-9]{2}$')
    
    def test_pseudoidentifier_must_be_unique(self):
        patient2 = factories.PatientCaseFactory()
        patient2.pseudoidentifier = self.patient.pseudoidentifier
        self.assertRaises(IntegrityError, patient2.save)

    def test_clinical_center_and_identifier_must_be_unique(self):
        patient2 = factories.PatientCaseFactory()
        patient2.clinical_identifier = self.patient.clinical_identifier
        patient2.clinical_center = self.patient.clinical_center
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


    def test_age_at_diagnosis_based_on_first_diagnosis(self):
        diagnosis = factories.PrimaryNeoplasticEntityFactory(case=self.patient, assertion_date=datetime(2010,1,1).date())
        delta = diagnosis.assertion_date - self.patient.date_of_birth
        self.assertLess(self.patient.age_at_diagnosis - delta.days/365, 1)

    def test_age_at_diagnosis_is_null_without_diagnosis(self):
        self.assertIsNone(self.patient.age_at_diagnosis)

    def test_data_completion_rate_based_on_completed_categories(self):
        factories.PatientCaseDataCompletionFactory(case=self.patient)
        expected = self.patient.completed_data_categories.count() / PatientCaseDataCompletion.DATA_CATEGORIES_COUNT * 100
        self.assertTrue(self.patient.completed_data_categories.count()>0)
        self.assertAlmostEqual(self.patient.data_completion_rate, round(expected))

    def test_overall_survival_calculated_based_on_date_of_death(self):
        self.patient.date_of_death = datetime(2010, 1, 1).date()
        self.patient.save()
        factories.PrimaryNeoplasticEntityFactory.create(case=self.patient)
        delta = self.patient.date_of_death - self.patient.neoplastic_entities.first().assertion_date
        self.assertAlmostEqual(self.patient.overall_survival, round(delta.days/30.436875), delta=1)

    def test_overall_survival_calculated_based_on_current_time(self):
        self.patient.date_of_death = None 
        self.patient.save()
        factories.PrimaryNeoplasticEntityFactory.create(case=self.patient)
        delta = date.today() - self.patient.neoplastic_entities.first().assertion_date
        self.assertAlmostEqual(self.patient.overall_survival, round(delta.days/30.436875), delta=1)
        
    def test_overall_survival_is_null_if_no_diagnosis(self):
        self.assertIsNone(self.patient.overall_survival)

class NeoplasticEntityModelTest(TestCase):
    
    @classmethod
    def setUpTestData(cls):
        cls.primary_neoplasm = factories.PrimaryNeoplasticEntityFactory()
        cls.metastatic_neoplasm = factories.MetastaticNeoplasticEntityFactory()
    
    def test_primary_neoplasm_cannot_have_related_primary(self):
        self.primary_neoplasm.related_primary = factories.PrimaryNeoplasticEntityFactory()
        self.assertRaises(IntegrityError, self.primary_neoplasm.save)
        
    def test_metastatic_neoplasm_can_have_related_primary(self):
        self.metastatic_neoplasm.related_primary = factories.PrimaryNeoplasticEntityFactory()
        self.assertIsNone(self.metastatic_neoplasm.save())
        
class VitalsModelTest(TestCase):
    
    @classmethod
    def setUpTestData(cls):
        cls.vitals = factories.VitalsFactory()
    
    def test_body_mass_index_is_properly_generated(self):
        self.vitals.save()
        expected_bmi = self.vitals.weight.kg/(self.vitals.height.m*self.vitals.height.m)
        self.assertAlmostEqual(self.vitals.body_mass_index.kg__square_meter, expected_bmi)

class SystemicTherapyModelTest(TestCase):
    
    @classmethod
    def setUpTestData(cls):
        cls.therapy = factories.SystemicTherapyFactory()
    
    def test_therapy_duration_is_correctly_annotated(self):
        expected_duration = self.therapy.period.upper - self.therapy.period.lower 
        self.assertEqual(self.therapy.duration, expected_duration.days)
        
    def test_therapy_drugs_combination_is_correctly_annotated(self):
        self.med1 = factories.SystemicTherapyMedicationFactory.create(systemic_therapy=self.therapy)
        self.med2 = factories.SystemicTherapyMedicationFactory.create(systemic_therapy=self.therapy)        
        expected_combination = f'{self.med1.drug}/{self.med2.drug}'
        self.assertEqual(self.therapy.drug_combination, expected_combination)

class RadiotherapyModelTest(TestCase):
    
    @classmethod
    def setUpTestData(cls):
        cls.therapy = factories.RadiotherapyFactory()
    
    def test_radiotherapy_duration_is_correctly_annotated(self):
        expected_duration = self.therapy.period.upper - self.therapy.period.lower 
        self.assertEqual(self.therapy.duration, expected_duration.days)

class TherapyLineModelTest(TestCase):
    
    @classmethod
    def setUpTestData(cls):
        cls.TREATMENT_NOT_TOLERATED = terminology.TreatmentTerminationReason.objects.get_or_create(code='407563006', display='termination-reason', system='http://snomed.info/sct')[0]
        cls.COMPLEMENTARY_THERAPY = terminology.AdjunctiveTherapyRole.objects.get_or_create(code='314122007', display='category-1', system='https://snomed.info/sct')[0]
        cls.PROGRESSIVE_DISEASE = terminology.CancerTreatmentResponse.objects.get_or_create(code='LA28370-7', display='PD', system='https://loinc.org')[0]
        cls.chemotherapy1 = terminology.AntineoplasticAgent.objects.create(code='drug-1', display='chemo-1', therapy_category='chemotherapy')
        cls.chemotherapy2 = terminology.AntineoplasticAgent.objects.create(code='drug-2', display='chemo-2', therapy_category='chemotherapy')
        cls.immunotherapy1 = terminology.AntineoplasticAgent.objects.create(code='drug-3', display='imuno-1', therapy_category='chemotherapy')
        cls.case = factories.PatientCaseFactory.create()
        cls.therapy_line = factories.TherapyLineFactory.create(case=cls.case)
    
    def test_line_label_is_properly_generated(self):
        expected_label = f'{self.therapy_line.intent[0].upper()}LoT{self.therapy_line.ordinal}'
        self.assertEqual(self.therapy_line.label, expected_label)
    
    def test_line_progression_free_survival_is_properly_generated(self):
        self.systemic_therapy = factories.SystemicTherapyFactory.create(period=PostgresRange(date(2000,1,1), date(2000,2,2)), case=self.case, therapy_line=self.therapy_line)  
        self.treatment_response = factories.TreatmentResponseFactory.create(date=date(2000,5,5), case=self.case, recist=self.PROGRESSIVE_DISEASE)
        TherapyLine.assign_therapy_lines(self.case)
        therapy_line = self.case.therapy_lines.first()
        expected_survival = self.treatment_response.date - self.systemic_therapy.period.lower
        self.assertAlmostEqual(therapy_line.progression_free_survival, (expected_survival.days - 1)/30.436875, 1)
            
    def test_period_is_properly_generated_from_systemic_therapies(self):
        self.systemic_therapy = factories.SystemicTherapyFactory.create(period=('2000-1-1', '2000-2-2'), therapy_line=self.therapy_line)  
        self.assertEqual(self.therapy_line.period.lower, datetime(2000,1,1).date())
        self.assertEqual(self.therapy_line.period.upper, datetime(2000,2,3).date())
        
    def test_period_is_properly_generated_from_radiotherapies(self):
        self.radiotherapy = factories.RadiotherapyFactory.create(period=('2000-1-1', '2000-2-2'), therapy_line=self.therapy_line)  
        self.assertEqual(self.therapy_line.period.lower, datetime(2000,1,1).date())
        self.assertEqual(self.therapy_line.period.upper, datetime(2000,2,3).date())
        
    def test_period_is_properly_generated_from_surgery(self):
        self.surgery = factories.SurgeryFactory.create(date='2000-1-1', therapy_line=self.therapy_line)  
        self.assertFalse(self.therapy_line.period.isempty)
        self.assertEqual(self.therapy_line.period.lower, datetime(2000,1,1).date())
        self.assertEqual(self.therapy_line.period.upper, datetime(2000,1,2).date())
        
    def test_period_is_properly_generated_with_ongoing_therapy(self):
        self.systemic_therapy = factories.SystemicTherapyFactory.create(period=('2000-1-1', None), therapy_line=self.therapy_line)  
        self.assertEqual(self.therapy_line.period.lower, datetime(2000,1,1).date())
        self.assertEqual(self.therapy_line.period.upper, None)

    def test_period_is_properly_generated_from_multiple_therapies(self):
        self.systemic_therapy1 = factories.SystemicTherapyFactory.create(period=('2000-1-1', '2000-3-3'), therapy_line=self.therapy_line)  
        self.systemic_therapy2 = factories.SystemicTherapyFactory.create(period=('2000-2-2', '2000-4-4'), therapy_line=self.therapy_line)  

        self.assertEqual(self.therapy_line.period.lower, datetime(2000,1,1).date())
        self.assertEqual(self.therapy_line.period.upper, datetime(2000,4,5).date())
        
    def test_period_is_properly_generated_from_multiple_mixed_therapies(self):
        self.systemic_therapy1 = factories.SystemicTherapyFactory.create(period=('2000-1-1', '2000-3-3'), therapy_line=self.therapy_line)  
        self.systemic_therapy2 = factories.RadiotherapyFactory.create(period=('2000-2-2', '2000-4-4'), therapy_line=self.therapy_line)  

        self.assertEqual(self.therapy_line.period.lower, datetime(2000,1,1).date())
        self.assertEqual(self.therapy_line.period.upper, datetime(2000,4,5).date())


    def test_therapy_line_assignment__no_existing_lines(self):
        self.systemic_therapy = factories.SystemicTherapyFactory.create(
            case = self.case,
            intent = 'curative',
        )  
        TherapyLine.assign_therapy_lines(self.case)
        # Refresh data
        self.systemic_therapy.refresh_from_db()
        self.assertEqual(self.systemic_therapy.therapy_line.label, 'CLoT1')

    def test_therapy_line_assignment__add_to_existing_line(self):
        self.systemic_therapy1 = factories.SystemicTherapyFactory.create(
            case = self.case,
            intent = 'curative',
        )  
        self.systemic_therapy2 = factories.SystemicTherapyFactory.create(
            case = self.case,
            intent = 'curative',
        )  
        TherapyLine.assign_therapy_lines(self.case)
        
        self.systemic_therapy1.refresh_from_db()
        self.systemic_therapy2.refresh_from_db()

        self.assertEqual(self.systemic_therapy1.therapy_line.label, 'CLoT1')
        self.assertEqual(self.systemic_therapy2.therapy_line.label, 'CLoT1')

    def test_therapy_line_assignment__switch_curative_to_palliative(self):
        self.systemic_therapy1 = factories.SystemicTherapyFactory.create(
            case = self.case,
            intent = 'curative',
        )  
        self.systemic_therapy2 = factories.SystemicTherapyFactory.create(
            case = self.case,
            intent = 'palliative',
        )  
        TherapyLine.assign_therapy_lines(self.case)
        
        self.systemic_therapy1.refresh_from_db()
        self.systemic_therapy2.refresh_from_db()
        
        self.assertEqual(self.systemic_therapy1.therapy_line.label, 'CLoT1')
        self.assertEqual(self.systemic_therapy2.therapy_line.label, 'PLoT1')

    def test_therapy_line_assignment__same_line_for_overlapping_therapies(self):
        self.systemic_therapy1 = factories.SystemicTherapyFactory.create(
            case=self.case,
            intent='curative',
            period=('2023-1-1', '2023-3-1')
        )  
        self.systemic_therapy2 = factories.SystemicTherapyFactory.create(
            case=self.case,
            intent='curative',
            period=('2023-2-1', '2023-4-1')
        )  
        TherapyLine.assign_therapy_lines(self.case)
        
        self.systemic_therapy1.refresh_from_db()
        self.systemic_therapy2.refresh_from_db()
        
        self.assertEqual(self.systemic_therapy1.therapy_line.label, 'CLoT1')
        self.assertEqual(self.systemic_therapy2.therapy_line.label, 'CLoT1')
        self.assertEqual(self.systemic_therapy1.therapy_line, self.systemic_therapy2.therapy_line)


    def test_therapy_line_assignment__new_line_due_to_progressive_disease(self):
        self.systemic_therapy1 = factories.SystemicTherapyFactory.create(
            case=self.case,
            intent='palliative',
            period=('2023-1-1', '2023-3-1'),
        )  
        self.treatment_response = factories.TreatmentResponseFactory.create(
            case=self.case,
            recist=self.PROGRESSIVE_DISEASE,
            date='2023-2-15',
        )
        self.systemic_therapy2 = factories.SystemicTherapyFactory.create(
            case=self.case,
            intent='palliative',
            period=('2023-4-1', '2023-5-1'),
        )  
        TherapyLine.assign_therapy_lines(self.case)
        
        self.systemic_therapy1.refresh_from_db()
        self.systemic_therapy2.refresh_from_db()
        
        self.assertEqual(self.systemic_therapy1.therapy_line.label, 'PLoT1')
        self.assertEqual(self.systemic_therapy2.therapy_line.label, 'PLoT2')
        self.assertNotEqual(self.systemic_therapy1.therapy_line, self.systemic_therapy2.therapy_line)

    def test_therapy_line_assignment__same_line_due_to_same_treatment_type(self):
        self.systemic_therapy1 = factories.SystemicTherapyFactory.create(
            case=self.case,
            intent='palliative',
            period=('2023-1-1', '2023-3-1'),
        )  
        self.treatment_response = factories.TreatmentResponseFactory.create(
            case=self.case,
            date='2023-2-15',
        )
        self.systemic_therapy2 = factories.SystemicTherapyFactory.create(
            case=self.case,
            intent='palliative',
            period=('2023-4-1', '2023-5-1'),
        )  
        TherapyLine.assign_therapy_lines(self.case)
        
        self.systemic_therapy1.refresh_from_db()
        self.systemic_therapy2.refresh_from_db()
        
        self.assertEqual(self.systemic_therapy1.therapy_line.label, 'PLoT1')
        self.assertEqual(self.systemic_therapy2.therapy_line.label, 'PLoT1')
        self.assertEqual(self.systemic_therapy1.therapy_line, self.systemic_therapy2.therapy_line)

    def test_therapy_line_assignment__new_line_due_to_different_treatment_category(self):
        self.systemic_therapy1 = factories.SystemicTherapyFactory.create(
            case=self.case,
            intent='palliative',
            period=('2023-1-1', '2023-3-1'),
        )  
        factories.SystemicTherapyMedicationFactory.create(
            drug=self.chemotherapy1,
            systemic_therapy=self.systemic_therapy1
        )
        self.systemic_therapy2 = factories.SystemicTherapyFactory.create(
            case=self.case,
            intent='palliative',
            period=('2023-4-1', '2023-5-1'),
        )  
        factories.SystemicTherapyMedicationFactory.create(
            drug=self.immunotherapy1,
            systemic_therapy=self.systemic_therapy2
        )
        TherapyLine.assign_therapy_lines(self.case)
        
        self.systemic_therapy1.refresh_from_db()
        self.systemic_therapy2.refresh_from_db()
        
        self.assertEqual(self.systemic_therapy1.therapy_line.label, 'PLoT1')
        self.assertEqual(self.systemic_therapy2.therapy_line.label, 'PLoT2')
        self.assertNotEqual(self.systemic_therapy1.therapy_line, self.systemic_therapy2.therapy_line)

    def test_therapy_line_assignment__same_line_due_to_maintenance(self):
        self.systemic_therapy1 = factories.SystemicTherapyFactory.create(
            case=self.case,
            intent='palliative',
            period=('2023-1-1', '2023-3-1'),
            adjunctive_role=None,
        )  
        factories.SystemicTherapyMedicationFactory.create(
            drug=self.chemotherapy1,
            systemic_therapy=self.systemic_therapy1
        )
        self.systemic_therapy2 = factories.SystemicTherapyFactory.create(
            case=self.case,
            intent='palliative',
            period=('2023-4-1', '2023-5-1'),
            adjunctive_role=self.COMPLEMENTARY_THERAPY,
        )  
        self.systemic_therapy2.save()
        
        factories.SystemicTherapyMedicationFactory.create(
            drug=self.chemotherapy2,
            systemic_therapy=self.systemic_therapy2
        )
        TherapyLine.assign_therapy_lines(self.case)
        
        self.systemic_therapy1.refresh_from_db()
        self.systemic_therapy2.refresh_from_db()
        
        self.assertEqual(self.systemic_therapy1.therapy_line.label, 'PLoT1')
        self.assertEqual(self.systemic_therapy2.therapy_line.label, 'PLoT1')
        self.assertEqual(self.systemic_therapy1.therapy_line, self.systemic_therapy2.therapy_line)



class GenomicVariantModelTest(TestCase):
    
    @classmethod
    def setUpTestData(cls):
        cls.variant = factories.GenomicVariantFactory()
    
    def test_cytogenetic_location_annotated_from_single_gene(self):
        self.variant.genes.set([terminology.Gene.objects.create(properties={'location': '12p34.5'}, code='gene-1', display='gene-1', system='system')])
        self.assertEqual(self.variant.cytogenetic_location, '12p34.5')
        
    def test_cytogenetic_location_annotated_from_multiple_genes(self):
        self.variant.genes.set([
            terminology.Gene.objects.create(properties={'location': '12p34.5'}, code='gene-1', display='gene-1', system='system'),
            terminology.Gene.objects.create(properties={'location': '12p56.7'}, code='gene-2', display='gene-2', system='system'),
        ])
        self.assertEqual(self.variant.cytogenetic_location, '12p34.5::12p56.7')

    def test_chromosomes_annotated_from_single_gene(self):
        self.variant.genes.set([terminology.Gene.objects.create(properties={'location': '12p34.5'}, code='gene-1', display='gene-1', system='system')])
        self.assertEqual(self.variant.chromosomes, ['12'])
        
    def test_chromosomes_annotated_from_multiple_genes(self):
        self.variant.genes.set([
            terminology.Gene.objects.create(properties={'location': '12p34.5'}, code='gene-1', display='gene-1', system='system'),
            terminology.Gene.objects.create(properties={'location': '13p56.7'}, code='gene-2', display='gene-2', system='system'),
        ])
        self.assertEqual(self.variant.chromosomes, ['12','13'])

    @parameterized.expand(
        [
           ('NM12345.0:c.123C>A', 'NM12345.0'),
           ('NP12345:g.1234_2345del', 'NP12345'),
           ('ENST12345.0:g.1234_1235insACGT', 'ENST12345.0'),
           ('LRG12345.0:g.123delinsAC', 'LRG12345.0'),
        ],
        name_func = lambda fcn,idx,param: f'{fcn.__name__}_{idx}_{list(param)[0][-1]}'
    )
    def test_dna_reference_sequence(self, hgvs, expected):
        self.variant.coding_hgvs = hgvs
        self.variant.save()
        self.assertEqual(self.variant.dna_reference_sequence, expected)
        
    def test_dna_reference_sequence_unset(self):
        self.variant.coding_hgvs = None
        self.variant.save()
        self.assertEqual(self.variant.dna_reference_sequence, None)
    
    @parameterized.expand(
        [
           ('NM12345.0:c.123C>A', 'substitution'),
           ('NM12345.0:g.1234_2345del', 'deletion'),
           ('NM12345.0:g.1234_1235insACGT', 'insertion'),
           ('NM12345.0:g.123delinsAC', 'deletion-insertion'),
           ('NM12345.0:g.1234_2345dup', 'duplication'),
           ('NM12345.0:g.(?_1234)_2345inv', 'inversion'),
        ],
        name_func = lambda fcn,idx,param: f'{fcn.__name__}_{idx}_{list(param)[0][-1]}'
    )
    def test_dna_change_type(self, hgvs, expected):
        self.variant.coding_hgvs = hgvs
        self.variant.save()
        self.assertEqual(self.variant.dna_change_type, expected)
        