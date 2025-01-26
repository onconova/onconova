import os
import unittest
import requests
from io import StringIO
from unittest.mock import patch, MagicMock, PropertyMock
from pop.terminology.utils import parent_to_children, _cache, CodedConcept, get_dictreader_and_size, \
            parse_OBO_file, get_file_location, ensure_within_string_limits, ensure_list, request_http_get

class TestParentToChildren(unittest.TestCase):
    def setUp(self):
        _cache.clear()

    def test_empty_codesystem(self):
        codesystem = {}
        result = parent_to_children(codesystem)
        self.assertEqual(result, {})

    def test_single_concept_no_parent(self):
        concept = CodedConcept(code='code1', parent=None)
        codesystem = {'concept1': concept}
        result = parent_to_children(codesystem)
        self.assertEqual(result, {None: [concept]})

    def test_multiple_concepts_same_parent(self):
        parent = 'parent1'
        concept1 = CodedConcept(code='code1', parent=parent)
        concept2 = CodedConcept(code='code2', parent=parent)
        codesystem = {'concept1': concept1, 'concept2': concept2}
        result = parent_to_children(codesystem)
        self.assertEqual(result, {parent: [concept1, concept2]})

    def test_concepts_different_parents(self):
        parent1 = 'parent1'
        parent2 = 'parent2'
        concept1 = CodedConcept(code='code1', parent=parent1)
        concept2 = CodedConcept(code='code2', parent=parent2)
        codesystem = {'concept1': concept1, 'concept2': concept2}
        result = parent_to_children(codesystem)
        self.assertEqual(result, {parent1: [concept1], parent2: [concept2]})

    def test_caching_same_codesystem(self):
        codesystem = {'concept1': CodedConcept(code='code1', parent='parent1')}
        result1 = parent_to_children(codesystem)
        result2 = parent_to_children(codesystem)
        self.assertEqual(result1, result2)
        self.assertEqual(id(result1), id(result2))

    def test_caching_different_codesystems(self):
        codesystem1 = {'concept1': CodedConcept(code='code1', parent='parent1')}
        codesystem2 = {'concept2': CodedConcept(code='code2', parent='parent2')}
        result1 = parent_to_children(codesystem1)
        result2 = parent_to_children(codesystem2)
        self.assertNotEqual(result1, result2)
        self.assertNotEqual(id(result1), id(result2))



class TestParseOBOFile(unittest.TestCase):
    def test_multiple_terms(self):
        file_contents = """
        [Term]
        id: GO:000001
        name: mitochondrion
        [Term]
        id: GO:000002
        name: nucleus
        """
        file = StringIO(file_contents)
        terms = list(parse_OBO_file(file))
        self.assertEqual(len(terms), 2)
        self.assertEqual(terms[0]['id'], 'GO:000001')
        self.assertEqual(terms[0]['name'], 'mitochondrion')
        self.assertEqual(terms[1]['id'], 'GO:000002')
        self.assertEqual(terms[1]['name'], 'nucleus')

    def test_single_term(self):
        file_contents = """
        [Term]
        id: GO:000001
        name: mitochondrion
        """
        file = StringIO(file_contents)
        terms = list(parse_OBO_file(file))
        self.assertEqual(len(terms), 1)
        self.assertEqual(terms[0]['id'], 'GO:000001')
        self.assertEqual(terms[0]['name'], 'mitochondrion')

    def test_no_terms(self):
        file_contents = ""
        file = StringIO(file_contents)
        terms = list(parse_OBO_file(file))
        self.assertEqual(len(terms), 0)

    def test_empty_line(self):
        file_contents = """
        [Term]
        id: GO:000001
        name: mitochondrion

        """
        file = StringIO(file_contents)
        terms = list(parse_OBO_file(file))
        self.assertEqual(len(terms), 1)
        self.assertEqual(terms[0]['id'], 'GO:000001')
        self.assertEqual(terms[0]['name'], 'mitochondrion')

class TestGetFileLocation(unittest.TestCase):

    @patch('os.listdir')
    @patch('os.path.isfile')
    def test_file_found(self, mock_isfile, mock_listdir):
        mock_listdir.return_value = ['file1.txt', 'file2.txt']
        mock_isfile.return_value = True
        path = 'test_path'
        filepart = 'file1'
        expected_result = os.path.join('test_path', 'file1.txt')
        result = get_file_location(path, filepart)
        self.assertEqual(result, expected_result)

    @patch('os.listdir')
    @patch('os.path.isfile')
    def test_file_not_found(self, mock_isfile, mock_listdir):
        mock_listdir.return_value = ['file1.txt', 'file2.txt']
        mock_isfile.return_value = True
        path = 'test_path'
        filepart = 'file3'
        with self.assertRaises(FileNotFoundError):
            get_file_location(path, filepart)

    @patch('os.listdir')
    @patch('os.path.isfile')
    def test_multiple_files(self, mock_isfile, mock_listdir):
        mock_listdir.return_value = ['file1.txt', 'file2.txt', 'file3.txt']
        mock_isfile.return_value = True
        path = 'test_path'
        filepart = 'file1'
        expected_result = os.path.join('test_path', 'file1.txt')
        result = get_file_location(path, filepart)
        self.assertEqual(result, expected_result)

    @patch('os.listdir')
    @patch('os.path.isfile')
    def test_multiple_files_not_found(self, mock_isfile, mock_listdir):
        mock_listdir.return_value = ['file1.txt', 'file2.txt', 'file3.txt']
        mock_isfile.return_value = True
        path = 'test_path'
        filepart = 'file4'
        with self.assertRaises(FileNotFoundError):
            get_file_location(path, filepart)

    @patch('os.listdir')
    @patch('os.path.isfile')
    def test_filepart_as_substring(self, mock_isfile, mock_listdir):
        mock_listdir.return_value = ['file1.txt', 'file2.txt']
        mock_isfile.return_value = True
        path = 'test_path'
        filepart = 'file'
        expected_result = os.path.join('test_path', 'file1.txt')
        result = get_file_location(path, filepart)
        self.assertEqual(result, expected_result)

    @patch('os.listdir')
    @patch('os.path.isfile')
    def test_filepart_as_substring_not_found(self, mock_isfile, mock_listdir):
        mock_listdir.return_value = ['file1.txt', 'file2.txt']
        mock_isfile.return_value = True
        path = 'test_path'
        filepart = 'test'
        with self.assertRaises(FileNotFoundError):
            get_file_location(path, filepart)


class TestEnsureWithinStringLimits(unittest.TestCase):
    def test_string_within_limit(self):
        input_string = "a" * 1999
        expected_output = input_string
        self.assertEqual(ensure_within_string_limits(input_string), expected_output)

    def test_string_above_limit(self):
        input_string = "a" * 2001
        expected_output = "a" * 2000
        self.assertEqual(ensure_within_string_limits(input_string), expected_output)

    def test_empty_string(self):
        input_string = ""
        expected_output = ""
        self.assertEqual(ensure_within_string_limits(input_string), expected_output)

    def test_none_input(self):
        input_string = None
        with self.assertRaises(TypeError):
            ensure_within_string_limits(input_string)


class TestEnsureListFunction(unittest.TestCase):

    def test_single_non_list_value(self):
        self.assertEqual(ensure_list(5), [5])

    def test_existing_list(self):
        self.assertEqual(ensure_list([1, 2, 3]), [1, 2, 3])

    def test_none_value(self):
        self.assertEqual(ensure_list(None), [None])

    def test_list_with_multiple_values(self):
        self.assertEqual(ensure_list([1, 2, 3, 4, 5]), [1, 2, 3, 4, 5])

class TestGetDictReaderAndSize(unittest.TestCase):

    class NamedStringIO(StringIO):
        def __init__(self, content: str, name: str):
            super().__init__(content)
            self.name = name

    def test_csv_with_header(self):
        file_content = """Name,Age
        John,30
        Alice,25
        """
        file = self.NamedStringIO(file_content, name='test.csv')
        reader, total = get_dictreader_and_size(file)
        self.assertEqual(total, 2)

    def test_csv_without_header(self):
        file_content = """John,30
        Alice,25
        """
        file = self.NamedStringIO(file_content, name='test.csv')
        reader, total = get_dictreader_and_size(file, has_header=False)
        self.assertEqual(total, 2)

    def test_tsv_with_header(self):
        file_content = """Name\tAge
        John\t30
        Alice\t25
        """
        file = self.NamedStringIO(file_content, name='test.tsv')
        reader, total = get_dictreader_and_size(file)
        self.assertEqual(total, 2)

    def test_tsv_without_header(self):
        file_content = """John\t30
        Alice\t25
        """
        file = self.NamedStringIO(file_content, name='test.tsv')
        reader, total = get_dictreader_and_size(file, has_header=False)
        self.assertEqual(total, 2)

    def test_obo_file(self):
        file_content = "[Term]\r\nid: GO:000001\r\nname: mitochondrion inheritance\r\n[Term]\r\nid: GO:000002\r\nname: endoplasmic reticulum inheritance"
        file = self.NamedStringIO(file_content, name='test.obo')
        reader, total = get_dictreader_and_size(file)
        self.assertEqual(total, 2)

    def test_non_csv_tsv_obo_file(self):
        file_content = "This is not a CSV, TSV, or OBO file"
        file = self.NamedStringIO(file_content, name='test.txt')
        with self.assertRaises(ValueError):
            get_dictreader_and_size(file)

    @patch('builtins.print')
    def test_verbose_mode_off(self, mock_print):
        file_content = "Name,Age\r\nJohn,30\r\nAlice,25"
        file = self.NamedStringIO(file_content, name='test.csv')
        get_dictreader_and_size(file, verbose=False)
        mock_print.assert_not_called()


if __name__ == '__main__':
    unittest.main()