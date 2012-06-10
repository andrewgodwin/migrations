import os
from django.utils import unittest
from ..loader import Loader


class LoaderTests(unittest.TestCase):
    """
    Tests the migration parser
    """

    def test_load(self):
        loader = Loader({
            "app1": os.path.join(os.path.dirname(__file__), "loader_files", "app1"),
            "app2": os.path.join(os.path.dirname(__file__), "loader_files", "app2"),
        })
        loader.load_all()
