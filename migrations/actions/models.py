"""
Actions are used to model the set of operations which migrations
request, and are responsible for changing AppState / emitting database
operations
"""

from django.db.models import AutoField
from ..state import ModelState
from .base import Action


class CreateModel(Action):
    "Action for creating a new model"

    def __init__(self, app_label, model_name, fields, bases, options={}):
        self.app_label = app_label
        self.model_name = model_name
        self.options = options
        self.bases = bases
        # Store fields
        self.fields = fields
        if not any([i.primary_key for n, i in fields]):
            fields.insert(0, ("id", AutoField(primary_key = True)))

    def __repr__(self):
        return "<CreateModel %s.%s (%s)>" % (
            self.app_label,
            self.model_name,
            ", ".join([n for n, d in self.fields]),
        )

    def __str__(self):
        return "Create model %s.%s" % (self.app_label, self.model_name)

    # State mutation

    def alter_state(self, project_state):
        "Alters the project state"
        project_state.models[(self.app_label, self.model_name)] = ModelState(
            project_state = project_state,
            app_label = self.app_label,
            name = self.model_name,
            fields = self.fields,
            options = self.options,
            bases = self.bases,
        )

    def alter_database(self, from_state, to_state, database, forwards):
        "Creates the model"
        if forwards:
            print "CALLING 'CREATE TABLE' with %s" % to_state.models[self.app_label, self.model_name].render()
        else:
            print "CALLING 'DROP TABLE' with %s" % to_state.models[self.app_label, self.model_name].render()


class DeleteModel(Action):
    "Action for deleting a model"

    def __init__(self, app_label, model_name):
        self.app_label = app_label
        self.model_name = model_name

    def alter_state(self, project_state):
        "Alters the project state"
        del project_state.models[(self.app_label, self.model_name)]


class AlterModelOption(Action):
    "Represents a change to a model option"

    def __init__(self, app_label, model_name, name, value):
        self.app_label = app_label
        self.model_name = model_name
        self.name = name
        self.value = value

    def __repr__(self):
        return "<AlterModelOption %s.%s %s=%s>" % (
            self.app_label,
            self.model_name,
            self.name,
            self.value,
        )

    def alter_state(self, project_state):
        "Alters the project state"
        project_state.models[(self.app_label, self.model_name)].options[self.name] = self.value


class AlterModelBases(Action):
    "Represents a change to a model's bases"

    def __init__(self, app_label, model_name, value):
        self.app_label = app_label
        self.model_name = model_name
        self.value = value

    def __repr__(self):
        return "<AlterModelBases %s.%s %s>" % (
            self.app_label,
            self.model_name,
            self.value,
        )

    def alter_state(self, project_state):
        "Alters the project state"
        project_state.models[(self.app_label, self.model_name)].bases = self.value
