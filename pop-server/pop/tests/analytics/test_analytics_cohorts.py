from django.test import TestCase
from django.db.models import Q
from pop.analytics.schemas import CohortRule, CohortRuleset, RulesetCondition, CohortQueryFilter, CohortQueryEntity
from pop.oncology.models import PatientCase
from pop.tests.factories import (
    PatientCaseFactory, PrimaryNeoplasticEntityFactory, SystemicTherapyFactory, SystemicTherapyMedicationFactory
)

class TestCohortRules(TestCase):

    @classmethod 
    def setUpTestData(cls):
        cls.case1 = PatientCaseFactory.create(pseudoidentifier='A.123.456.78')
        cls.case2 = PatientCaseFactory.create(pseudoidentifier='B.123.456.78')
        cls.case3 = PatientCaseFactory.create(pseudoidentifier='C.123.456.78')
        
        SystemicTherapyMedicationFactory.create(systemic_therapy=SystemicTherapyFactory.create(case=cls.case1))
        SystemicTherapyMedicationFactory.create(systemic_therapy=SystemicTherapyFactory.create(case=cls.case2))
        
        PrimaryNeoplasticEntityFactory.create(case=cls.case1)
        PrimaryNeoplasticEntityFactory.create(case=cls.case2)

    def test_patient_case_rule_returns_q(self):
        value = self.case1.pseudoidentifier
        # case = PatientCaseFactory(pseudoidentifier=value)
        rule = CohortRule(
            entity=CohortQueryEntity.PatientCase,
            field='pseudoidentifier',
            operator=CohortQueryFilter.ExactStringFilter,
            value=value
        )
        query = next(rule.convert_to_query())
        # Assert the query object
        self.assertIsInstance(query, Q)
        self.assertEqual(query, Q(pseudoidentifier__iexact=value))
        # Test that cohort filtering works with the query
        cohort = PatientCase.objects.filter(query)
        self.assertQuerySetEqual(cohort, [self.case1])

    def test_related_model_rule_returns_subquery(self):
        value = 'primary'
        # entity = PrimaryNeoplasticEntityFactory(relationship='primary')
        rule = CohortRule(
            entity=CohortQueryEntity.NeoplasticEntity,
            field='relationship',
            operator=CohortQueryFilter.ExactStringFilter,
            value=value
        )
        query = next(rule.convert_to_query())
        # Assert the query object
        self.assertIsInstance(query, Q)
        # Test that cohort filtering works with the query
        cohort = PatientCase.objects.filter(query).order_by('pseudoidentifier')
        self.assertQuerySetEqual(cohort, [self.case1, self.case2])

    def test_related_nested_model_rule_returns_subquery(self):
        # entity = PrimaryNeoplasticEntityFactory(relationship='primary')
        rule = CohortRule(
            entity=CohortQueryEntity.SystemicTherapy,
            field='medications.drug',
            operator=CohortQueryFilter.NotIsNullFilter,
            value=True
        )
        query = next(rule.convert_to_query())
        # Assert the query object
        self.assertIsInstance(query, Q)
        # Test that cohort filtering works with the query
        cohort = PatientCase.objects.filter(query).order_by('pseudoidentifier')
        self.assertQuerySetEqual(cohort, [self.case1, self.case2])


    def test_and_ruleset_combines_q_objects(self):
        ruleset = CohortRuleset(
            condition=RulesetCondition.AND,
            rules=[
                CohortRule(
                    entity=CohortQueryEntity.PatientCase,
                    field='pseudoidentifier',
                    operator=CohortQueryFilter.ExactStringFilter,
                    value=self.case1.pseudoidentifier
                ),
                CohortRule(
                    entity=CohortQueryEntity.PatientCase,
                    field='clinical_center',
                    operator=CohortQueryFilter.ExactStringFilter,
                    value=self.case1.clinical_center
                ),
            ]
        )
        query = list(ruleset.convert_to_query())[0]
        # Assert the query object
        self.assertIsInstance(query, Q)
        self.assertEqual(query.connector, 'AND')
        self.assertEqual(query.children, [
            ('clinical_center__iexact', self.case1.clinical_center),
            ('pseudoidentifier__iexact', self.case1.pseudoidentifier)
        ])
        # Test that cohort filtering works with the query
        cohort = PatientCase.objects.filter(query).order_by('pseudoidentifier')
        self.assertQuerySetEqual(cohort, [self.case1])

    def test_or_ruleset_combines_q_objects(self):
        ruleset = CohortRuleset(
            condition=RulesetCondition.OR,
            rules=[
                CohortRule(
                    entity=CohortQueryEntity.PatientCase,
                    field='pseudoidentifier',
                    operator=CohortQueryFilter.ExactStringFilter,
                    value=self.case1.pseudoidentifier
                ),
                CohortRule(
                    entity=CohortQueryEntity.PatientCase,
                    field='pseudoidentifier',
                    operator=CohortQueryFilter.ExactStringFilter,
                    value=self.case2.pseudoidentifier
                ),
            ]
        )
        query = list(ruleset.convert_to_query())[0]
        # Assert the query object
        self.assertIsInstance(query, Q)
        self.assertEqual(query.connector, 'OR')
        self.assertEqual(query.children, [
            ('pseudoidentifier__iexact', self.case2.pseudoidentifier),
            ('pseudoidentifier__iexact', self.case1.pseudoidentifier),
        ])
        # Test that cohort filtering works with the query
        cohort = PatientCase.objects.filter(query).order_by('pseudoidentifier')
        self.assertQuerySetEqual(cohort, [self.case1, self.case2])

    def test_nested_rulesets(self):
        nested = CohortRuleset(
            condition=RulesetCondition.OR,
            rules=[
                CohortRule(
                    entity=CohortQueryEntity.PatientCase,
                    field='pseudoidentifier',
                    operator=CohortQueryFilter.ExactStringFilter,
                    value=self.case1.pseudoidentifier
                ),
                CohortRule(
                    entity=CohortQueryEntity.PatientCase,
                    field='pseudoidentifier',
                    operator=CohortQueryFilter.ExactStringFilter,
                    value=self.case2.pseudoidentifier
                ),
            ]
        )
        outer = CohortRuleset(
            condition=RulesetCondition.AND,
            rules=[
                nested,
                CohortRule(
                    entity=CohortQueryEntity.PatientCase,
                    field='clinical_center',
                    operator=CohortQueryFilter.ExactStringFilter,
                    value=self.case1.clinical_center
                ),
            ]
        )
        query = list(outer.convert_to_query())[0]
        # Assert the query object
        self.assertIsInstance(query, Q)
        self.assertEqual(query.connector, 'AND')
        # Test that cohort filtering works with the query
        cohort = PatientCase.objects.filter(query).order_by('pseudoidentifier')
        self.assertQuerySetEqual(cohort, [self.case1])