"""
Actions are used to model the set of operations which migrations
request. They are not themselves responsible for actually making
any changes - they're just a representation.
"""

from django.db.models import AutoField
from .parser.option import parse_field_definition, parse_option_definition


class Action(object):
    "Base class for actions"

    # If this is True, the action only exists temporarily for parsing
    # and is replaced by self.actions once parsing is complete.
    context_only = False

    def final_check(self):
        "Entrypoint for a final sanity check for context-type actions"
        pass


class CreateModel(Action):
    "Action for creating a new model"

    def __init__(self, app_label, model_name):
        self.app_label = app_label
        self.model_name = model_name
        self.fields = [("id", AutoField(primary_key = True))]
        self.options = {}
        self.bases = []

    def set_field(self, name, definition):
        instance = parse_field_definition(definition)
        self.fields.append((name, instance))

    def set_option(self, name, definition):
        self.options[name] = parse_option_definition(definition)

    def set_bases(self, definition):
        self.bases = definition

    def __repr__(self):
        return "<CreateModel %s.%s (%s)>" % (
            self.app_label,
            self.model_name,
            ", ".join([n for n, d in self.fields]),
        )

    def final_check(self):
        has_pk = False
        for name, instance in self.fields[1:]:
            if instance.primary_key:
                has_pk = True
        if has_pk:
            self.fields = self.fields[1:]


class AlterModel(Action):
    "Action for altering a model. Contains the actual actions."

    context_only = True

    def __init__(self, app_label, model_name):
        self.app_label = app_label
        self.model_name = model_name
        self.actions = []

    def set_option(self, name, definition):
        self.actions.append(AlterModelOption(
            self.app_label,
            self.model_name,
            name,
            definition,
        ))

    def set_bases(self, definition):
        self.actions.append(AlterModelBases(
            self.app_label,
            self.model_name,
            definition,
        ))

    def create_field(self, name, definition):
        self.actions.append(CreateField(
            self.app_label,
            self.model_name,
            name,
            definition,
        ))

    def delete_field(self, name):
        self.actions.append(DeleteField(
            self.app_label,
            self.model_name,
            name,
        ))

    def __repr__(self):
        return "<AlterModel %s.%s>" % (
            self.app_label,
            self.model_name,
        )


class AlterModelOption(Action):
    "Represents a change to a model option"

    def __init__(self, app_label, model_name, name, definition):
        self.app_label = app_label
        self.model_name = model_name
        self.name = name
        self.definition = parse_option_definition(definition)

    def __repr__(self):
        return "<AlterModelOption %s.%s %s=%s>" % (
            self.app_label,
            self.model_name,
            self.name,
            self.definition,
        )


class AlterModelBases(Action):
    "Represents a change to a model's bases"

    def __init__(self, app_label, model_name, definition):
        self.app_label = app_label
        self.model_name = model_name
        self.definition = definition

    def __repr__(self):
        return "<AlterModelBases %s.%s %s>" % (
            self.app_label,
            self.model_name,
            self.definition,
        )


class CreateField(Action):
    "Represents a field being added to an existing model"

    def __init__(self, app_label, model_name, name, definition):
        self.app_label = app_label
        self.model_name = model_name
        self.name = name
        self.definition = definition

    def __repr__(self):
        return "<CreateField %s.%s %s>" % (
            self.app_label,
            self.model_name,
            self.name,
        )


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
