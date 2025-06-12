import unittest
from typing import Union, Type, List, Literal, Union
from enum import Enum
from pop.core.utils import (
    is_optional,
    is_list,
    is_enum,
    is_literal,
    to_camel_case,
    average,
    std,
    percentile,
    median,
    hash_to_range,
)


class TestIsOptional(unittest.TestCase):
    def test_union_with_none(self):
        self.assertTrue(is_optional(Union[int, None]))

    def test_union_without_none(self):
        self.assertFalse(is_optional(Union[int, str]))

    def test_non_union_type(self):
        self.assertFalse(is_optional(int))

    def test_none_type(self):
        self.assertFalse(is_optional(type(None)))


class TestIsListFunction(unittest.TestCase):
    def test_list_type_returns_true(self):
        self.assertTrue(is_list(List))

    def test_non_list_type_returns_false(self):
        self.assertFalse(is_list(int))

    def test_union_type_containing_list_returns_false(self):
        self.assertFalse(is_list(Union[List, int]))

    def test_non_class_type_returns_false(self):
        self.assertFalse(is_list(5))


class TestIsEnum(unittest.TestCase):
    def test_is_enum(self):
        # Testing with an Enum type
        class MyEnum(Enum):
            VALUE1 = 1
            VALUE2 = 2

        self.assertTrue(is_enum(MyEnum))

        # Testing with a non-Enum type
        class MyClass:
            pass

        self.assertFalse(is_enum(MyClass))

        # Testing with a different type
        self.assertFalse(is_enum(int))


class TestIsLiteralFunction(unittest.TestCase):

    def test_literal_type(self):
        self.assertTrue(is_literal(Literal["a", "b"]))

    def test_non_literal_type(self):
        self.assertFalse(is_literal(int))


class TestToCamelCase(unittest.TestCase):
    def test_empty_string(self):
        self.assertEqual(to_camel_case(""), "")

    def test_single_word(self):
        self.assertEqual(to_camel_case("hello"), "hello")

    def test_multiple_words(self):
        self.assertEqual(to_camel_case("hello_world"), "helloWorld")

    def test_uppercase_letters(self):
        self.assertEqual(to_camel_case("Hello_World"), "helloWorld")

    def test_numbers(self):
        self.assertEqual(to_camel_case("hello_123"), "hello123")


class TestAverageFunction(unittest.TestCase):
    def test_average_empty_data(self):
        with self.assertRaises(ValueError):
            average([])

    def test_average_single_element_data(self):
        self.assertEqual(average([5]), 5)

    def test_average_multi_element_data_without_weights(self):
        self.assertEqual(average([1, 2, 3, 4, 5]), 3)

    def test_average_multi_element_data_with_weights(self):
        self.assertEqual(average([1, 2, 3, 4, 5], [1, 1, 1, 1, 1]), 3)
        self.assertAlmostEqual(average([1, 2, 3, 4, 5], [2, 2, 1, 1, 1]), 2.571, 3)

    def test_average_weights_of_different_lengths(self):
        with self.assertRaises(ValueError):
            average([1, 2, 3, 4, 5], [1, 1, 1, 1])

    def test_average_zero_total_weight(self):
        with self.assertRaises(ValueError):
            average([1, 2, 3, 4, 5], [0, 0, 0, 0, 0])


class TestMedianFunction(unittest.TestCase):

    def test_empty_data(self):
        with self.assertRaises(ValueError):
            median([])

    def test_single_element_data(self):
        self.assertEqual(median([5]), 5)

    def test_even_length_data(self):
        self.assertEqual(median([1, 2, 3, 4]), 2.5)

    def test_odd_length_data(self):
        self.assertEqual(median([1, 2, 3, 4, 5]), 3)

    def test_unsorted_data(self):
        self.assertEqual(median([4, 2, 1, 3]), 2.5)

    def test_data_with_duplicates(self):
        self.assertEqual(median([1, 2, 2, 3, 3, 3]), 2.5)


class TestPercentileFunction(unittest.TestCase):
    def test_empty_data(self):
        with self.assertRaises(ValueError):
            percentile([], 50)

    def test_percentile_out_of_range(self):
        with self.assertRaises(ValueError):
            percentile([1, 2, 3], -1)
        with self.assertRaises(ValueError):
            percentile([1, 2, 3], 101)

    def test_percentile_at_lower_bound(self):
        self.assertEqual(percentile([1, 2, 3], 0), 1)

    def test_percentile_at_upper_bound(self):
        self.assertEqual(percentile([1, 2, 3], 100), 3)

    def test_percentile_at_median(self):
        self.assertEqual(percentile([1, 2, 3], 50), 2)

    def test_percentile_between_bounds(self):
        self.assertAlmostEqual(percentile([1, 2, 3, 4, 5], 75), 4)


class TestStdFunction(unittest.TestCase):
    def test_population_std(self):
        data = [1, 2, 3, 4, 5]
        self.assertAlmostEqual(std(data, ddof=0), 1.4142135623730951)

    def test_sample_std(self):
        data = [1, 2, 3, 4, 5]
        self.assertAlmostEqual(std(data, ddof=1), 1.5811388300841898)

    def test_single_element_list(self):
        data = [5]
        self.assertAlmostEqual(std(data, ddof=0), 0)

    def test_empty_list(self):
        data = []
        with self.assertRaises(ValueError):
            std(data, ddof=0)

    def test_non_numeric_data(self):
        data = ["a", "b", "c"]
        with self.assertRaises(TypeError):
            std(data, ddof=0)


class TestHashToRange(unittest.TestCase):
    def test_default_range(self):
        input_str = "test_string"
        secret = "secret_key"
        result = hash_to_range(input_str, secret)
        self.assertGreaterEqual(result, -90)
        self.assertLessEqual(result, 90)

    def test_custom_range(self):
        input_str = "test_string"
        secret = "secret_key"
        low = 0
        high = 100
        result = hash_to_range(input_str, secret, low, high)
        self.assertGreaterEqual(result, low)
        self.assertLessEqual(result, high)

    def test_same_input_different_ranges(self):
        input_str = "test_string"
        secret = "secret_key"
        low1 = 0
        high1 = 100
        low2 = -50
        high2 = 50
        result1 = hash_to_range(input_str, secret, low1, high1)
        result2 = hash_to_range(input_str, secret, low2, high2)
        self.assertNotEqual(result1, result2)

    def test_different_inputs_same_secret(self):
        input_str1 = "test_string1"
        input_str2 = "test_string2"
        secret = "secret_key"
        result1 = hash_to_range(input_str1, secret)
        result2 = hash_to_range(input_str2, secret)
        self.assertNotEqual(result1, result2)

    def test_same_input_different_secrets(self):
        input_str = "test_string"
        secret1 = "secret_key1"
        secret2 = "secret_key2"
        result1 = hash_to_range(input_str, secret1)
        result2 = hash_to_range(input_str, secret2)
        self.assertNotEqual(result1, result2)

    def test_edge_cases(self):
        input_str = ""
        secret = "secret_key"
        result = hash_to_range(input_str, secret)
        self.assertGreaterEqual(result, -90)
        self.assertLessEqual(result, 90)

        input_str = "a"
        secret = "secret_key"
        result = hash_to_range(input_str, secret)
        self.assertGreaterEqual(result, -90)
        self.assertLessEqual(result, 90)

    def test_non_string_inputs(self):
        input_str = 123
        secret = "secret_key"
        with self.assertRaises(TypeError):
            hash_to_range(input_str, secret)
