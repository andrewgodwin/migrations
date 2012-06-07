import re
from django.utils import importlib
from . import datetime_utils


def parse_field_definition(definition):
    """
    Given a field definition in the format appname.ClassName or
    full.module.path.ClassName, resolves into a field instance.
    """
    # First, split by brackets
    match = re.match(r"([\d\w\._]+)\(([^\)]+)\)", definition)
    if not match:
        raise ValueError("%s is not a valid field definition" % definition)
    path, args = match.groups()
    # Next, resolve that path
    bits = path.split(".")
    if len(bits) == 2:
        if bits[0] == "django":
            path = "django.db.models.%s" % bits[-1]
    if "." not in path:
        raise ValueError("Invalid field class '%s'" % path)
    module_path, class_name = path.rsplit(".", 1)
    # Import the class and instantiate it
    module = importlib.import_module(module_path)
    klass = getattr(module, class_name)
    fake_locals = {
        '_': lambda x: x,
        'datetime': datetime_utils,
        class_name: klass,
    }
    instance = eval("%s(%s)" % (class_name, args), {}, fake_locals)
    return instance
