"""
The user-exposed API of migrations. This is technically api_v1 - the reason it
is separate to the core classes is so that in future it's possible to move to
a v2 of this API.
"""

from django.utils.importlib import import_module
import actions


class BaseMigration(object):
    "Base migration class"

    dependencies = []
    actions = []


class Action(object):
    "Base class for all actions"
    
    def render(self, app_label):
        raise NotImplementedError()

## Field definition ##

def Field(path, args, kwargs):
    "Creates fields from textual definitions"
    field_module, field_class = path.rsplit(".", 1)
    field_module = import_module(field_module)
    return getattr(field_module, field_class)(*args, **kwargs)

## Model-level ##

class CreateModel(Action):
    "Creation of models"

    def __init__(self, name, fields, bases=None, options={}):
        self.name = name
        self.fields = fields
        self.bases = bases or ["django.db.models.base.Model"]
        self.options = options

    def render(self, app_label):
        return actions.CreateModel(
            app_label = app_label,
            model_name = self.name,
            fields = self.fields,
            bases = self.bases,
            options = self.options,
        )


class CreateField(Action):
    "Creation of models"

    def __init__(self, model_name, name, field):
        self.model_name = model_name
        self.name = name
        self.field = field

    def render(self, app_label):
        return actions.CreateField(
            app_label = app_label,
            model_name = self.model_name,
            name = self.name,
            instance = self.field,
        )
