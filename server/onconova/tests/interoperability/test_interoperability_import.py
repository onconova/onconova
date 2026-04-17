from uuid import UUID

import pghistory
from django.test import TestCase

from onconova.core.auth.models import User
from onconova.core.auth.schemas import User as UserSchema
from onconova.core.history.schemas import HistoryEvent
from onconova.core.models import BaseModel
from onconova.interoperability.parsers import BundleParser
from onconova.interoperability.schemas import PatientCaseBundle, UserExport
from onconova.oncology import models, schemas
from onconova.tests import factories


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
                **basic,
                targeted_entities=related_entities,
                therapy_line=None,
                medications=[],
            )
            cls.original_systemic_therapy_medication = (
                factories.SystemicTherapyMedicationFactory(
                    systemic_therapy=cls.original_systemic_therapy
                )
            )
            cls.original_radiotherapy = factories.RadiotherapyFactory(
                **basic,
                targeted_entities=related_entities,
                therapy_line=None,
                settings=[],
                dosages=[],
            )
            cls.original_radiotherapy_dosage = factories.RadiotherapyDosageFactory(
                radiotherapy=cls.original_radiotherapy
            )
            cls.original_radiotherapy_setting = factories.RadiotherapySettingFactory(
                radiotherapy=cls.original_radiotherapy
            )
            cls.original_adverse_event = factories.AdverseEventFactory(
                **basic,
                suspected_causes=[],
                mitigations=[],
            )
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
            cls.original_staging = factories.TNMStagingFactory.create(
                **basic, staged_entities=related_entities
            )
            cls.original_genomic_signature = (
                factories.TumorMutationalBurdenFactory.create(**basic)
            )
            cls.original_tumor_board = factories.MolecularTumorBoardFactory(
                **basic,
                related_entities=related_entities,
                therapeutic_recommendations=[],
            )
            cls.original_tumor_board_recommendation = (
                factories.MolecularTherapeuticRecommendationFactory(
                    molecular_tumor_board=cls.original_tumor_board,
                    supporting_genomic_variants=[cls.original_genomic_variant],
                    supporting_tumor_markers=[],
                    supporting_genomic_signatures=[],
                )
            )

            # Create bundle
            cls.bundle = PatientCaseBundle.model_validate(cls.original_case)
            cls.bundle.contributorsDetails = [
                UserExport.model_validate(cls.original_user)
            ]
            # Add a custom event to the case
            pghistory.create_event(cls.original_case, label="update")
            pghistory.create_event(cls.original_case, label="export")
            # Get all events related to the case and delete the original audit trail
            cls.bundle.history = [
                HistoryEvent.model_validate(event)
                for event in cls.bundle.resolve_history(cls.original_case) or []
            ]

            cls.original_events = list(
                cls.original_case.events.all().order_by("pgh_created_at")
            )
            cls.original_case.events.all().delete()

            cls.original_primary_entity_events = list(
                cls.original_primary_entity.events.all().order_by("pgh_created_at")
            )
            cls.original_primary_entity.events.all().delete()

            # Remove all instances of the "external" resources
            for resource in (
                cls.original_user,
                cls.original_case,
            ):
                resource.delete()

        # Assign a new id to the bundle
        cls.bundle.pseudoidentifier = "A.123.456.7890"
        cls.bundle.clinicalIdentifier = "123456789"

        # Simulate parsing of the external bundle
        cls.importing_user = factories.UserFactory()
        cls.parser = BundleParser(cls.bundle)

    def test_get_or_create_user_creates_external_user(self):
        """Test that a new user is created when not found."""
        self.original_user.save()
        user_schema = UserExport.model_validate(self.original_user)
        self.original_user.delete()
        user = self.parser.get_or_create_user(user_schema)

        self.assertTrue(
            User.objects.filter(username=f"{self.original_user.username}-ext").exists()
        )
        self.assertEqual(user.email, self.original_user.email)
        self.assertEqual(user.access_level, 0)
        self.assertEqual(user.is_active, False)

    def test_get_or_create_user_retrieves_existing_user(self):
        """Test that an existing user is retrieved and not duplicated."""
        user_schema = UserExport.model_validate(self.importing_user)
        retrieved_user = self.parser.get_or_create_user(user_schema)
        self.assertEqual(retrieved_user.id, self.importing_user.id)

    def test_completed_data_categories_import(self):
        """Test that data completion statuses are correctly imported."""
        self.bundle.completedDataCategories = {
            "Diagnosis": schemas.PatientCaseDataCompletionStatus(
                status=True, timestamp="2024-01-01T12:00:00Z", username="doctor1"
            )
        }
        self.imported_case = self.parser.import_bundle()
        self.assertTrue(
            models.PatientCaseDataCompletion.objects.filter(
                case=self.imported_case, category="Diagnosis"
            ).exists()
        )

    def _import_bundle(self):

        with pghistory.context(username=self.importing_user.username):
            self.imported_case = self.parser.import_bundle()
        self.imported_primary_entity = models.NeoplasticEntity.objects.get(
            case=self.imported_case, relationship="primary"
        )
        self.imported_secondary_entity = models.NeoplasticEntity.objects.get(
            case=self.imported_case, relationship="metastatic"
        )
        self.imported_staging = models.TNMStaging.objects.get(case=self.imported_case)
        self.imported_systemic_therapy = models.SystemicTherapy.objects.get(
            case=self.imported_case
        )
        self.imported_radiotherapy = models.Radiotherapy.objects.get(
            case=self.imported_case
        )

    def test_import_bundle__patient_case(self):
        self._import_bundle()
        self.assertNotEqual(
            self.imported_case.pseudoidentifier, self.original_case.pseudoidentifier
        )
        self.assertNotEqual(
            self.imported_case.clinical_identifier,
            self.original_case.clinical_identifier,
        )
        self.assertIsNotNone(
            self.imported_case.events.filter(pgh_label="import").first()
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
        self.assertIsNotNone(
            self.imported_primary_entity.events.filter(pgh_label="import").first()
        )

        # Ensure the secondary neoplastic entity has been imported properly
        imported_secondary_entity = models.NeoplasticEntity.objects.get(
            case=self.imported_case, related_primary=imported_primary_entity
        )
        self.assertEqual(
            imported_secondary_entity.description,
            self.original_secondary_entity.description,
        )
        self.assertIsNotNone(
            self.imported_secondary_entity.events.filter(pgh_label="import").first()
        )

    def test_import_bundle__tnm_stagings(self):
        self._import_bundle()
        # Ensure the staging has been imported properly
        imported_staging = models.TNMStaging.objects.get(case=self.imported_case)
        self.assertEqual(imported_staging.stage, self.original_staging.stage)
        # Check resolved references
        self.assertIn(
            self.imported_primary_entity, imported_staging.staged_entities.all()
        )
        self.assertIn(
            self.imported_secondary_entity, imported_staging.staged_entities.all()
        )
        self.assertIsNotNone(
            self.imported_staging.events.filter(pgh_label="import").first()
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
        self.assertIsNotNone(
            imported_systemic_therapy.events.filter(pgh_label="import").first()
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
        self.assertIsNotNone(
            imported_radiotherapy.events.filter(pgh_label="import").first()
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
        self.assertIsNotNone(
            imported_genomic_variant.events.filter(pgh_label="import").first()
        )

    def test_import_bundle__risk_assessments(self):
        self._import_bundle()
        # Ensure the risk assessment has been imported properly
        imported_risk_assessment = models.RiskAssessment.objects.get(
            case=self.imported_case
        )
        self.assertEqual(
            imported_risk_assessment.description,
            self.original_risk_assessment.description,
        )
        self.assertIsNotNone(
            imported_risk_assessment.events.filter(pgh_label="import").first()
        )

    def test_import_bundle__family_histories(self):
        self._import_bundle()
        # Ensure the family history has been imported properly
        imported_family_history = models.FamilyHistory.objects.get(
            case=self.imported_case
        )
        self.assertEqual(
            imported_family_history.description,
            self.original_family_history.description,
        )
        self.assertIsNotNone(
            imported_family_history.events.filter(pgh_label="import").first()
        )

    def test_import_bundle__comorbidities(self):
        self._import_bundle()
        # Ensure the comordbities has been imported properly
        imported_comorbidity = models.ComorbiditiesAssessment.objects.get(
            case=self.imported_case
        )
        self.assertIsNotNone(
            imported_comorbidity.events.filter(pgh_label="import").first()
        )

    def test_import_bundle__lifestyles(self):
        self._import_bundle()
        # Ensure the lifestyle has been imported properly
        imported_lifestyle = models.Lifestyle.objects.get(case=self.imported_case)
        self.assertEqual(
            imported_lifestyle.night_sleep,
            self.original_lifestyle.night_sleep,
        )
        self.assertIsNotNone(
            imported_lifestyle.events.filter(pgh_label="import").first()
        )

    def test_import_bundle__vitals(self):
        self._import_bundle()
        # Ensure the vitals has been imported properly
        imported_vitals = models.Vitals.objects.get(case=self.imported_case)
        self.assertIsNotNone(imported_vitals.events.filter(pgh_label="import").first())

    def test_import_bundle__tumor_markers(self):
        self._import_bundle()
        # Ensure the tumor marker has been imported properly
        imported_tumor_marker = models.TumorMarker.objects.get(case=self.imported_case)
        self.assertEqual(
            imported_tumor_marker.description,
            self.original_tumor_marker.description,
        )
        self.assertIsNotNone(
            imported_tumor_marker.events.filter(pgh_label="import").first()
        )

    def test_import_bundle__treatment_response(self):
        self._import_bundle()
        # Ensure the treatment response has been imported properly
        imported_treatment_response = models.TreatmentResponse.objects.get(
            case=self.imported_case
        )
        self.assertEqual(
            imported_treatment_response.description,
            self.original_treatment_response.description,
        )
        self.assertIsNotNone(
            imported_treatment_response.events.filter(pgh_label="import").first()
        )

    def test_import_bundle__adverse_events(self):
        self._import_bundle()
        # Ensure the adverse event has been imported properly
        imported_adverse_event = models.AdverseEvent.objects.get(
            case=self.imported_case
        )
        self.assertIsNotNone(
            imported_adverse_event.events.filter(pgh_label="import").first()
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
        self.assertIsNotNone(
            imported_adverse_event_cause.events.filter(pgh_label="import").first()
        )
        self.assertEqual(
            imported_adverse_event_mitigation.description,
            self.original_adverse_event_mitigation.description,
        )
        self.assertIsNotNone(
            imported_adverse_event_mitigation.events.filter(pgh_label="import").first()
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
        self.assertIsNotNone(
            imported_genomic_signature.events.filter(pgh_label="import").first()
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
        self.assertIsNotNone(
            imported_performance_status.events.filter(pgh_label="import").first()
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
        self.assertIsNotNone(
            imported_molecular_tumor_board_recommendation.events.filter(
                pgh_label="import"
            ).first()
        )

    def test_import_bundle__case_history(self):
        self._import_bundle()
        # Ensure the case data has been imported properly
        imported_case_events = (
            self.imported_case.events.all()
            .order_by("pgh_created_at")
            .exclude(pgh_label="import")
        )
        self.assertEqual(len(imported_case_events), len(self.original_events))
        for original_event, event in zip(self.original_events, imported_case_events):
            self.assertEqual(original_event.pgh_label, event.pgh_label)
            self.assertEqual(
                f"{original_event.pgh_context['username']}-ext",
                event.pgh_context["username"],
            )
            self.assertEqual(original_event.pgh_created_at, event.pgh_created_at)

    def test_import_bundle__resource_history(self):
        self._import_bundle()
        # Ensure the case data has been imported properly
        imported_events = (
            self.imported_primary_entity.events.all()
            .order_by("pgh_created_at")
            .exclude(pgh_label="import")
        )
        self.assertEqual(len(imported_events), len(self.original_primary_entity_events))
        for original_event, event in zip(
            self.original_primary_entity_events, imported_events
        ):
            self.assertEqual(original_event.pgh_label, event.pgh_label)
            self.assertEqual(
                f"{original_event.pgh_context['username']}-ext",
                event.pgh_context["username"],
            )
            self.assertEqual(original_event.pgh_created_at, event.pgh_created_at)

    def test_import_bundle__forward_reference(self):
        """Import succeeds even when a referencing resource appears before the referenced one in the bundle."""
        bundle = self.bundle.model_copy(deep=True)
        # Reverse the list so the metastatic entity (which has relatedPrimaryId) comes first,
        # creating a forward reference to a resource not yet imported.
        bundle.neoplasticEntities = list(reversed(bundle.neoplasticEntities))

        parser = BundleParser(bundle)
        with pghistory.context(username=self.importing_user.username):
            imported_case = parser.import_bundle()

        primary = models.NeoplasticEntity.objects.get(
            case=imported_case, relationship="primary"
        )
        secondary = models.NeoplasticEntity.objects.get(
            case=imported_case, relationship="metastatic"
        )
        self.assertEqual(secondary.related_primary, primary)

    def test_import_bundle__missing_reference_raises_descriptive_error(self):
        """Import raises a clear, actionable ValueError when a referenced ID is absent from the bundle."""
        import uuid

        bundle = self.bundle.model_copy(deep=True)
        # Replace the metastatic entity's relatedPrimaryId with a UUID not present in the bundle
        secondary = next(
            e for e in bundle.neoplasticEntities if e.relatedPrimaryId is not None
        )
        nonexistent_id = str(uuid.uuid4())
        secondary.relatedPrimaryId = nonexistent_id

        parser = BundleParser(bundle)
        with self.assertRaises(ValueError) as ctx:
            parser.import_bundle()

        self.assertIn(str(nonexistent_id), str(ctx.exception))
        self.assertIn("unresolved references", str(ctx.exception))
