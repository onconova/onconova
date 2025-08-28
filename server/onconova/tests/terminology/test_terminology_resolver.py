import unittest
from unittest.mock import patch

from onconova.terminology.resolver import CanonicalUrlResolver


class TestCanonicalUrlResolver(unittest.TestCase):

    def setUp(self):
        self.resolver = CanonicalUrlResolver()

    def test_resolve_with_valid_loinc_url(self):
        canonical_url = "http://loinc.org/123"
        expected_url = "http://fhir.loinc.org/ValueSet/$expand?url=http://loinc.org/123&_format=json"
        with patch.object(
            self.resolver, "resolve_LOINC_endpoint", return_value=expected_url
        ) as mock_resolve:
            result = self.resolver.resolve(canonical_url)
            self.assertEqual(result, expected_url)
            mock_resolve.assert_called_once_with(canonical_url)

    def test_resolve_with_valid_hl7_url(self):
        canonical_url = "http://hl7.org/fhir/us/core/ValueSet/123"
        expected_url = "http://hl7.org/fhir/us/core/ValueSet/$expand?url=http://hl7.org/fhir/us/core/ValueSet/123&_format=json"
        with patch.object(
            self.resolver, "resolve_HL7_endpoint", return_value=expected_url
        ) as mock_resolve:
            result = self.resolver.resolve(canonical_url)
            self.assertEqual(result, expected_url)
            mock_resolve.assert_called_once_with(canonical_url)

    def test_resolve_with_valid_vsac_url(self):
        canonical_url = "https://vsac.nlm.nih.gov/valueset/123"
        expected_url = (
            "https://cts.nlm.nih.gov/fhir/res/ValueSet/123/$expand?_format=json"
        )
        with patch.object(
            self.resolver, "resolve_VSAC_endpoint", return_value=expected_url
        ) as mock_resolve:
            result = self.resolver.resolve(canonical_url)
            self.assertEqual(result, expected_url)
            mock_resolve.assert_called_once_with(canonical_url)

    def test_resolve_with_valid_cts_url(self):
        canonical_url = "https://cts.nlm.nih.gov/fhir/ValueSet/123"
        expected_url = "https://cts.nlm.nih.gov/fhir/ValueSet/123/$expand?_format=json"
        with patch.object(
            self.resolver, "resolve_CTS_endpoint", return_value=expected_url
        ) as mock_resolve:
            result = self.resolver.resolve(canonical_url)
            self.assertEqual(result, expected_url)
            mock_resolve.assert_called_once_with(canonical_url)

    def test_resolve_with_valid_simplifier_url(self):
        canonical_url = "https://simplifier.net/onconova/ValueSets/123"
        expected_url = (
            "https://simplifier.net/onconova/ValueSets/123/$download?format=json"
        )
        with patch.object(
            self.resolver, "resolve_Simplifier_endpoint", return_value=expected_url
        ) as mock_resolve:
            result = self.resolver.resolve(canonical_url)
            self.assertEqual(result, expected_url)
            mock_resolve.assert_called_once_with(canonical_url)

    def test_resolve_with_invalid_url(self):
        canonical_url = "http://example.com/fhir/us/core/ValueSet/123"
        with self.assertRaises(KeyError):
            self.resolver.resolve(canonical_url)


if __name__ == "__main__":
    unittest.main
    unittest.main
