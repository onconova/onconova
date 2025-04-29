import pghistory
import pghistory.models

from django.test import TestCase
from django.db.models import Model

from pop.oncology import models, schemas
from pop.tests import factories, common 
from pop.core.schemas import HistoryEvent
from pop.core.schemas.factory import ModelGetSchema, ModelCreateSchema
from copy import deepcopy
from parameterized import parameterized
import pytest 

class ApiControllerTextMixin(common.ApiControllerTestMixin):
    FACTORY: factories.factory.django.DjangoModelFactory
    MODEL: Model
    SCHEMA: ModelGetSchema
    CREATE_SCHEMA: ModelCreateSchema      
    history_tracked: bool = True 

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        # Ensure class settings are iterable
        cls.FACTORY = [cls.FACTORY] if not isinstance(cls.FACTORY, list) else cls.FACTORY
        cls.SUBTESTS = len(cls.FACTORY)
        cls.MODEL = [cls.MODEL]*cls.SUBTESTS if not isinstance(cls.MODEL, list) else cls.MODEL
        cls.SCHEMA = [cls.SCHEMA]*cls.SUBTESTS if not isinstance(cls.SCHEMA, list) else cls.SCHEMA
        cls.CREATE_SCHEMA = [cls.CREATE_SCHEMA]*cls.SUBTESTS if not isinstance(cls.CREATE_SCHEMA, list) else cls.CREATE_SCHEMA        
        cls.INSTANCE = []
        cls.CREATE_PAYLOAD = []
        cls.UPDATE_PAYLOAD = []
        for factory, schema in zip(cls.FACTORY, cls.CREATE_SCHEMA):
            with pghistory.context(username=cls.user.username):
                instance1, instance2  = factory.create_batch(2)
                cls.INSTANCE.append(instance1)
                cls.CREATE_PAYLOAD.append(schema.model_validate(instance1).model_dump(mode='json'))
                cls.UPDATE_PAYLOAD.append(schema.model_validate(instance2).model_dump(mode='json'))
                instance2.delete()
        
    def _remove_key_recursive(self, dictionary, keys_to_remove):
        """
        Recursively removes a key from a dictionary that contains lists.

        Args:
            dictionary (dict): The dictionary to remove the key from.
            key_to_remove (str): The key to remove.

        Returns:
            dict: The updated dictionary with the key removed.
        """
        def __remove_key_recursive(d, key_to_remove):
            for key, value in list(d.items()):
                if key == key_to_remove:
                    del d[key]
                elif isinstance(value, dict):
                    __remove_key_recursive(value, key_to_remove)
                elif isinstance(value, list):
                    for item in value:
                        if isinstance(item, dict):
                            __remove_key_recursive(item, key_to_remove)
            return d 
        for key_to_remove in keys_to_remove:
            dictionary = __remove_key_recursive(dictionary, key_to_remove)
        return dictionary

    @parameterized.expand(common.ApiControllerTestMixin.get_scenarios)
    def test_get_all(self, scenario, config):            
        for i in range(self.SUBTESTS):
            instance = self.INSTANCE[i]
            # Call the API endpoint
            response = self.call_api_endpoint('GET', self.get_route_url(instance), **config)
            with self.subTest(i=i):
                # Assert response content
                if scenario == 'HTTPS Authenticated':
                    self.assertEqual(response.status_code, 200)
                    if 'items' in response.json():
                        entry = next((item for item in response.json()['items'] if str(instance.id) == item['id']))
                    else:
                        entry = response.json()[0]
                    expected = self.SCHEMA[i].model_validate(instance).model_dump()
                    result = self.SCHEMA[i].model_validate(entry).model_dump()
                    if self.history_tracked:
                        expected['createdAt'] = expected['createdAt'].replace(microsecond=0)
                        result['createdAt'] = result['createdAt'].replace(microsecond=0)
                    self.assertEqual(expected, result)
                self.MODEL[i].objects.all().delete()

    @parameterized.expand(common.ApiControllerTestMixin.get_scenarios)
    def test_get_by_id(self, scenario, config):              
        for i in range(self.SUBTESTS):
            instance = self.INSTANCE[i]
            # Call the API endpoint
            response = self.call_api_endpoint('GET', self.get_route_url_with_id(instance), **config)
            with self.subTest(i=i):
                # Assert response content
                if scenario == 'HTTPS Authenticated':
                    self.assertEqual(response.status_code, 200)
                    expected = self.SCHEMA[i].model_validate(instance).model_dump()
                    result = self.SCHEMA[i].model_validate(response.json()).model_dump()
                    if self.history_tracked:
                        expected['createdAt'] = expected['createdAt'].replace(microsecond=0)
                        result['createdAt'] = result['createdAt'].replace(microsecond=0)
                    self.assertDictEqual(result, expected)
                self.MODEL[i].objects.all().delete()
    
    @parameterized.expand(common.ApiControllerTestMixin.scenarios)
    def test_delete(self, scenario, config):            
        for i in range(self.SUBTESTS):
            instance = self.INSTANCE[i]
            # Call the API endpoint
            response = self.call_api_endpoint('DELETE', self.get_route_url_with_id(instance), **config)
            with self.subTest(i=i):       
                # Assert response content
                if scenario == 'HTTPS Authenticated':
                    self.assertEqual(response.status_code, 204)
                    self.assertFalse(self.MODEL[i].objects.filter(id=instance.id).exists())
                    # Assert audit trail
                    if self.history_tracked:
                        self.assertTrue(pghistory.models.Events.objects.filter(pgh_obj_id=instance.id, pgh_label='delete').exists(), 'Event not properly registered')
                self.MODEL[i].objects.all().delete()

    @parameterized.expand(common.ApiControllerTestMixin.scenarios)
    def test_create(self, scenario, config):                  
        for i,(instance, payload, model) in enumerate(zip(self.INSTANCE, self.CREATE_PAYLOAD, self.MODEL)):
            instance.delete()
            # Call the API endpoint.
            response = self.call_api_endpoint('POST', self.get_route_url(instance), data=payload, **config)
            with self.subTest(i=i):       
                # Assert response content
                if scenario == 'HTTPS Authenticated':
                    created_id = response.json()['id']
                    created_instance = model.objects.filter(id=created_id).first()
                    self.assertIsNotNone(created_instance, 'Resource has not been created')
                    # Assert audit trail
                    if self.history_tracked:
                        self.assertEqual(self.user.username, created_instance.created_by, 'Unexpected creator user.')
                        self.assertTrue(created_instance.events.filter(pgh_label='create').exists(), 'Event not properly registered')
                model.objects.all().delete()

    @parameterized.expand(common.ApiControllerTestMixin.scenarios)
    def test_update(self, scenario, config):              
        for i in range(self.SUBTESTS):
            instance = self.INSTANCE[i]
            payload = self.UPDATE_PAYLOAD[i]
            with self.subTest(i=i):      
                # Call the API endpoint
                response = self.call_api_endpoint('PUT', self.get_route_url_with_id(instance), data=payload, **config)
                # Assert response content
                if scenario == 'HTTPS Authenticated':
                    updated_id = response.json()['id']
                    self.assertEqual(response.status_code, 200) 
                    updated_instance =self.MODEL[i].objects.filter(id=updated_id).first() 
                    self.assertIsNotNone(updated_instance, 'The updated instance does not exist') 
                    self.assertNotEqual(
                        [getattr(instance,field.name) for field in self.MODEL[i]._meta.concrete_fields],
                        [getattr(updated_instance,field.name) for field in self.MODEL[i]._meta.concrete_fields]
                    )
                    # Assert audit trail
                    if self.history_tracked:
                        if updated_instance.updated_by:
                            self.assertIn(self.user.username, updated_instance.updated_by, 'The updating user is not registered') 
                        self.assertTrue(pghistory.models.Events.objects.filter(pgh_obj_id=instance.id, pgh_label='update').exists(), 'Event not properly registered')
                self.MODEL[i].objects.all().delete() 
               

    @parameterized.expand(common.ApiControllerTestMixin.get_scenarios)
    def test_get_all_history_events(self, scenario, config):            
        for i in range(self.SUBTESTS):
            if not hasattr(self.MODEL[i],'pgh_event_model'):
                pytest.skip("Non-tracked model")
            instance = self.INSTANCE[i]
            # Call the API endpoint
            response = self.call_api_endpoint('GET', self.get_route_url_history(instance), **config)
            with self.subTest(i=i):
                # Assert response content
                if scenario == 'HTTPS Authenticated':
                    self.assertEqual(response.status_code, 200)
                    entry = next((item for item in response.json()['items']))
                    self.assertEqual(entry['category'], 'create')
                    self.assertEqual(entry['user'], self.user.username)
                    self.assertEqual(entry['snapshot']['id'], str(instance.id))                    
                self.MODEL[i].objects.all().delete()
    
    @parameterized.expand(common.ApiControllerTestMixin.get_scenarios)
    def test_get_history_events_by_id(self, scenario, config):            
        for i in range(self.SUBTESTS):
            if not hasattr(self.MODEL[i],'pgh_event_model'):
                pytest.skip("Non-tracked model")
            instance = self.INSTANCE[i]
            if hasattr(instance, 'parent_events'):
                event = instance.parent_events.first()
            else:
                event = instance.events.first() 
            # Call the API endpoint
            response = self.call_api_endpoint('GET', self.get_route_url_history_with_id(instance, event), **config)
            with self.subTest(i=i):
                # Assert response content
                if scenario == 'HTTPS Authenticated':
                    self.assertEqual(response.status_code, 200)
                    entry = response.json()
                    self.assertEqual(entry['id'], event.pgh_id)
                    self.assertEqual(entry['user'], event.pgh_context['username'])
                    self.assertEqual(entry['snapshot']['id'], str(instance.id))                    
                self.MODEL[i].objects.all().delete()

    @parameterized.expand(common.ApiControllerTestMixin.scenarios)
    def test_revert_changes(self, scenario, config):  
        for i in range(self.SUBTESTS):  
            if not hasattr(self.MODEL[i],'pgh_event_model'):
                pytest.skip("Non-tracked model")
            original_instance = self.INSTANCE[i]
            original_instance =self.MODEL[i].objects.filter(pk=original_instance.pk).first() 
            payload = self.UPDATE_PAYLOAD[i]
            updated_instance = self.CREATE_SCHEMA[i].model_validate(payload).model_dump_django(instance=deepcopy(original_instance))
            if hasattr(original_instance, 'parent_events'):
                insert_event = original_instance.parent_events.filter(pgh_label='create').first()
            else:
                insert_event = original_instance.events.filter(pgh_label='create').first()
            response = self.call_api_endpoint('PUT', self.get_route_url_history_revert(original_instance, insert_event), **config)
            with self.subTest(i=i):
                # Assert response content
                if scenario == 'HTTPS Authenticated':
                    updated_id = response.json()['id']
                    reverted_instance =self.MODEL[i].objects.filter(id=updated_id).first() 
                    self.assertIsNotNone(reverted_instance, 'The updated instance does not exist')
                    self.assertNotEqual(
                        [getattr(original_instance,field.name) for field in self.MODEL[i]._meta.concrete_fields],
                        [getattr(updated_instance,field.name) for field in self.MODEL[i]._meta.concrete_fields]
                    )
                    self.assertNotEqual(
                        [getattr(reverted_instance,field.name) for field in self.MODEL[i]._meta.concrete_fields],
                        [getattr(updated_instance,field.name) for field in self.MODEL[i]._meta.concrete_fields]
                    )
                    self.assertEqual(
                        [getattr(reverted_instance,field.name) for field in self.MODEL[i]._meta.concrete_fields],
                        [getattr(original_instance,field.name) for field in self.MODEL[i]._meta.concrete_fields]
                    )
                self.MODEL[i].objects.all().delete()


class TestPatientCaseController(ApiControllerTextMixin, TestCase):
    controller_path = '/api/patient-cases'
    FACTORY = factories.PatientCaseFactory
    MODEL = models.PatientCase
    SCHEMA = schemas.PatientCaseSchema
    CREATE_SCHEMA = schemas.PatientCaseCreateSchema             


class TestNeoplastcEntityController(ApiControllerTextMixin, TestCase):
    controller_path = '/api/neoplastic-entities'
    FACTORY = factories.PrimaryNeoplasticEntityFactory
    MODEL = models.NeoplasticEntity
    SCHEMA = schemas.NeoplasticEntitySchema
    CREATE_SCHEMA = schemas.NeoplasticEntityCreateSchema    
    

class TestStagingController(ApiControllerTextMixin, TestCase):
    controller_path = '/api/stagings'
    FACTORY = [
        factories.TNMStagingFactory, 
        factories.FIGOStagingFactory,
    ]
    MODEL = [
        models.TNMStaging, 
        models.FIGOStaging,
    ]
    SCHEMA = [
        schemas.TNMStagingSchema, 
        schemas.FIGOStagingSchema,
    ]
    CREATE_SCHEMA = [
        schemas.TNMStagingCreateSchema, 
        schemas.FIGOStagingCreateSchema
    ]
    

class TestTumorMarkerController(ApiControllerTextMixin, TestCase):
    controller_path = '/api/tumor-markers'
    FACTORY = factories.TumorMarkerTestFactory
    MODEL = models.TumorMarker
    SCHEMA = schemas.TumorMarkerSchema
    CREATE_SCHEMA = schemas.TumorMarkerCreateSchema    
    

class TestRiskAssessmentController(ApiControllerTextMixin, TestCase):
    controller_path = '/api/risk-assessments'
    FACTORY = factories.RiskAssessmentFactory
    MODEL = models.RiskAssessment
    SCHEMA = schemas.RiskAssessmentSchema
    CREATE_SCHEMA = schemas.RiskAssessmentCreateSchema    
    
    
class TestSystemicTherapyController(ApiControllerTextMixin, TestCase):
    controller_path = '/api/systemic-therapies'
    FACTORY = factories.SystemicTherapyFactory
    MODEL = models.SystemicTherapy
    SCHEMA = schemas.SystemicTherapySchema
    CREATE_SCHEMA = schemas.SystemicTherapyCreateSchema    
    
    
class TestSystemicTherapyMedicationController(ApiControllerTextMixin, TestCase):
    controller_path = '/api/systemic-therapies'
    FACTORY = factories.SystemicTherapyMedicationFactory
    MODEL = models.SystemicTherapyMedication
    SCHEMA = schemas.SystemicTherapyMedicationSchema
    CREATE_SCHEMA = schemas.SystemicTherapyMedicationCreateSchema    

    def get_route_url(self, instance):
        return f'/{instance.systemic_therapy.id}/medications'
        
    def get_route_url_with_id(self, instance):
        return f'/{instance.systemic_therapy.id}/medications/{instance.id}'

    def get_route_url_history(self, instance):
        return f'/{instance.systemic_therapy.id}/medications/{instance.id}/history/events'
    
    def get_route_url_history_with_id(self, instance, event):
        return f'/{instance.systemic_therapy.id}/medications/{instance.id}/history/events/{event.pgh_id}'
    
    def get_route_url_history_revert(self, instance, event):
        return f'/{instance.systemic_therapy.id}/medications/{instance.id}/history/events/{event.pgh_id}/reversion'
    

class TestSurgeryController(ApiControllerTextMixin, TestCase):
    controller_path = '/api/surgeries'
    FACTORY = factories.SurgeryFactory
    MODEL = models.Surgery
    SCHEMA = schemas.SurgerySchema
    CREATE_SCHEMA = schemas.SurgeryCreateSchema    
    
    
class TestRadiotherapyController(ApiControllerTextMixin, TestCase):
    controller_path = '/api/radiotherapies'
    FACTORY = factories.RadiotherapyFactory
    MODEL = models.Radiotherapy
    SCHEMA = schemas.RadiotherapySchema
    CREATE_SCHEMA = schemas.RadiotherapyCreateSchema    
    
class TestRadiotherapyDosageController(ApiControllerTextMixin, TestCase):
    controller_path = '/api/radiotherapies'
    FACTORY = factories.RadiotherapyDosageFactory
    MODEL = models.RadiotherapyDosage
    SCHEMA = schemas.RadiotherapyDosageSchema
    CREATE_SCHEMA = schemas.RadiotherapyDosageCreateSchema    

    def get_route_url(self, instance):
        return f'/{instance.radiotherapy.id}/dosages'
        
    def get_route_url_with_id(self, instance):
        return f'/{instance.radiotherapy.id}/dosages/{instance.id}'
    
    def get_route_url_history(self, instance):
        return f'/{instance.radiotherapy.id}/dosages/{instance.id}/history/events'
    
    def get_route_url_history_with_id(self, instance, event):
        return f'/{instance.radiotherapy.id}/dosages/{instance.id}/history/events/{event.pgh_id}'
    
    def get_route_url_history_revert(self, instance, event):
        return f'/{instance.radiotherapy.id}/dosages/{instance.id}/history/events/{event.pgh_id}/reversion'


class TestRadiotherapySettingController(ApiControllerTextMixin, TestCase):
    controller_path = '/api/radiotherapies'
    FACTORY = factories.RadiotherapySettingFactory
    MODEL = models.RadiotherapySetting
    SCHEMA = schemas.RadiotherapySettingSchema
    CREATE_SCHEMA = schemas.RadiotherapySettingCreateSchema    

    def get_route_url(self, instance):
        return f'/{instance.radiotherapy.id}/settings'
        
    def get_route_url_with_id(self, instance):
        return f'/{instance.radiotherapy.id}/settings/{instance.id}'
    
    def get_route_url_history(self, instance):
        return f'/{instance.radiotherapy.id}/settings/{instance.id}/history/events'
    
    def get_route_url_history_with_id(self, instance, event):
        return f'/{instance.radiotherapy.id}/settings/{instance.id}/history/events/{event.pgh_id}'
    
    def get_route_url_history_revert(self, instance, event):
        return f'/{instance.radiotherapy.id}/settings/{instance.id}/history/events/{event.pgh_id}/reversion'
    
class TestTreatmentResponseController(ApiControllerTextMixin, TestCase):
    controller_path = '/api/treatment-responses'
    FACTORY = factories.TreatmentResponseFactory
    MODEL = models.TreatmentResponse
    SCHEMA = schemas.TreatmentResponseSchema
    CREATE_SCHEMA = schemas.TreatmentResponseCreateSchema    
    
    
class TestAdverseEventController(ApiControllerTextMixin, TestCase):
    controller_path = '/api/adverse-events'
    FACTORY = factories.AdverseEventFactory
    MODEL = models.AdverseEvent
    SCHEMA = schemas.AdverseEventSchema
    CREATE_SCHEMA = schemas.AdverseEventCreateSchema    
    
class TestAdverseEventSuspectedCauseController(ApiControllerTextMixin, TestCase):
    controller_path = '/api/adverse-events'
    FACTORY = factories.AdverseEventSuspectedCauseFactory
    MODEL = models.AdverseEventSuspectedCause
    SCHEMA = schemas.AdverseEventSuspectedCauseSchema
    CREATE_SCHEMA = schemas.AdverseEventSuspectedCauseCreateSchema    

    def get_route_url(self, instance):
        return f'/{instance.adverse_event.id}/suspected-causes'
        
    def get_route_url_with_id(self, instance):
        return f'/{instance.adverse_event.id}/suspected-causes/{instance.id}'

    def get_route_url_history(self, instance):
        return f'/{instance.adverse_event.id}/suspected-causes/{instance.id}/history/events'
    
    def get_route_url_history_with_id(self, instance, event):
        return f'/{instance.adverse_event.id}/suspected-causes/{instance.id}/history/events/{event.pgh_id}'
    
    def get_route_url_history_revert(self, instance, event):
        return f'/{instance.adverse_event.id}/suspected-causes/{instance.id}/history/events/{event.pgh_id}/reversion'

class TestAdverseEventMitigationController(ApiControllerTextMixin, TestCase):
    controller_path = '/api/adverse-events'
    FACTORY = factories.AdverseEventMitigationFactory
    MODEL = models.AdverseEventMitigation
    SCHEMA = schemas.AdverseEventMitigationSchema
    CREATE_SCHEMA = schemas.AdverseEventMitigationCreateSchema    

    def get_route_url(self, instance):
        return f'/{instance.adverse_event.id}/mitigations'
        
    def get_route_url_with_id(self, instance):
        return f'/{instance.adverse_event.id}/mitigations/{instance.id}'
    
    def get_route_url_history(self, instance):
        return f'/{instance.adverse_event.id}/mitigations/{instance.id}/history/events'
    
    def get_route_url_history_with_id(self, instance, event):
        return f'/{instance.adverse_event.id}/mitigations/{instance.id}/history/events/{event.pgh_id}'
    
    def get_route_url_history_revert(self, instance, event):
        return f'/{instance.adverse_event.id}/mitigations/{instance.id}/history/events/{event.pgh_id}/reversion'
        
class TestGenomicVariantController(ApiControllerTextMixin, TestCase):
    controller_path = '/api/genomic-variants'
    FACTORY = factories.GenomicVariantFactory
    MODEL = models.GenomicVariant
    SCHEMA = schemas.GenomicVariantSchema
    CREATE_SCHEMA = schemas.GenomicVariantCreateSchema    
    

class TestTumorBoardController(ApiControllerTextMixin, TestCase):
    controller_path = '/api/tumor-boards'
    FACTORY = [
        factories.TumorBoardFactory,
        factories.MolecularTumorBoardFactory,
    ]
    MODEL = [
        models.UnspecifiedTumorBoard,
        models.MolecularTumorBoard,
    ]
    SCHEMA = [
        schemas.UnspecifiedTumorBoardSchema,
        schemas.MolecularTumorBoardSchema,
    ]
    CREATE_SCHEMA = [
        schemas.UnspecifiedTumorBoardCreateSchema,
        schemas.MolecularTumorBoardCreateSchema,
    ]
    
class TestMolecularTherapeuticRecommendationController(ApiControllerTextMixin, TestCase):
    controller_path = '/api/molecular-tumor-boards'
    FACTORY = factories.MolecularTherapeuticRecommendationFactory
    MODEL = models.MolecularTherapeuticRecommendation
    SCHEMA = schemas.MolecularTherapeuticRecommendationSchema
    CREATE_SCHEMA = schemas.MolecularTherapeuticRecommendationCreateSchema    
    
    def get_route_url(self, instance):
        return f'/{instance.molecular_tumor_board.id}/therapeutic-recommendations'
        
    def get_route_url_with_id(self, instance):
        return f'/{instance.molecular_tumor_board.id}/therapeutic-recommendations/{instance.id}'
    
    def get_route_url_history(self, instance):
        return f'/{instance.molecular_tumor_board.id}/therapeutic-recommendations/{instance.id}/history/events'
    
    def get_route_url_history_with_id(self, instance, event):
        return f'/{instance.molecular_tumor_board.id}/therapeutic-recommendations/{instance.id}/history/events/{event.pgh_id}'
    
    def get_route_url_history_revert(self, instance, event):
        return f'/{instance.molecular_tumor_board.id}/therapeutic-recommendations/{instance.id}/history/events/{event.pgh_id}/reversion'
    
        
class TestTherapyLineController(ApiControllerTextMixin, TestCase):
    controller_path = '/api/therapy-lines'
    FACTORY = factories.TherapyLineFactory
    MODEL = models.TherapyLine
    SCHEMA = schemas.TherapyLineSchema
    CREATE_SCHEMA = schemas.TherapyLineCreateSchema    

class TestPerformanceStatusController(ApiControllerTextMixin, TestCase):
    controller_path = '/api/performance-status'
    FACTORY = factories.PerformanceStatusFactory
    MODEL = models.PerformanceStatus
    SCHEMA = schemas.PerformanceStatusSchema
    CREATE_SCHEMA = schemas.PerformanceStatusCreateSchema    
    
    
class TestLifestyleController(ApiControllerTextMixin, TestCase):
    controller_path = '/api/lifestyles'
    FACTORY = factories.LifestyleFactory
    MODEL = models.Lifestyle
    SCHEMA = schemas.LifestyleSchema
    CREATE_SCHEMA = schemas.LifestyleCreateSchema    
    
    
class TestFamilyHistoryController(ApiControllerTextMixin, TestCase):
    controller_path = '/api/family-histories'
    FACTORY = factories.FamilyHistoryFactory
    MODEL = models.FamilyHistory
    SCHEMA = schemas.FamilyHistorySchema
    CREATE_SCHEMA = schemas.FamilyHistoryCreateSchema    


class TestVitalsController(ApiControllerTextMixin, TestCase):
    controller_path = '/api/vitals'
    FACTORY = factories.VitalsFactory
    MODEL = models.Vitals
    SCHEMA = schemas.VitalsSchema
    CREATE_SCHEMA = schemas.VitalsCreateSchema    


class TestComorbiditiesAssessmentController(ApiControllerTextMixin, TestCase):
    controller_path = '/api/comorbidities-assessments'
    FACTORY = factories.ComorbiditiesAssessmentFactory
    MODEL = models.ComorbiditiesAssessment
    SCHEMA = schemas.ComorbiditiesAssessmentSchema
    CREATE_SCHEMA = schemas.ComorbiditiesAssessmentCreateSchema    
    
    @parameterized.expand(common.ApiControllerTestMixin.get_scenarios)
    def test_get_all_comorbidities_panels(self, scenario, config):       
        response = self.call_api_endpoint('GET', '/meta/panels', **config)
        if scenario == 'HTTPS Authenticated':
            self.assertEqual(response.status_code, 200)

    @parameterized.expand(common.ApiControllerTestMixin.get_scenarios)
    def test_get_comorbidities_panel_by_name(self, scenario, config):    
        panel = 'Charlson'
        response = self.call_api_endpoint('GET', f'/meta/panels/{panel}', **config)
        if scenario == 'HTTPS Authenticated':
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()['name'], panel)
            self.assertEqual(len(response.json()['categories']), 16)
            
class TestGenomicSignatureController(ApiControllerTextMixin, TestCase):
    controller_path = '/api/genomic-signatures'
    FACTORY = [
        factories.TumorMutationalBurdenFactory, 
        factories.LossOfHeterozygosityFactory,
        factories.MicrosatelliteInstabilityFactory,
        factories.HomologousRecombinationDeficiencyFactory,
        factories.TumorNeoantigenBurdenFactory,
        factories.AneuploidScoreFactory,
    ]
    MODEL = [
        models.TumorMutationalBurden, 
        models.LossOfHeterozygosity,
        models.MicrosatelliteInstability,
        models.HomologousRecombinationDeficiency,
        models.TumorNeoantigenBurden,
        models.AneuploidScore,
    ]
    SCHEMA = [
        schemas.TumorMutationalBurdenSchema, 
        schemas.LossOfHeterozygositySchema,
        schemas.MicrosatelliteInstabilitySchema,
        schemas.HomologousRecombinationDeficiencySchema,
        schemas.TumorNeoantigenBurdenSchema,
        schemas.AneuploidScoreSchema,
    ]
    CREATE_SCHEMA = [
        schemas.TumorMutationalBurdenCreateSchema, 
        schemas.LossOfHeterozygosityCreateSchema,
        schemas.MicrosatelliteInstabilityCreateSchema,
        schemas.HomologousRecombinationDeficiencyCreateSchema,
        schemas.TumorNeoantigenBurdenCreateSchema,
        schemas.AneuploidScoreCreateSchema,
    ]
    