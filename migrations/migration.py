from .parser import MigrationParser


class Migration(object):
    """
    Represents a migration file on disk.
    """

    is_root = False

    def __init__(self, app_label, name):
        self.app_label = app_label
        self.name = name

    def load(self, path):
        "Reads the migration and parses it"
        parser = MigrationParser(self.app_label, path)
        parser.parse()
        self.actions = parser.actions
        self.dependencies = parser.dependencies

    def __eq__(self, other):
        try:
            return self.app_label == other.app_label and self.name == other.name
        except AttributeError:
            return False

    def __neq__(self, other):
        return not self == other

    def __hash__(self):
        return hash((self.app_label, self.name))

    def __str__(self):
        return "%s:%s" % (self.app_label, self.name)

    def __repr__(self):
        return "<Migration %s:%s>" % (self.app_label, self.name)


class RootMigration(Migration):
    """
    Special Migration-like class for the root migration
    (the fake migration that exists before the initial one).
    This is used as a target for "undo all migrations".
    """

    is_root = True

    def __init__(self, app_label):
        self.app_label = app_label
        self.name = "0000_root"
        self.dependencies = []

    def load(self):
        raise RuntimeError("You cannot call load() on RootMigration")
