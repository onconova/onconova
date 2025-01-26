import unittest
from typing import Union, Type, List, Literal, Union
from enum import Enum
from pop.core.utils import is_optional, is_list, is_enum, is_literal, to_camel_case

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
        self.assertTrue(is_literal(Literal['a', 'b']))

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

if __name__ == '__main__':
    unittest.main()