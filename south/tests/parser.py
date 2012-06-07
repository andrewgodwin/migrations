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
        parser = self.get_parser("add_model.migration")
        parser.parse()
        self.assertEqual(len(parser.actions), 1)
        self.assertTrue(isinstance(parser.actions[0], CreateModel))

    def test_alter_model(self):
        parser = self.get_parser("alter_model.migration")
        parser.parse()
        self.assertEqual(len(parser.actions), 2)
        self.assertTrue(isinstance(parser.actions[0], CreateField))
        self.assertTrue(isinstance(parser.actions[1], AlterModelOption))
