from .parser import MigrationParser


class Migration(object):
    """
    Represents a migration file on disk.
    """

    def __init__(self, app_label, name, path):
        self.app_label = app_label
        self.name = name
        self.path = path

    def load(self):
        "Reads the migration and parses it"
        parser = MigrationParser(self.app_label, self.path)
        parser.parse()
        self.actions = parser.actions
        self.dependencies = parser.dependencies
