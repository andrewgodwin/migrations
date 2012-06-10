"""
Actions are used to model the set of operations which migrations
request, and are responsible for changing AppState / emitting database
operations
"""

from django.db.models import AutoField
from ..state import ModelState
from .base import Action
from .fields import CreateField, DeleteField


class CreateModel(Action):
    "Action for creating a new model"

    def __init__(self, app_label, model_name):
        self.app_label = app_label
        self.model_name = model_name
        self.fields = [("id", AutoField(primary_key = True))]
        self.options = {}
        self.bases = []

    def __repr__(self):
        return "<CreateModel %s.%s (%s)>" % (
            self.app_label,
            self.model_name,
            ", ".join([n for n, d in self.fields]),
        )

    def __str__(self):
        return "Create model %s.%s" % (self.app_label, self.model_name)

    # Called by the parser as it encounters inner statements

    def set_field(self, name, instance):
        self.fields.append((name, instance))

    def set_option(self, name, value):
        self.options[name] = value

    def set_bases(self, value):
        self.bases = value

    # Final parsing check - keeps implicit ID if needed

    def final_check(self):
        "Entrypoint for a final sanity check for context-type actions"
        has_pk = False
        for name, instance in self.fields[1:]:
            if instance.primary_key:
                has_pk = True
        if has_pk:
            self.fields = self.fields[1:]

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


class AlterModel(Action):
    "Action for altering a model. Contains the actual actions."

    context_only = True

    def __init__(self, app_label, model_name):
        self.app_label = app_label
        self.model_name = model_name
        self.actions = []

    def __repr__(self):
        return "<AlterModel %s.%s>" % (
            self.app_label,
            self.model_name,
        )

    # Called by the parser as it encounters inner statements

    def set_option(self, name, value):
        self.actions.append(AlterModelOption(
            self.app_label,
            self.model_name,
            name,
            value,
        ))

    def set_bases(self, value):
        self.actions.append(AlterModelBases(
            self.app_label,
            self.model_name,
            value,
        ))

    def create_field(self, name, instance):
        self.actions.append(CreateField(
            self.app_label,
            self.model_name,
            name,
            instance,
        ))

    def delete_field(self, name):
        self.actions.append(DeleteField(
            self.app_label,
            self.model_name,
            name,
        ))


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
