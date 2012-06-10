"""
Contains classes which model the state of an app's models.
Not called models.py for obvious reasons.
"""

from django.db import models


class ProjectState(object):
    """
    Represents the entire project's overall state.
    This is the item that is passed around - we do it here rather than at the
    app level so that cross-app FKs/etc. resolve properly.
    """

    def __init__(self, models=None):
        self.models = models or {}

    def copy(self):
        ps = ProjectState(
            models = dict((k, v.copy()) for k, v in self.models.items())
        )
        for model in ps.models.values():
            model.project_state = ps
        return ps


class ModelState(object):
    """
    Represents a Django Model. We don't use the actual Model class
    as it's not designed to have its options changed - instead, we
    mutate this one and then render it into a Model as required.
    """

    def __init__(self, project_state, app_label, name, fields=None, options=None, bases=None):
        self.project_state = project_state
        self.app_label = app_label
        self.name = name
        self.fields = fields or []
        self.options = options or {}
        self.bases = bases or []

    def copy(self):
        "Returns an exact copy of this ModelState"
        return self.__class__(
            project_state = self.project_state,
            app_label = self.app_label,
            name = self.name,
            fields = self.fields,
            options = self.options,
            bases = self.bases,
        )

    def render(self):
        "Returns a Model object created from our current state"
        # First, make a Meta object
        meta_contents = {'app_label': self.app_label}
        meta_contents.update(self.options)
        meta = type("Meta", tuple(), meta_contents)
        # Then, work out our bases
        # TODO: Use the actual bases
        bases = [models.Model]
        # Turn fields into a dict for the body, add other bits
        body = dict(self.fields)
        body['Meta'] = meta
        body['__module__'] = "__fake__"
        # Then, make a Model object
        return type(
            self.name,
            tuple(bases),
            body,
        )
