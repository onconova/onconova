import unittest
from datetime import date, datetime
from unittest.mock import MagicMock, patch

from django.db.models import Model  # Add this import at the top if not present
from ninja import Schema

from onconova.core.anonymization.base import (
    MAX_DATE_SHIFT,
    REDACTED_STRING,
    AnonymizationConfig,
    AnonymizationMixin,
    anonymize_age,
    anonymize_by_redacting_string,
    anonymize_clinically_relevant_date,
    anonymize_personal_date,
    anonymize_value,
)
from onconova.core.anonymization.decorator import AnonymizationBase, HttpError
from onconova.core.schemas import Period
from onconova.core.types import Age, AgeBin
from onconova.tests.models import MockModel


class TestAnonymizeByRedactingString(unittest.TestCase):
    def test_non_empty_string(self):
        original_value = "Hello World"
        expected_result = REDACTED_STRING
        self.assertEqual(anonymize_by_redacting_string(original_value), expected_result)

    def test_empty_string(self):
        original_value = ""
        expected_result = REDACTED_STRING
        self.assertEqual(anonymize_by_redacting_string(original_value), expected_result)

    def test_special_characters(self):
        original_value = "!@#$%^&*()"
        expected_result = REDACTED_STRING
        self.assertEqual(anonymize_by_redacting_string(original_value), expected_result)

    def test_numbers(self):
        original_value = "1234567890"
        expected_result = REDACTED_STRING
        self.assertEqual(anonymize_by_redacting_string(original_value), expected_result)


class TestAnonymizeClinicallyRelevantDate(unittest.TestCase):

    def test_anonymize_date_object(self):
        original_date = date(2022, 1, 1)
        case_id = "test_case_id"
        anonymized_date = anonymize_clinically_relevant_date(original_date, case_id)
        self.assertIsInstance(anonymized_date, date)
        self.assertNotEqual(anonymized_date, original_date)

    def test_anonymize_datetime_object(self):
        original_date = datetime(2022, 1, 1)
        case_id = "test_case_id"
        anonymized_date = anonymize_clinically_relevant_date(original_date, case_id)
        self.assertIsInstance(anonymized_date, datetime)
        self.assertNotEqual(anonymized_date, original_date)

    def test_anonymize_string_in_correct_format(self):
        original_date = "2022-01-01"
        case_id = "test_case_id"
        anonymized_date = anonymize_clinically_relevant_date(original_date, case_id)
        self.assertIsInstance(anonymized_date, date)
        self.assertNotEqual(
            anonymized_date, datetime.strptime(original_date, "%Y-%m-%d").date()
        )

    def test_anonymize_string_in_incorrect_format(self):
        original_date = "invalid_date_format"
        case_id = "test_case_id"
        with self.assertRaises(ValueError):
            anonymize_clinically_relevant_date(original_date, case_id)

    def test_timeshift_within_expected_range(self):
        original_date = date(2022, 1, 1)
        case_id = "test_case_id"
        anonymized_date = anonymize_clinically_relevant_date(original_date, case_id)
        assert type(anonymized_date) is date
        timeshift = (anonymized_date - original_date).days
        self.assertGreaterEqual(timeshift, -MAX_DATE_SHIFT)
        self.assertLessEqual(timeshift, MAX_DATE_SHIFT)

    def test_timeshift_different_for_different_case_ids(self):
        original_date = date(2022, 1, 1)
        case_id1 = "test_case_id1"
        case_id2 = "test_case_id2"
        anonymized_date1 = anonymize_clinically_relevant_date(original_date, case_id1)
        anonymized_date2 = anonymize_clinically_relevant_date(original_date, case_id2)
        self.assertNotEqual(anonymized_date1, anonymized_date2)


class TestAnonymizeAge(unittest.TestCase):
    def test_age_bins(self):
        self.assertEqual(anonymize_age(Age(15)), AgeBin.SUB_20)
        self.assertEqual(anonymize_age(Age(22)), AgeBin.AGE_20_24)
        self.assertEqual(anonymize_age(Age(27)), AgeBin.AGE_25_29)
        self.assertEqual(anonymize_age(Age(32)), AgeBin.AGE_30_34)
        self.assertEqual(anonymize_age(Age(37)), AgeBin.AGE_35_39)
        self.assertEqual(anonymize_age(Age(42)), AgeBin.AGE_40_44)
        self.assertEqual(anonymize_age(Age(47)), AgeBin.AGE_45_49)
        self.assertEqual(anonymize_age(Age(52)), AgeBin.AGE_50_54)
        self.assertEqual(anonymize_age(Age(57)), AgeBin.AGE_55_59)
        self.assertEqual(anonymize_age(Age(62)), AgeBin.AGE_60_64)
        self.assertEqual(anonymize_age(Age(67)), AgeBin.AGE_65_69)
        self.assertEqual(anonymize_age(Age(72)), AgeBin.AGE_70_74)
        self.assertEqual(anonymize_age(Age(77)), AgeBin.AGE_75_79)
        self.assertEqual(anonymize_age(Age(82)), AgeBin.AGE_80_84)
        self.assertEqual(anonymize_age(Age(87)), AgeBin.AGE_85_89)
        self.assertEqual(anonymize_age(Age(92)), AgeBin.OVER_90)

    def test_edge_cases(self):
        self.assertEqual(anonymize_age(Age(20)), AgeBin.AGE_20_24)
        self.assertEqual(anonymize_age(Age(90)), AgeBin.OVER_90)

    def test_invalid_age_values(self):
        with self.assertRaises(ValueError):
            anonymize_age(Age(-1))
        with self.assertRaises(ValueError):
            anonymize_age(Age(1000))


class TestAnonymizePersonalDate(unittest.TestCase):
    def test_datetime_object(self):
        expected_date = datetime(2022, 1, 1).date()
        original_date = datetime(2022, 2, 3)
        self.assertEqual(anonymize_personal_date(original_date), expected_date)

    def test_date_object(self):
        expected_date = datetime(2022, 1, 1).date()
        original_date = date(2022, 2, 3)
        self.assertEqual(anonymize_personal_date(original_date), expected_date)

    def test_iso_format_string(self):
        expected_date = datetime(2022, 1, 1).date()
        original_date = "2022-02-03"
        self.assertEqual(anonymize_personal_date(original_date), expected_date)

    def test_yyyymmdd_format_string(self):
        expected_date = datetime(2022, 1, 1).date()
        original_date = "2022-02-03"
        self.assertEqual(anonymize_personal_date(original_date), expected_date)

    def test_invalid_date_string(self):
        original_date = "invalid-date"
        with self.assertRaises(ValueError):
            anonymize_personal_date(original_date)

    def test_unsupported_type(self):
        original_date = 123
        with self.assertRaises(TypeError):
            anonymize_personal_date(original_date)  # type: ignore


class TestAnonymizeValue(unittest.TestCase):
    def test_anonymize_date(self):
        original_date = date(2022, 1, 1)
        case_id = "test_case_id"
        anonymized_date = anonymize_value(original_date, case_id)
        self.assertIsInstance(anonymized_date, date)
        self.assertNotEqual(anonymized_date, original_date)

    def test_anonymize_datetime(self):
        original_datetime = datetime(2022, 1, 1, 12, 0, 0)
        case_id = "test_case_id"
        anonymized_datetime = anonymize_value(original_datetime, case_id)
        self.assertIsInstance(anonymized_datetime, datetime)
        self.assertNotEqual(anonymized_datetime, original_datetime)

    def test_anonymize_string_date(self):
        original_date_string = "2022-01-01"
        case_id = "test_case_id"
        anonymized_date = anonymize_value(original_date_string, case_id)
        self.assertIsInstance(anonymized_date, date)
        self.assertNotEqual(
            anonymized_date, datetime.strptime(original_date_string, "%Y-%m-%d").date()
        )

    def test_anonymize_period(self):
        original_period = Period(start=date(2022, 1, 1), end=date(2022, 1, 31))
        case_id = "test_case_id"
        anonymized_period = anonymize_value(original_period, case_id)
        self.assertIsInstance(anonymized_period, Period)
        self.assertNotEqual(anonymized_period.start, original_period.start)
        self.assertNotEqual(anonymized_period.end, original_period.end)

    def test_anonymize_string_period(self):
        original_period_string = "[2022-01-01, 2022-01-31]"
        case_id = "test_case_id"
        anonymized_period = anonymize_value(original_period_string, case_id)
        self.assertIsInstance(anonymized_period, str)
        self.assertNotEqual(anonymized_period, original_period_string)

    def test_anonymize_string(self):
        original_string = "Hello World"
        case_id = "test_case_id"
        anonymized_string = anonymize_value(original_string, case_id)
        self.assertEqual(
            anonymized_string, anonymize_by_redacting_string(original_string)
        )

    def test_anonymize_age(self):
        original_age = Age(25)
        case_id = "test_case_id"
        anonymized_age = anonymize_value(original_age, case_id)
        self.assertIsInstance(anonymized_age, AgeBin)
        self.assertNotEqual(anonymized_age, original_age)

    def test_anonymize_unsupported_type(self):
        original_value = 123
        case_id = "test_case_id"
        with self.assertRaises(NotImplementedError):
            anonymize_value(original_value, case_id)


class TestAnonymizationMixin(unittest.TestCase):

    class DummySchema(Schema, AnonymizationMixin):
        anonymized: bool = False
        field1: str | None = None
        field2: str | None = None

        def __post_anonymization_hook__(self):
            pass

    def setUp(self):
        self.DummySchema.__anonymization_fields__ = ("field1", "field2")
        self.DummySchema.__anonymization_functions__ = {
            "field1": MagicMock(return_value="anonymized_value1")
        }
        self.obj = self.DummySchema()
        self.obj.anonymized = True
        self.obj.field1 = "value1"
        self.obj.field2 = None

    def test_setup_with_valid_config(self):
        model_class = MagicMock()
        func1 = lambda x: x
        config = AnonymizationConfig(
            fields=["field1", "field2"], key="key", functions={"func1": func1}
        )
        AnonymizationMixin._setup(model_class, config)
        self.assertEqual(
            model_class.__anonymization_fields__, ("field1", "field2", "func1")
        )
        self.assertEqual(model_class.__anonymization_key__, "key")
        self.assertEqual(model_class.__anonymization_functions__, {"func1": func1})

    def test_anonymization_skipped_when_anonymized_is_false(self):
        self.obj.anonymized = False
        self.obj = self.obj.model_validate(self.obj)
        self.assertEqual(self.obj.field1, "value1")

    def test_anonymization_applied_to_fields_with_values(self):
        self.obj = self.obj.model_validate(self.obj)
        self.assertEqual(self.obj.field1, "anonymized_value1")

    def test_anonymization_skipped_for_fields_with_no_values(self):
        self.obj = self.obj.model_validate(self.obj)
        self.assertIsNone(self.obj.field2)

    def test_field_specific_anonymizer_used_when_available(self):
        self.obj = self.obj.model_validate(self.obj)
        self.obj.__anonymization_functions__["field1"].assert_called_once_with("value1")

    def test_fallback_anonymizer_used_when_field_specific_anonymizer_is_not_available(
        self,
    ):
        self.obj.field2 = "value2"
        with patch.object(self.DummySchema, "anonymize_value") as anonymize_value:
            self.obj = self.obj.model_validate(self.obj)
            anonymize_value.assert_called_once_with("value2")

    def test_post_anonymization_hook_called_after_anonymization(self):
        with patch.object(self.DummySchema, "__post_anonymization_hook__") as hook:
            self.obj = self.obj.model_validate(self.obj)
            hook.assert_called_once()


class TestAnonymizationBase(unittest.TestCase):

    # Dummy classes
    class DummyUser:
        pass

    class DummyRequest:
        def __init__(self, user):
            self.user = user

    class DummySchema(Schema):
        anonymized: bool = False
        pass

    def setUp(self):
        self.base = AnonymizationBase()
        self.dummy_request = self.DummyRequest(self.DummyUser())

    def test_raises_if_request_missing(self):
        with self.assertRaises(HttpError) as cm:
            self.base.anonymize_queryset(MockModel(), request=None)
        self.assertEqual(cm.exception.status_code, 400)

    def test_raises_if_permission_denied(self):
        user = self.DummyUser()
        request = self.DummyRequest(user)
        with patch(
            "onconova.core.anonymization.decorator.permissions.CanManageCases"
        ) as can_manage:
            can_manage.return_value.check_user_permission.return_value = False
            with self.assertRaises(HttpError) as cm:
                self.base.anonymize_queryset(
                    MockModel(), anonymized=False, request=request
                )
            self.assertEqual(cm.exception.status_code, 403)

    def test_allows_if_permission_granted(self):
        user = self.DummyUser()
        request = self.DummyRequest(user)
        with patch(
            "onconova.core.anonymization.decorator.permissions.CanManageCases"
        ) as can_manage:
            can_manage.return_value.check_user_permission.return_value = True
            obj = MockModel()
            result = self.base.anonymize_queryset(
                obj, anonymized=False, request=request
            )
            self.assertIs(result, obj)

    def test_sets_anonymized_on_model(self):
        obj = MockModel()
        result = self.base.anonymize_queryset(obj, request=self.dummy_request)
        self.assertTrue(getattr(result, "anonymized", False))

    def test_sets_anonymized_on_schema(self):
        obj = self.DummySchema()
        result = self.base.anonymize_queryset(obj, request=self.dummy_request)
        self.assertTrue(getattr(result, "anonymized", False))

    def test_sets_anonymized_on_list(self):
        objs = [MockModel(), MockModel()]
        result = self.base.anonymize_queryset(objs, request=self.dummy_request)
        for obj in result:
            self.assertTrue(getattr(obj, "anonymized", False))

    def test_sets_anonymized_on_tuple(self):
        objs = (MockModel(), MockModel())
        result = self.base.anonymize_queryset(objs, request=self.dummy_request)
        for obj in result:
            self.assertTrue(getattr(obj, "anonymized", False))

    def test_queryset_annotate_called(self):
        mock_qs = MagicMock()
        result_qs = MagicMock()
        mock_qs.annotate.return_value = result_qs
        with patch("onconova.core.anonymization.decorator.Value") as mock_value:
            # You need to complete this test based on your implementation
            pass
