from datetime import date, datetime, timedelta

from django.test import TestCase
from django.db.utils import IntegrityError
from psycopg.types.range import Range as PostgresRange
from pop.oncology.models.patient_case import PatientCaseDataCompletion
from pop.oncology.models.therapy_line import TherapyLine
import pop.tests.factories as factories
import pop.terminology.models as terminology
from parameterized import parameterized
import re 

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
    dynamic_test_name = lambda fcn,idx,param: f'{fcn.__name__}_#{idx}_' + re.split(r":", list(param)[0][0])[1]
    
    @classmethod
    def setUpTestData(cls):
        gene = terminology.Gene.objects.create(properties={
            'location': '12p34.5',
        }, code='gene-1', display='gene-1', system='system')
        terminology.GeneExon.objects.create(gene=gene, rank=1, coding_dna_region=(100,199), coding_genomic_region=(100000,199999))
        terminology.GeneExon.objects.create(gene=gene, rank=2, coding_dna_region=(200,299), coding_genomic_region=(200000,299999))
        cls.variant = factories.GenomicVariantFactory.create(dna_hgvs=None, rna_hgvs=None, protein_hgvs=None)
        cls.variant.genes.set([gene])
    
    def test_cytogenetic_location_annotated_from_single_gene(self):
        self.assertEqual(self.variant.cytogenetic_location, '12p34.5')
        
    def test_cytogenetic_location_annotated_from_multiple_genes(self):
        self.variant.genes.set([
            terminology.Gene.objects.create(properties={'location': '12p34.5'}, code='gene-2', display='gene-2', system='system'),
            terminology.Gene.objects.create(properties={'location': '12p56.7'}, code='gene-3', display='gene-3', system='system'),
        ])
        self.assertEqual(self.variant.cytogenetic_location, '12p34.5::12p56.7')

    def test_chromosomes_annotated_from_single_gene(self):
        self.assertEqual(self.variant.chromosomes, ['12'])
        
    def test_chromosomes_annotated_from_multiple_genes(self):
        self.variant.genes.set([
            terminology.Gene.objects.create(properties={'location': '12p34.5'}, code='gene-2', display='gene-2', system='system'),
            terminology.Gene.objects.create(properties={'location': '13p56.7'}, code='gene-3', display='gene-3', system='system'),
        ])
        self.assertEqual(self.variant.chromosomes, ['12','13'])

    @parameterized.expand(
        [
            # NCIB Sequences (genomic DNA coordinate)
           ('NM_12345:c.123C>A', 'NM_12345'),
           ('NR_12345.1:c.123C>A', 'NR_12345.1'),
           ('XM_12345.2:c.123C>A', 'XM_12345.2'),
           ('XR_12345.3:c.123C>A', 'XR_12345.3'),
           ('NC_12345:g.123456C>A', 'NC_12345'),
            # NCIB Sequences (coding DNA coordinate)
           ('NG_00001(NM_12345.0):c.123C>A', 'NM_12345.0'),
           ('NC_00001(NR_12345.0):c.123C>A', 'NR_12345.0'),
           ('NW_00001(XM_12345.0):c.123C>A', 'XM_12345.0'),
           ('AC_00001(XR_12345.0):c.123C>A', 'XR_12345.0'),
           # ENSEMBL Sequences (genomic DNA coordinate)
           ('ENSG12345:g.123456C>A', 'ENSG12345'),
           # ENSEMBL Sequences (coding DNA coordinate)
           ('ENST12345:c.123C>A', 'ENST12345'),
           ('ENST12345.0:c.123C>A', 'ENST12345.0'),
           # LRG Sequences (genomic DNA coordinate)
           ('LRG_123:g.123456C>A', 'LRG_123'),
           # LRG Sequences (coding DNA coordinate)
           ('LRG_123t4:c.123C>A', 'LRG_123t4'),
        ],
        name_func = dynamic_test_name
    )
    def test_dna_reference_sequence(self, hgvs, expected):
        self.variant.dna_hgvs = hgvs
        self.variant.save()
        self.assertEqual(self.variant.dna_reference_sequence, expected)
        
    @parameterized.expand(
        [
            # Examples from HGVS documentation (genomic DNA coordinate)
            ('NC_000001.11:g.1234=', 'unchanged'),
            ('NC_000001.11:g.1234_2345=', 'unchanged'),
            ('NC_000023.10:g.33038255C>A', 'substitution'),
            ('NC_000001.11:g.1234del', 'deletion'),
            ('NC_000001.11:g.1234_2345del', 'deletion'),
            ('NC_000001.11:g.1234dup', 'duplication'),
            ('NC_000001.11:g.1234_2345dup', 'duplication'),
            ('NC_000001.11:g.1234_1235insACGT', 'insertion'),
            ('NC_000001.11:g.1234_2345inv', 'inversion'),
            ('NC_000001.11:g.123delinsAC', 'deletion-insertion'),
            ('NC_000014.8:g.123CAG[23]', 'repetition'),
            ('NC_000011.10:g.1999904_1999946|gom', 'methylation-gain'),
            ('NC_000011.10:g.1999904_1999946|lom', 'methylation-loss'),
            ('NC_000011.10:g.1999904_1999946|met=', 'methylation-unchanged'),
            ('NC_000002.12:g.?_8247756delins[NC_000011.10:g.15825272_?]', 'translocation'),
            ('NC_000004.12:g.134850793_134850794ins[NC_000023.11:g.89555676_100352080] and NC_000023.11:g.89555676_100352080del', 'transposition'),
            # Examples from HGVS documentation (coding DNA coordinate)
            ('NM_004006.2:c.123=', 'unchanged'),
            ('NM_004006.2:c.56A>C', 'substitution'),
            ('NM_004006.2:c.5697del', 'deletion'),
            ('NC_000023.11(NM_004006.2):c.183_186+48del', 'deletion'),
            ('NM_004006.2:c.5697dup', 'duplication'),
            ('NM_004006.2:c.20_23dup ', 'duplication'),
            ('NM_004006.2:c.849_850ins858_895', 'insertion'),
            ('LRG_199t1:c.240_241insAGG', 'insertion'),
            ('NM_004006.2:c.5657_5660inv', 'inversion'),
            ('NM_004006.2:c.6775_6777delinsC', 'deletion-insertion'),
            ('LRG_199t1:c.850_901delinsTTCCTCGATGCCTG', 'deletion-insertion'),
            ('NM_000014.8:c.1342_1345[14]', 'repetition'),
            ('LRG_199t1:c.123_145|gom', 'methylation-gain'),
            ('LRG_199t1:c.123_145|lom', 'methylation-loss'),
            ('LRG_199t1:c.123_145|met=', 'methylation-unchanged'),
        ],
        name_func = dynamic_test_name
    )
    def test_dna_change_type(self, hgvs, expected):
        self.variant.dna_hgvs = hgvs
        self.variant.save()
        self.assertEqual(self.variant.dna_change_type, expected)
        
    @parameterized.expand(
        [
            # Sequences (genomic DNA coordinate)
           ('NC_12345:g.12345C>A', 12345),
           ('NC_12345:g.(12345_45678)C>A', 12345),
           ('NC_12345:g.(?_12345)C>A', 12345),
           ('NC_12345:g.(12345_?)C>A', 12345),
            # Sequences (coding DNA coordinate)
           ('NM_12345.0:c.123C>A', 123),
           ('NM_12345.0:c.(123_456)C>A', 123),
           ('NM_12345.0:c.(?_1234)C>A', 1234),
           ('NM_12345.0:c.(1234_?)C>A', 1234),
        ],
        name_func = dynamic_test_name
    )
    def test_dna_change_position(self, hgvs, expected):
        self.variant.dna_hgvs = hgvs
        self.variant.save()
        self.assertEqual(self.variant.dna_change_position, expected)
        
        
    @parameterized.expand(
        [
            # Sequences (genomic DNA coordinate)
           ('NC_12345:g.12345_45678del', 12345),
           ('NC_12345:g.(12345_?)_45678del', 12345),
           ('NC_12345:g.12345_(45678_?)del', 12345),
           ('NC_12345:g.(12345_?)_(45678_?)del', 12345),
            # Sequences (coding DNA coordinate)
           ('NM_12345.0:c.123_456del', 123),
           ('NM_12345.0:c.(123_124)_456del',123),
           ('NM_12345.0:c.(123_?)_456del',123),
           ('NM_12345.0:c.(?_123)_456del',123),
           ('NM_12345.0:c.123_(456_457)del', 123),
           ('NM_12345.0:c.123_(456_?)del', 123),
           ('NM_12345.0:c.123_(?_456)del', 123),
           ('NM_12345.0:c.(123_?)_(456_?)del', 123),
           ('NM_12345.0:c.(123_?)_(?_456)del', 123),
           ('NM_12345.0:c.(?_123)_(456_?)del', 123),
           ('NM_12345.0:c.(?_123)_(?_456)del', 123),
           ('NM_12345.0:c.123_?del', 123),
           ('NM_12345.0:c.?_456del', None),
           ('NM_12345.0:c.?_(456_?)del', None),
           ('NM_12345.0:c.(123_?)_?del', 123),
        ],
        name_func = dynamic_test_name
    )
    def test_dna_change_position_range_start(self, hgvs, expected):
        self.variant.dna_hgvs = hgvs
        self.variant.save()
        self.assertEqual(self.variant.dna_change_position_range_start, expected)

    @parameterized.expand(
        [
            # Sequences (genomic DNA coordinate)
           ('NC_12345:g.111111del', ['gene-1 exon 1']),
           ('NC_12345:g.(111111_?)_122222del', ['gene-1 exon 1']),
           ('NC_12345:g.222222_(222223_?)del', ['gene-1 exon 2']),
           ('NC_12345:g.(222222_?)_(222222_?)del', ['gene-1 exon 2']),
            # Sequences (coding DNA coordinate)
           ('NM_12345.0:c.105del', ['gene-1 exon 1']),
           ('NM_12345.0:c.105_106del', ['gene-1 exon 1']),
           ('NM_12345.0:c.(106_107)_456del',['gene-1 exon 1']),
           ('NM_12345.0:c.(108_?)_456del',['gene-1 exon 1']),
           ('NM_12345.0:c.(?_109)_456del',['gene-1 exon 1']),
           ('NM_12345.0:c.110_(111_112)del', ['gene-1 exon 1']),
           ('NM_12345.0:c.113_(114_?)del', ['gene-1 exon 1']),
           ('NM_12345.0:c.205_(?_208)del', ['gene-1 exon 2']),
           ('NM_12345.0:c.(201_?)_(209_?)del', ['gene-1 exon 2']),
           ('NM_12345.0:c.(200_?)_(?_206)del', ['gene-1 exon 2']),
           ('NM_12345.0:c.(?_123)_(156_?)del', ['gene-1 exon 1']),
           ('NM_12345.0:c.(?_101)_(?_201)del', ['gene-1 exon 1','gene-1 exon 2']),
           ('NM_12345.0:c.123_?del', ['gene-1 exon 1']),
           ('NM_12345.0:c.?_256del', ['gene-1 exon 2']),
           ('NM_12345.0:c.?_(202_?)del', ['gene-1 exon 2']),
           ('NM_12345.0:c.(123_?)_?del', ['gene-1 exon 1']),
        ],
        name_func = dynamic_test_name
    )
    def test_dna_change_exons(self, hgvs, expected):
        self.variant.dna_hgvs = hgvs
        self.variant.save()
        self.assertEqual(self.variant.exons, expected)
        
    @parameterized.expand(
        [
            # Sequences (genomic DNA coordinate)
           ('NC_12345:g.12345_45678del', 45678),
           ('NC_12345:g.(12345_?)_45678del', 45678),
           ('NC_12345:g.12345_(45678_?)del', 45678),
           ('NC_12345:g.(12345_?)_(45678_?)del', 45678),
            # Sequences (coding DNA coordinate)
           ('NM_12345.0:c.123_456del', 456),
           ('NM_12345.0:c.(123_124)_456del',456),
           ('NM_12345.0:c.(123_?)_456del',456),
           ('NM_12345.0:c.(?_123)_456del',456),
           ('NM_12345.0:c.123_(455_456)del', 456),
           ('NM_12345.0:c.123_(456_?)del', 456),
           ('NM_12345.0:c.123_(?_456)del', 456),
           ('NM_12345.0:c.(123_?)_(456_?)del', 456),
           ('NM_12345.0:c.(123_?)_(?_456)del', 456),
           ('NM_12345.0:c.(?_123)_(456_?)del', 456),
           ('NM_12345.0:c.(?_123)_(?_456)del', 456),
           ('NM_12345.0:c.123_?del', None),
           ('NM_12345.0:c.?_456del', 456),
           ('NM_12345.0:c.?_(456_?)del', 456),
           ('NM_12345.0:c.(123_?)_?del', None),
        ],
        name_func = dynamic_test_name
    )
    def test_dna_change_position_range_end(self, hgvs, expected):
        self.variant.dna_hgvs = hgvs
        self.variant.save()
        self.assertEqual(self.variant.dna_change_position_range_end, expected)
        
    @parameterized.expand(
        [
            # Sequences (genomic DNA coordinate)
           ('NC_12345:g.100C>A', 1),
           ('NC_12345:g.(100_200)C>A', 1),
           ('NC_12345:g.(?_200)C>A', 1),
           ('NC_12345:g.(100_?)C>A', 1),
           ('NC_12345:g.100_104del', 5),
           ('NC_12345:g.(100_?)_104del', 5),
           ('NC_12345:g.100_(104_?)del', 5),
           ('NC_12345:g.(100_?)_(104_?)del', 5),
           ('NC_12345:g.(100_101)_(103_104)del', 5),
            # Sequences (coding DNA coordinate)
           ('NM_12345:c.10C>A', 1),
           ('NM_12345:c.(10_11)C>A', 1),
           ('NM_12345:c.(?_11)C>A', 1),
           ('NM_12345:c.(10_?)C>A', 1),
           ('NM_12345:c.10_14del', 5),
           ('NM_12345:c.(10_?)_14del', 5),
           ('NM_12345:c.10_(14_?)del', 5),
           ('NM_12345:c.(10_?)_(14_?)del', 5),
           ('NM_12345:c.(10_11)_(13_14)del', 5),
        ],
        name_func = dynamic_test_name
    )
    def test_nucleotides_length_from_dna_hgvs(self, hgvs, expected):
        self.variant.dna_hgvs = hgvs
        self.variant.save()
        self.assertEqual(self.variant.nucleotides_length, expected)

    @parameterized.expand(
        [
            # NCIB Sequences
           ('NM_12345:r.123c>a', 'NM_12345'),
           ('NR_12345.1:r.123c>a', 'NR_12345.1'),
           ('XM_12345.2:r.123c>a', 'XM_12345.2'),
           ('XR_12345.3:r.123c>a', 'XR_12345.3'),
           # ENSEMBL Sequences
           ('ENST12345:r.123c>a', 'ENST12345'),
           ('ENST12345.0:r.123c>a', 'ENST12345.0'),
           # LRG Sequences
           ('LRG_123t4:r.123c>a', 'LRG_123t4'),
        ],
        name_func = dynamic_test_name
    )
    def test_rna_reference_sequence(self, hgvs, expected):
        self.variant.rna_hgvs = hgvs
        self.variant.save()
        self.assertEqual(self.variant.rna_reference_sequence, expected)
        
    @parameterized.expand(
        [
            # Examples from HGVS documentation 
            ('NM_004006.3:r.123=', 'unchanged'),
            ('NM_004006.3:r.123c>g', 'substitution'),
            ('NM_004006.3:r.123_127del', 'deletion'),
            ('NM_004006.3:r.123_124insauc', 'insertion'),
            ('NM_004006.3:r.123_127delinsag', 'deletion-insertion'),
            ('NM_004006.3:r.123_345dup', 'duplication'),
            ('NM_004006.3:r.123_345inv', 'inversion'),
            ('NM_004006.3:r.-110_-108[6]', 'repetition'),
        ],
        name_func = dynamic_test_name
    )
    def test_rna_change_type(self, hgvs, expected):
        self.variant.rna_hgvs = hgvs
        self.variant.save()
        self.assertEqual(self.variant.rna_change_type, expected)
        
    @parameterized.expand(
        [
           ('NM_12345.0:r.123c>a', '123'),
           ('NM_12345.0:r.(123_456)c>a', '(123_456)'),
           ('NM_12345.0:r.(?_1234)c>a', '(?_1234)'),
           ('NM_12345.0:r.(1234_?)c>a', '(1234_?)'),
           ('NM_12345.0:r.123_456del', '123_456'),
           ('NM_12345.0:r.(1234_?)_456del', '(1234_?)_456'),
           ('NM_12345.0:r.123_(4567_?)del', '123_(4567_?)'),
           ('NM_12345.0:r.(1234_?)_(1234_?)del', '(1234_?)_(1234_?)'),
        ],
        name_func = dynamic_test_name
    )
    def test_rna_change_position(self, hgvs, expected):
        self.variant.rna_hgvs = hgvs
        self.variant.save()
        self.assertEqual(self.variant.rna_change_position, expected)

    @parameterized.expand(
        [
            # NCIB Sequences
           ('NP_12345:p.Trp24del', 'NP_12345'),
           ('NP_12345.1:p.Trp24del', 'NP_12345.1'),
           ('AP_12345.2:p.Trp24del', 'AP_12345.2'),
           ('YP_12345.3:p.Trp24del', 'YP_12345.3'),
           ('XP_12345.4:p.Trp24del', 'XP_12345.4'),
           ('WP_12345.5:p.Trp24del', 'WP_12345.5'),
           # ENSEMBL Sequences
           ('ENSP12345:p.Trp24del', 'ENSP12345'),
           ('ENSP12345.0:p.Trp24del', 'ENSP12345.0'),
           # LRG Sequences
           ('LRG_123p4:p.Trp24del', 'LRG_123p4'),
        ],
        name_func = dynamic_test_name
    )
    def test_protein_reference_sequence(self, hgvs, expected):
        self.variant.protein_hgvs = hgvs
        self.variant.save()
        self.assertEqual(self.variant.protein_reference_sequence, expected)
        
    @parameterized.expand(
        [
            # Examples from HGVS documentation 
            # (https://hgvs-nomenclature.org/stable/recommendations/summary/)
           ('NP_003997.1:p.Cys188=', 'silent'),
           ('LRG_199p1:p.0', 'no-protein'),
           ('NP_003997.1:p.Trp24Cys', 'missense'),
           ('NP_003997.1:p.Trp24Ter', 'nonsense'),
           ('NP_003997.1:p.Tyr24*', 'nonsense'),
           ('NP_003997.1:p.(Trp24Cys)', 'missense'),
           ('NP_003997.2:p.Val7del', 'deletion'),
           ('NP_003997.2:p.Lys23_Val25del', 'deletion'),
           ('NP_004371.2:p.(Pro46_Asn47insSerSerTer)', 'insertion'),
           ('NP_004371.2:p.Asn47delinsSerSerTer', 'deletion-insertion'),
           ('NP_004371.2:p.(Asn47delinsSerSerTer)', 'deletion-insertion'),
           ('NP_004371.2:p.Glu125_Ala132delinsGlyLeuHisArgPheIleValLeu', 'deletion-insertion'),
           ('NP_003997.2:p.Met1ext-5', 'extension'),
           ('NP_003997.2:p.Ter110GlnextTer17', 'extension'),
           ('NP_0123456.1:p.Arg97ProfsTer23', 'frameshift'),
           ('NP_0123456.1:p.Arg97fs', 'frameshift'),
           ('NP_0123456.1:p.Ala2[10]', 'repetition'),
           ('NP_0123456.1:p.(Gln18)[(70_80)]', 'repetition'),
        ],
        name_func = dynamic_test_name
    )
    def test_protein_change_type(self, hgvs, expected):
        self.variant.protein_hgvs = hgvs
        self.variant.save()
        self.assertEqual(self.variant.protein_change_type, expected)
        