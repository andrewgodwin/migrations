import os
from django.conf import settings
from django.utils import importlib
from .migration import Migration


class Loader(object):
    """
    Responsible for scanning the filesystem for migrations, loading them in,
    and dependency handling.
    """

    def __init__(self, apps):
        "Constructor. Apps should be a map of {app label: migs dir}"
        self.apps = apps
        self.migrations = {}

    @classmethod
    def from_settings(cls):
        "Makes a Loader configured for the current INSTALLED_APPS setting"
        result = {}
        for app in settings.INSTALLED_APPS:
            # Work out its app label, do a sanity check
            app_label = app.split(".")[-1]
            if app_label in result:
                raise ValueError("There are two apps with the same app_label: %s" % app_label)
            # Work out migration path and see if it exists
            module = importlib.import_module(app)
            mig_path = os.path.join(os.path.dirname(module.__file__), "migrations")
            if os.path.is_dir(mig_path):
                result[app_label] = mig_path
        # Construct the class
        return cls(result)

    def load_all(self):
        "Loads all migrations of all enabled apps"
        for app_label in self.apps:
            self.load_app(app_label)

    def load_app(self, app_label):
        "Loads all migrations of the specified app"
        self.migrations[app_label] = {}
        # Read in all the migrations by name
        for filename in os.listdir(self.apps[app_label]):
            path = os.path.join(self.apps[app_label], filename)
            if filename.endswith(".migration"):
                # Alright, load it
                name = filename[:-10]
                migration = Migration(app_label, name, path)
                migration.load()
                self.migrations[app_label][name] = migration

