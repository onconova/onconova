import unittest
import requests
from unittest.mock import patch, MagicMock
from pop.terminology.models import AdministrativeGender as CodedConceptTestModel
from fhir.resources.R4B.valueset import (
    ValueSet,
    ValueSetCompose,
    ValueSetComposeInclude,
    ValueSetExpansion,
    ValueSetExpansionContains,
    ValueSetComposeIncludeConcept,
    ValueSetComposeIncludeFilter,
)
from pop.terminology.services import (
    download_canonical_url,
    expand_valueset,
    CodedConcept,
    download_valueset,
    download_codesystem,
    FilterOperator,
    follow_valueset_composition_rule,
    collect_codedconcept_terminology,
)


class TestExpandValueSet(unittest.TestCase):

    def test_expansion_with_predefined_expansion(self):
        # Mock valuesetdef with predefined expansion
        valuesetdef = ValueSet.construct(
            **dict(
                expansion=ValueSetExpansion.construct(
                    **dict(
                        contains=[
                            ValueSetExpansionContains(
                                code="code1", system="system1", version="version1"
                            ),
                            ValueSetExpansionContains(
                                code="code2", system="system2", version="version2"
                            ),
                        ]
                    )
                )
            )
        )
        expected_concepts = [
            CodedConcept(code="code1", system="system1", version="version1"),
            CodedConcept(code="code2", system="system2", version="version2"),
        ]
        self.assertEqual(expand_valueset(valuesetdef), expected_concepts)

    def test_expansion_with_composition_rules_include(self):
        # Mock valuesetdef with composition rules (include)
        valuesetdef = ValueSet.construct(
            **dict(
                compose=ValueSetCompose(
                    include=[
                        ValueSetComposeInclude(
                            system="system1",
                            concept=[ValueSetComposeIncludeConcept(code="code1")],
                        )
                    ]
                )
            )
        )
        # Mock follow_valueset_composition_rule to return expected concepts
        with patch(
            "pop.terminology.services.follow_valueset_composition_rule"
        ) as mock_follow_rule:
            mock_follow_rule.return_value = [
                CodedConcept(code="code1", system="system1", version="version1")
            ]
            expected_concepts = [
                CodedConcept(code="code1", system="system1", version="version1")
            ]
            self.assertEqual(expand_valueset(valuesetdef), expected_concepts)

    def test_expansion_with_composition_rules_exclude(self):
        # Mock valuesetdef with composition rules (exclude)
        valuesetdef = ValueSet.construct(
            **dict(
                compose=ValueSetCompose(
                    include=[
                        ValueSetComposeInclude(
                            system="system1",
                            concept=[ValueSetComposeIncludeConcept(code="code1")],
                        )
                    ],
                    exclude=[
                        ValueSetComposeInclude(
                            system="system1",
                            concept=[ValueSetComposeIncludeConcept(code="code1")],
                        )
                    ],
                )
            )
        )
        # Mock follow_valueset_composition_rule to return expected concepts
        with patch(
            "pop.terminology.services.follow_valueset_composition_rule"
        ) as mock_follow_rule:
            mock_follow_rule.return_value = [
                CodedConcept(code="code1", system="system1", version="version1")
            ]
            expected_concepts = []
            self.assertEqual(expand_valueset(valuesetdef), expected_concepts)

    def test_error_handling_when_neither_expansion_nor_composition_is_present(self):
        # Mock valuesetdef with neither expansion nor composition
        valuesetdef = ValueSet.construct()
        with self.assertRaises(ValueError):
            expand_valueset(valuesetdef)

    def test_error_handling_when_valuesetdef_is_none(self):
        with self.assertRaises(AttributeError):
            expand_valueset(None)

    def test_error_handling_when_valuesetdef_is_not_a_value_set_schema_object(self):
        with self.assertRaises(AttributeError):
            expand_valueset("not a ValueSet object")


class TestFollowValueSetCompositionRule(unittest.TestCase):
    def test_rule_with_system_no_concept_no_filter(self):
        rule = ValueSetComposeInclude(system="http://example.com/codesystem")
        codesystem = {
            "code1": CodedConcept(code="code1", system="http://example.com/codesystem")
        }
        with patch(
            "pop.terminology.services.download_codesystem", return_value=codesystem
        ):
            result = follow_valueset_composition_rule(rule)
            self.assertEqual(
                result,
                [CodedConcept(code="code1", system="http://example.com/codesystem")],
            )

    def test_rule_with_system_and_concept(self):
        rule = ValueSetComposeInclude(
            system="http://example.com/codesystem",
            concept=[ValueSetComposeIncludeConcept(code="code1")],
        )
        codesystem = {
            "code1": CodedConcept(code="code1", system="http://example.com/codesystem")
        }
        with patch(
            "pop.terminology.services.download_codesystem", return_value=codesystem
        ):
            result = follow_valueset_composition_rule(rule)
            self.assertEqual(
                result,
                [CodedConcept(code="code1", system="http://example.com/codesystem")],
            )

    def test_rule_with_system_and_filter(self):
        rule = ValueSetComposeInclude(
            system="http://example.com/codesystem",
            filter=[
                ValueSetComposeIncludeFilter.construct(
                    op=FilterOperator.IS_A, value="code1"
                )
            ],
        )
        codesystem = {
            "code1": CodedConcept(code="code1", system="http://example.com/codesystem")
        }
        with patch(
            "pop.terminology.services.download_codesystem", return_value=codesystem
        ):
            result = follow_valueset_composition_rule(rule)
            self.assertEqual(
                result,
                [CodedConcept(code="code1", system="http://example.com/codesystem")],
            )

    def test_rule_with_value_set(self):
        rule = ValueSetComposeInclude(valueSet=["http://example.com/valueset"])
        valueset_concepts = [
            CodedConcept(code="code1", system="http://example.com/valueset")
        ]
        with patch(
            "pop.terminology.services.download_valueset", return_value=valueset_concepts
        ):
            result = follow_valueset_composition_rule(rule)
            self.assertEqual(
                result,
                [CodedConcept(code="code1", system="http://example.com/valueset")],
            )

    def test_rule_with_system_and_value_set(self):
        rule = ValueSetComposeInclude(
            system="http://example.com/codesystem",
            valueSet=["http://example.com/valueset"],
        )
        codesystem = {
            "code1": CodedConcept(code="code1", system="http://example.com/codesystem")
        }
        valueset = MagicMock()
        valueset.concepts.return_value = [
            CodedConcept(code="code1", system="http://example.com/valueset")
        ]
        with patch(
            "pop.terminology.services.download_codesystem", return_value=codesystem
        ):
            with patch(
                "pop.terminology.services.download_valueset", return_value=valueset
            ):
                result = follow_valueset_composition_rule(rule)
                self.assertEqual(
                    result,
                    [
                        CodedConcept(
                            code="code1", system="http://example.com/codesystem"
                        )
                    ],
                )

    def test_rule_with_multiple_value_sets(self):
        rule = ValueSetComposeInclude(
            valueSet=["http://example.com/valueset1", "http://example.com/valueset2"]
        )
        valueset1_concepts = [
            CodedConcept(code="code1", system="http://example.com/codesystem"),
            CodedConcept(code="code2", system="http://example.com/codesystem"),
        ]
        valueset2_concepts = [
            CodedConcept(code="code2", system="http://example.com/codesystem"),
            CodedConcept(code="code3", system="http://example.com/codesystem"),
        ]
        with patch(
            "pop.terminology.services.download_valueset",
            side_effect=[valueset1_concepts, valueset2_concepts],
        ):
            result = follow_valueset_composition_rule(rule)
            self.assertEqual(
                result,
                [CodedConcept(code="code2", system="http://example.com/codesystem")],
            )


class TestCollectCodedConceptTerminology(unittest.TestCase):

    def setUp(self):
        CodedConceptTestModel.__name__ = "CodedConceptTestModel"
        CodedConceptTestModel.valueset = None
        CodedConceptTestModel.codesystem = None
        CodedConceptTestModel.objects.all().delete()

    def test_force_reset(self):
        CodedConceptTestModel.objects.create(
            code="code1", system="system1", display="display1"
        )
        collect_codedconcept_terminology(CodedConceptTestModel, force_reset=True)
        self.assertEqual(CodedConceptTestModel.objects.count(), 0)

    def test_skip_existing(self):
        CodedConceptTestModel.objects.create(
            code="code1", system="system1", display="display1"
        )
        status_before = list(CodedConceptTestModel.objects.all())
        collect_codedconcept_terminology(CodedConceptTestModel, skip_existing=True)
        status_after = list(CodedConceptTestModel.objects.all())
        self.assertEqual(status_before, status_after)

    @patch("pop.terminology.services.download_valueset")
    def test_model_based_on_valueset(self, mock_download_valueset):
        CodedConceptTestModel.valueset = "https://example.com/valueset"
        mock_download_valueset.return_value = [
            CodedConcept(code="code1", system="system1", display="display1"),
            CodedConcept(code="code2", system="system1", display="display2"),
        ]
        collect_codedconcept_terminology(CodedConceptTestModel)
        mock_download_valueset.assert_called_once_with(CodedConceptTestModel.valueset)
        self.assertEqual(CodedConceptTestModel.objects.count(), 2)
        self.assertTrue(CodedConceptTestModel.objects.filter(code="code1").exists())
        self.assertTrue(CodedConceptTestModel.objects.filter(code="code2").exists())

    @patch("pop.terminology.services.download_codesystem")
    def test_model_based_on_codesystem(self, mock_download_codesystem):
        CodedConceptTestModel.codesystem = "https://example.com/codesystem"
        mock_download_codesystem.return_value = {
            "code1": CodedConcept(code="code1", system="system1", display="display1"),
            "code2": CodedConcept(code="code2", system="system1", display="display2"),
        }
        collect_codedconcept_terminology(CodedConceptTestModel)
        mock_download_codesystem.assert_called_once_with(
            CodedConceptTestModel.codesystem
        )
        self.assertEqual(CodedConceptTestModel.objects.count(), 2)
        self.assertTrue(CodedConceptTestModel.objects.filter(code="code1").exists())
        self.assertTrue(CodedConceptTestModel.objects.filter(code="code2").exists())

    @patch("pop.terminology.services.download_valueset")
    def test_updating_existing_concepts(self, mock_download_valueset):
        CodedConceptTestModel.valueset = "https://example.com/valueset"
        CodedConceptTestModel.objects.create(
            code="code1", system="system1", display="wrong_display"
        )
        CodedConceptTestModel.objects.create(
            code="code2", system="system1", display="display2"
        )
        mock_download_valueset.return_value = [
            CodedConcept(code="code1", system="system1", display="display1"),
            CodedConcept(code="code2", system="system1", display="display2"),
        ]
        collect_codedconcept_terminology(CodedConceptTestModel)
        self.assertEqual(CodedConceptTestModel.objects.count(), 2)
        self.assertTrue(
            CodedConceptTestModel.objects.filter(display="display1").exists()
        )
        self.assertTrue(
            CodedConceptTestModel.objects.filter(display="display2").exists()
        )

    @patch("pop.terminology.services.download_valueset")
    def test_updating_concept_relationships(self, mock_download_valueset):
        CodedConceptTestModel.valueset = "https://example.com/valueset"
        CodedConceptTestModel.objects.create(
            code="code1", system="system1", display="display1"
        )
        CodedConceptTestModel.objects.create(
            code="code2", system="system1", display="display2"
        )
        mock_download_valueset.return_value = [
            CodedConcept(code="code1", system="system1", display="display1"),
            CodedConcept(
                code="code2", system="system1", display="display2", parent="code1"
            ),
        ]
        collect_codedconcept_terminology(CodedConceptTestModel)
        self.assertEqual(CodedConceptTestModel.objects.count(), 2)
        child_concept = CodedConceptTestModel.objects.get(code="code2")
        parent_concept = CodedConceptTestModel.objects.get(code="code1")
        self.assertEqual(child_concept.parent, parent_concept)

    @patch("pop.terminology.services.download_valueset")
    def test_prune_danling_concepts(self, mock_download_valueset):
        CodedConceptTestModel.valueset = "https://example.com/valueset"
        CodedConceptTestModel.objects.create(
            code="code1", system="system1", display="display1"
        )
        CodedConceptTestModel.objects.create(
            code="code2", system="system1", display="display2"
        )
        mock_download_valueset.return_value = [
            CodedConcept(code="code1", system="system1", display="display1"),
        ]
        collect_codedconcept_terminology(CodedConceptTestModel, prune_dangling=True)
        self.assertEqual(CodedConceptTestModel.objects.count(), 1)
        self.assertTrue(
            CodedConceptTestModel.objects.filter(display="display1").exists()
        )
        self.assertTrue(
            not CodedConceptTestModel.objects.filter(display="display2").exists()
        )

    @patch("pop.terminology.services.download_valueset")
    def test_disabling_writting_to_db(self, mock_download_valueset):
        CodedConceptTestModel.valueset = "https://example.com/valueset"
        mock_download_valueset.return_value = [
            CodedConcept(code="code1", system="system1", display="display1"),
            CodedConcept(code="code2", system="system1", display="display2"),
        ]
        collect_codedconcept_terminology(CodedConceptTestModel, write_db=False)
        self.assertEqual(CodedConceptTestModel.objects.count(), 0)


if __name__ == "__main__":
    unittest.main()
