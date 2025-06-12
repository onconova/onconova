import pghistory
from uuid import UUID
from pop.core.models import BaseModel
from pop.core.auth.models import User
from pop.interoperability.schemas import PatientCaseBundle
from pop.core.auth.schemas import UserSchema
from pop.oncology import models, schemas
from pop.tests import factories
from django.test import TestCase

from pop.interoperability.parsers import BundleParser


class BundleParserTest(TestCase):
    mixin = BaseModel

    @classmethod
    def setUpTestData(cls):
        # Simulate bundling in an external setting
        cls.original_user = factories.UserFactory()
        with pghistory.context(username=cls.original_user.username):
            cls.original_case = factories.PatientCaseFactory()
            basic = dict(case=cls.original_case)
            cls.original_primary_entity = factories.PrimaryNeoplasticEntityFactory(
                **basic
            )
            cls.original_secondary_entity = factories.MetastaticNeoplasticEntityFactory(
                **basic, related_primary=cls.original_primary_entity
            )
            related_entities = [
                cls.original_primary_entity,
                cls.original_secondary_entity,
            ]
            cls.original_treatment_response = factories.TreatmentResponseFactory(
                **basic, assessed_entities=related_entities
            )
            cls.original_risk_assessment = factories.RiskAssessmentFactory(
                **basic, assessed_entities=related_entities
            )
            cls.original_tumor_marker = factories.TumorMarkerTestFactory(
                **basic, related_entities=related_entities
            )
            cls.original_family_history = factories.FamilyHistoryFactory(**basic)
            cls.original_lifestyle = factories.LifestyleFactory(**basic)
            cls.original_vitals = factories.VitalsFactory(**basic)
            cls.original_genomic_variant = factories.GenomicVariantFactory(**basic)
            cls.original_performance_status = factories.PerformanceStatusFactory(
                **basic
            )
            cls.original_comorbidities = factories.ComorbiditiesAssessmentFactory(
                **basic, index_condition=cls.original_primary_entity
            )
            cls.original_systemic_therapy = factories.SystemicTherapyFactory(
                **basic, targeted_entities=related_entities, therapy_line=None
            )
            cls.original_systemic_therapy_medication = (
                factories.SystemicTherapyMedicationFactory(
                    systemic_therapy=cls.original_systemic_therapy
                )
            )
            cls.original_radiotherapy = factories.RadiotherapyFactory(
                **basic, targeted_entities=related_entities, therapy_line=None
            )
            cls.original_radiotherapy_dosage = factories.RadiotherapyDosageFactory(
                radiotherapy=cls.original_radiotherapy
            )
            cls.original_radiotherapy_setting = factories.RadiotherapySettingFactory(
                radiotherapy=cls.original_radiotherapy
            )
            cls.original_adverse_event = factories.AdverseEventFactory(**basic)
            cls.original_adverse_event_cause = (
                factories.AdverseEventSuspectedCauseFactory(
                    adverse_event=cls.original_adverse_event,
                    systemic_therapy=cls.original_systemic_therapy,
                )
            )
            cls.original_adverse_event_mitigation = (
                factories.AdverseEventMitigationFactory(
                    adverse_event=cls.original_adverse_event
                )
            )
            cls.bundle = PatientCaseBundle.model_validate(cls.original_case)
            cls.original_staging = factories.TNMStagingFactory.create(
                **basic, staged_entities=related_entities
            )
            cls.original_genomic_signature = (
                factories.TumorMutationalBurdenFactory.create(**basic)
            )
            cls.original_tumor_board = factories.MolecularTumorBoardFactory(
                **basic, related_entities=related_entities
            )
            cls.original_tumor_board_recommendation = (
                factories.MolecularTherapeuticRecommendationFactory(
                    molecular_tumor_board=cls.original_tumor_board,
                    supporting_genomic_variants=[cls.original_genomic_variant],
                    supporting_tumor_markers=[],
                    supporting_genomic_signatures=[],
                )
            )
            # TODO: currently bugged in model_validate, can be removed once fixed
            cls.bundle.stagings = [
                schemas.TNMStagingSchema.model_validate(cls.original_staging)
            ]
            cls.bundle.genomicSignatures = [
                schemas.TumorMutationalBurdenSchema.model_validate(
                    cls.original_genomic_signature
                )
            ]
            cls.bundle.familyHistory = [
                schemas.FamilyHistorySchema.model_validate(cls.original_family_history)
            ]
            cls.bundle.tumorBoards = [
                schemas.MolecularTumorBoardSchema.model_validate(
                    cls.original_tumor_board
                )
            ]
            # Remove all instances of the "external" resources
            for resource in (
                cls.original_user,
                cls.original_case,
            ):
                resource.delete()
        # Simulate parsing of the external bundle
        cls.importing_user = factories.UserFactory()
        cls.parser = BundleParser(cls.bundle)

    def test_get_or_create_user_creates_external_user(self):
        """Test that a new user is created when not found."""
        self.original_user.save()
        user_schema = UserSchema.model_validate(self.original_user)
        self.original_user.delete()
        user = self.parser.get_or_create_user(user_schema)

        self.assertTrue(
            User.objects.filter(username=self.original_user.username).exists()
        )
        self.assertEqual(user.email, self.original_user.email)
        self.assertEqual(user.access_level, 0)
        self.assertEqual(user.is_active, False)

    def test_get_or_create_user_retrieves_existing_user(self):
        """Test that an existing user is retrieved and not duplicated."""
        user_schema = UserSchema.model_validate(self.importing_user)
        retrieved_user = self.parser.get_or_create_user(user_schema)
        self.assertEqual(retrieved_user.id, self.importing_user.id)

    def test_completed_data_categories_import(self):
        """Test that data completion statuses are correctly imported."""
        self.bundle.completedDataCategories = {
            "Diagnosis": schemas.PatientCaseDataCompletionStatusSchema(
                status=True, timestamp="2024-01-01T12:00:00Z", username="doctor1"
            )
        }
        self.parser.import_bundle()

        imported_case = models.PatientCase.objects.get(
            clinical_identifier=self.original_case.clinical_identifier
        )
        self.assertTrue(
            models.PatientCaseDataCompletion.objects.filter(
                case=imported_case, category="Diagnosis"
            ).exists()
        )

    def _import_bundle(self):
        self.imported_case = self.parser.import_bundle()
        self.imported_primary_entity = models.NeoplasticEntity.objects.get(
            case=self.imported_case, relationship="primary"
        )
        self.imported_secondary_entity = models.NeoplasticEntity.objects.get(
            case=self.imported_case, relationship="metastatic"
        )
        self.imported_systemic_therapy = models.SystemicTherapy.objects.get(
            case=self.imported_case
        )
        self.imported_radiotherapy = models.Radiotherapy.objects.get(
            case=self.imported_case
        )

    def test_import_bundle__patient_case(self):
        self._import_bundle()
        # Ensure the case data has been imported properly
        imported_case = models.PatientCase.objects.get(
            clinical_identifier=self.original_case.clinical_identifier
        )
        self.assertEqual(
            imported_case.pseudoidentifier, self.original_case.pseudoidentifier
        )
        self.assertEqual(
            imported_case.clinical_identifier, self.original_case.clinical_identifier
        )

    def test_import_bundle__neoplastic_entities(self):
        self._import_bundle()
        # Ensure the primary neoplastic entity has been imported properly
        imported_primary_entity = models.NeoplasticEntity.objects.get(
            case=self.imported_case, relationship="primary"
        )
        self.assertEqual(
            imported_primary_entity.description,
            self.original_primary_entity.description,
        )

        # Ensure the secondary neoplastic entity has been imported properly
        imported_secondary_entity = models.NeoplasticEntity.objects.get(
            case=self.imported_case, related_primary=imported_primary_entity
        )
        self.assertEqual(
            imported_secondary_entity.description,
            self.original_secondary_entity.description,
        )

    def test_import_bundle__tnm_stagings(self):
        self._import_bundle()
        # Ensure the staging has been imported properly
        imported_staging = models.TNMStaging.objects.get(case=self.imported_case)
        self.assertEqual(
            imported_staging.description, self.original_staging.description
        )
        # Check resolved references
        self.assertIn(
            self.imported_primary_entity, imported_staging.staged_entities.all()
        )
        self.assertIn(
            self.imported_secondary_entity, imported_staging.staged_entities.all()
        )

    def test_import_bundle__systemic_therapies(self):
        self._import_bundle()
        # Ensure the systemic therapy has been imported properly
        imported_systemic_therapy = models.SystemicTherapy.objects.get(
            case=self.imported_case
        )
        imported_systemic_therapy_medication = (
            imported_systemic_therapy.medications.first()
        )
        self.assertEqual(
            imported_systemic_therapy.period, self.original_systemic_therapy.period
        )
        # Check nested resources
        self.assertEqual(
            imported_systemic_therapy_medication.description,
            self.original_systemic_therapy_medication.description,
        )
        # Check resolved references
        self.assertIn(
            self.imported_primary_entity,
            imported_systemic_therapy.targeted_entities.all(),
        )
        self.assertIn(
            self.imported_secondary_entity,
            imported_systemic_therapy.targeted_entities.all(),
        )

    def test_import_bundle__radiotherapies(self):
        self._import_bundle()
        # Ensure the radiotherapy has been imported properly
        imported_radiotherapy = models.Radiotherapy.objects.get(case=self.imported_case)
        imported_radiotherapy_dosage = imported_radiotherapy.dosages.first()
        imported_radiotherapy_setting = imported_radiotherapy.settings.first()
        # Check nested resources
        self.assertEqual(
            imported_radiotherapy_dosage.description,
            self.original_radiotherapy_dosage.description,
        )
        self.assertEqual(
            imported_radiotherapy_setting.description,
            self.original_radiotherapy_setting.description,
        )
        # Check resolved references
        self.assertIn(
            self.imported_primary_entity, imported_radiotherapy.targeted_entities.all()
        )
        self.assertIn(
            self.imported_secondary_entity,
            imported_radiotherapy.targeted_entities.all(),
        )

    def test_import_bundle__genomic_variants(self):
        self._import_bundle()
        # Ensure the genomic variant has been imported properly
        imported_genomic_variant = models.GenomicVariant.objects.get(
            case=self.imported_case
        )
        self.assertEqual(
            imported_genomic_variant.protein_hgvs,
            self.original_genomic_variant.protein_hgvs,
        )

    def test_import_bundle__risk_assessments(self):
        self._import_bundle()
        # Ensure the risk assessment has been imported properly
        imported_risk_assessment = models.RiskAssessment.objects.get(
            case=self.imported_case
        )

    def test_import_bundle__family_histories(self):
        self._import_bundle()
        # Ensure the family history has been imported properly
        imported_family_history = models.FamilyHistory.objects.get(
            case=self.imported_case
        )

    def test_import_bundle__comorbidities(self):
        self._import_bundle()
        # Ensure the comordbities has been imported properly
        imported_comorbidity = models.ComorbiditiesAssessment.objects.get(
            case=self.imported_case
        )

    def test_import_bundle__lifestyles(self):
        self._import_bundle()
        # Ensure the lifestyle has been imported properly
        imported_lifestyle = models.Lifestyle.objects.get(case=self.imported_case)

    def test_import_bundle__vitals(self):
        self._import_bundle()
        # Ensure the vitals has been imported properly
        imported_vitals = models.Vitals.objects.get(case=self.imported_case)

    def test_import_bundle__tumor_markers(self):
        self._import_bundle()
        # Ensure the tumor marker has been imported properly
        imported_tumor_marker = models.TumorMarker.objects.get(case=self.imported_case)

    def test_import_bundle__treatment_response(self):
        self._import_bundle()
        # Ensure the treatment response has been imported properly
        imported_treatment_response = models.TreatmentResponse.objects.get(
            case=self.imported_case
        )

    def test_import_bundle__adverse_events(self):
        self._import_bundle()
        # Ensure the adverse event has been imported properly
        imported_adverse_event = models.AdverseEvent.objects.get(
            case=self.imported_case
        )
        imported_adverse_event_cause = imported_adverse_event.suspected_causes.first()
        imported_adverse_event_mitigation = imported_adverse_event.mitigations.first()
        # Check nested resources
        self.assertEqual(
            imported_adverse_event_cause.causality,
            self.original_adverse_event_cause.causality,
        )
        self.assertEqual(
            imported_adverse_event_cause.systemic_therapy,
            self.imported_systemic_therapy,
        )
        self.assertEqual(
            imported_adverse_event_mitigation.description,
            self.original_adverse_event_mitigation.description,
        )

    def test_import_bundle__genomic_signatures(self):
        self._import_bundle()
        # Ensure the genomic signature has been imported properly
        imported_genomic_signature = models.TumorMutationalBurden.objects.get(
            case=self.imported_case
        )
        self.assertEqual(
            imported_genomic_signature.description,
            self.original_genomic_signature.description,
        )

    def test_import_bundle__performance_status(self):
        self._import_bundle()
        # Ensure the performance status has been imported properly
        imported_performance_status = models.PerformanceStatus.objects.get(
            case=self.imported_case
        )
        self.assertEqual(
            imported_performance_status.description,
            self.original_performance_status.description,
        )

    def test_import_bundle__molecular_tumor_boards(self):
        self._import_bundle()
        # Ensure the adverse event has been imported properly
        imported_molecular_tumor_board = models.MolecularTumorBoard.objects.get(
            case=self.imported_case
        )
        imported_molecular_tumor_board_recommendation = (
            imported_molecular_tumor_board.therapeutic_recommendations.first()
        )
        # Check nested resources
