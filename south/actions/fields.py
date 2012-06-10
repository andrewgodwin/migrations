"""
Actions are used to model the set of operations which migrations
request, and are responsible for changing AppState / emitting database
operations
"""

from .base import Action


class CreateField(Action):
    "Represents a field being added to an existing model"

    def __init__(self, app_label, model_name, name, instance):
        self.app_label = app_label
        self.model_name = model_name
        self.name = name
        self.instance = instance

    def __repr__(self):
        return "<CreateField %s.%s %s>" % (
            self.app_label,
            self.model_name,
            self.name,
        )

    def __str__(self):
        return "Create field %s on %s.%s" % (self.name, self.app_label, self.model_name)

    def alter_state(self, project_state):
        "Alters the project state"
        project_state.models[(self.app_label, self.model_name)].fields.append(
            (self.name, self.instance),
        )

    def alter_database(self, from_state, to_state, database, forwards):
        "Creates the field (column or table)"
        pass


class DeleteField(Action):
    "Represents a field being removed from an existing model"

    def __init__(self, app_label, model_name, name):
        self.app_label = app_label
        self.model_name = model_name
        self.name = name

    def __repr__(self):
        return "<DeleteField %s.%s %s>" % (
            self.app_label,
            self.model_name,
            self.name,
        )

    def __str__(self):
        return "Delete field %s from %s.%s" % (self.name, self.app_label, self.model_name)

    def alter_state(self, project_state):
        "Alters the project state"
        model_state = project_state.models[(self.app_label, self.model_name)]
        model_state.fields = [
            (name, field)
            for name, field in model_state.fields
            if name != self.name
        ]

    def alter_database(self, from_state, to_state, database, forwards):
        "Creates the field (column or table)"
        pass
