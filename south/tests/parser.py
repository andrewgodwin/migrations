import os
from django.utils import unittest
from ..parser import MigrationParser
from ..actions import CreateModel, CreateField, AlterModelOption


class ParserTests(unittest.TestCase):
    """
    Tests the migration parser
    """

    files_root = os.path.join(os.path.dirname(__file__), "parser_files")

    def get_parser(self, filename):
        "Assembles a parser for the test file 'filename'"
        return MigrationParser("fake_app", os.path.join(self.files_root, filename))

    def test_create_model(self):
        # First, test we get an implicit ID field
        parser = self.get_parser("create_model.migration")
        parser.parse()
        self.assertEqual(len(parser.actions), 1)
        self.assertTrue(isinstance(parser.actions[0], CreateModel))
        self.assertEqual(parser.actions[0].fields[0][0], "id")
        # Then, make sure it goes away with an explicit PK
        parser = self.get_parser("create_model_with_pk.migration")
        parser.parse()
        self.assertEqual(parser.actions[0].fields[0][0], "identifier")

    def test_bad_create_model(self):
        parser = self.get_parser("bad_create_model.migration")
        self.assertRaises(
            SyntaxError,
            parser.parse,
        )

    def test_alter_model(self):
        parser = self.get_parser("alter_model.migration")
        parser.parse()
        self.assertEqual(len(parser.actions), 2)
        self.assertTrue(isinstance(parser.actions[0], CreateField))
        self.assertTrue(isinstance(parser.actions[1], AlterModelOption))

    def test_bad_alter_model(self):
        parser = self.get_parser("bad_alter_model.migration")
        self.assertRaises(
            SyntaxError,
            parser.parse,
        )

    def test_bad_indenting(self):
        parser = self.get_parser("bad_initial_indent.migration")
        self.assertRaises(
            SyntaxError,
            parser.parse,
        )
        parser = self.get_parser("bad_middle_indent.migration")
        self.assertRaises(
            SyntaxError,
            parser.parse,
        )
