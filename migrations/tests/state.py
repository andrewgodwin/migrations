from django.utils import unittest
from django.db import models
from ..state import ProjectState, ModelState


class StateTests(unittest.TestCase):
    """
    Tests the rendering of ModelStates into models
    """

    def test_render_simple(self):
        "Tests a simple model"
        project_state = ProjectState()
        model_state = ModelState(
            project_state = project_state,
            app_label = "app0",
            name = "SimpleModel",
            fields = [
                ("id", models.AutoField(primary_key=True)),
                ("name", models.CharField(max_length=255)),
                ("when", models.DateTimeField()),
            ],
        )
        model = model_state.render()
        self.assertEqual(model.__name__, "SimpleModel")
        self.assertEqual(model._meta.app_label, "app0")
        self.assertEqual(len(model._meta.fields), 3)
        self.assertEqual(model._meta.fields[1].max_length, 255)
