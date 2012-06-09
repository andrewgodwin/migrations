"""
Contains classes which model the state of an app's models.
Not called models.py for obvious reasons.
"""


class ModelState(object):
    """
    Represents a Django Model. We don't use the actual Model class
    as it's not designed to have its options changed - instead, we
    mutate this one and then render it into a Model as required.
    """

    def __init__(self, app_label, name, fields=None, options=None, bases=None):
        self.app_label = app_label
        self.name = name
        self.fields = fields or []
        self.options = options or {}
        self.bases = bases or []

    def copy(self):
        "Returns an exact copy of this ModelState"
        return self.__class__(
            app_label = self.app_label,
            name = self.name,
            fields = self.fields,
            options = self.options,
            bases = self.bases,
        )

    def render(self):
        "Returns a Model object created from our current state"
        # First, make a Meta object
        meta_contents = {'app_label': app}
        meta_contents.update(self.options)
        for key, code in data.items():
            # Some things we never want to use.
            if key in ["_bases", "_ormbases"]:
                continue
            # Some things we don't want with stubs.
            if stub and key in ["order_with_respect_to"]:
                continue
            # OK, add it.
            try:
                results[key] = self.eval_in_context(code, app)
            except (NameError, AttributeError), e:
                raise ValueError("Cannot successfully create meta field '%s' for model '%s.%s': %s." % (
                    key, app, model, e
                ))
        return type("Meta", tuple(), results) 
    
