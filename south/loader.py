import os
from django.conf import settings
from django.utils import importlib
from .migration import Migration, RootMigration
from .dependencies import depends
from .exceptions import NonexistentDependency, InvalidDependency, NonexistentMigration, AmbiguousMigration, UnmigratedApp
from .state import ProjectState


class Loader(object):
    """
    Responsible for scanning the filesystem for migrations, loading them in,
    planning, state creation and dependency handling.
    """

    def __init__(self, apps):
        "Constructor. Apps should be a map of {app label: migs dir}"
        self.apps = apps
        self.migrations = {}
        self.dependencies = {}
        self.reverse_dependencies = {}

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
            if os.path.isdir(mig_path):
                result[app_label] = mig_path
        # Construct the class
        return cls(result)

    def load_all(self):
        "Loads all migrations of all enabled apps"
        for app_label in sorted(self.apps.keys()):
            self.load_app(app_label)

    def load_app(self, app_label):
        "Loads all migrations of the specified app"
        self.migrations[app_label] = {"0000_root": RootMigration(app_label)}
        # Read in all the migrations by name
        for filename in os.listdir(self.apps[app_label]):
            path = os.path.join(self.apps[app_label], filename)
            if filename.endswith(".migration"):
                # Alright, load it
                name = filename[:-10]
                migration = Migration(app_label, name)
                migration.load(path)
                self.migrations[app_label][name] = migration

    def calculate_dependencies(self):
        "Calculates and stores the dependency links"
        for app_label, migrations in self.migrations.items():
            migrations = migrations.values()
            migrations.sort(key=lambda m: m.name)
            for i, migration in enumerate(migrations):
                # Initialise our entries
                self.dependencies.setdefault(migration, [])
                self.reverse_dependencies.setdefault(migration, [])
                # If we're not the first, add a dep link backwards
                if i > 0:
                    self.dependencies[migration].append(migrations[i - 1])
                # If we're not the last, add a reverse dep link forwards
                if i < len(migrations) - 1:
                    self.reverse_dependencies[migration].append(migrations[i + 1])
                # For each dependency entry, add the right links
                for dep_tuple in migration.dependencies:
                    if dep_tuple[0] == app_label:
                        raise InvalidDependency("Migration %s depends on something in its own app: %s" % (
                            migration,
                            "%s:%s" % dep_tuple,
                        ))
                    try:
                        dependency = self.migrations[dep_tuple[0]][dep_tuple[1]]
                    except KeyError:
                        raise NonexistentDependency("Migration %s depends on non-existent %s" % (
                            migration,
                            "%s:%s" % dep_tuple,
                        ))
                    self.reverse_dependencies.setdefault(dependency, [])
                    self.dependencies[migration].append(dependency)
                    self.reverse_dependencies[dependency].append(migration)

    def get_migration(self, app_label, name):
        "Returns a Migration class with loaded actions by name"
        if app_label not in self.migrations:
            raise UnmigratedApp("App %s does not have migrations." % app_label)
        try:
            return self.migrations[app_label][name]
        except KeyError:
            raise NonexistentMigration("No loaded migration matches %s:%s" % (app_label, name))

    def get_migration_by_prefix(self, app_label, prefix):
        "Given an app label and prefix of a migration name, either returns one or errors"
        if app_label not in self.migrations:
            raise UnmigratedApp("App %s does not have migrations." % app_label)
        matches = []
        for name in self.migrations[app_label]:
            if name.startswith(prefix):
                matches.append(name)
        if not matches:
            raise NonexistentMigration("No loaded migration match the prefix %s:%s" % (app_label, name))
        elif len(matches) > 1:
            raise AmbiguousMigration("Multiple migrations match the prefix %s:%s (%s)" % (
                app_label,
                name,
                ", ".join(matches),
            ))
        else:
            return self.get_migration(app_label, matches[0])

    def get_top_migration(self, app_label):
        "Returns the most recent migration for app_label"
        if app_label not in self.migrations:
            raise UnmigratedApp("App %s does not have migrations." % app_label)
        return sorted(self.migrations[app_label].items())[-1][1]

    def get_forward_dependencies(self, migration):
        return self.dependencies.get(migration, [])

    def get_backwards_dependencies(self, migration):
        return self.reverse_dependencies.get(migration, [])

    def plan(self, targets, applied):
        """
        Takes a set of target Migration id tuples and returns a plan for them.
        Also needs a set of already-applied migrations, to which the root migrations
        will be added.
        Returns a list of (forwards?, migration_instance).
        """
        applied = set(applied)
        for app_label in self.migrations:
            applied.add(RootMigration(app_label))
        # Plan!
        plan = []
        for target in targets:
            forwards = target not in applied
            if forwards:
                # Go through a forwards plan and add anything missing
                for entry in depends(target, self.get_forward_dependencies):
                    if entry not in applied:
                        plan.append((True, entry))
                        applied.add(entry)
            else:
                # Work out if there's another migration ahead of us in the app.
                # If so, this is a backwards migration ending with removing that.
                backwards_target = None
                for dependent in self.get_backwards_dependencies(target):
                    if dependent.app_label == target.app_label:
                        backwards_target = dependent
                # Go through a backwards plan and remove anything we need to
                if backwards_target:
                    for entry in depends(backwards_target, self.get_backwards_dependencies):
                        if entry in applied:
                            plan.append((False, entry))
                            applied.remove(entry)
        return plan

    def state(self, migration):
        """
        Given a migration, returns a state.ProjectState representing the
        models of the project needed for this migration (for things like
        ForeignKeys, __bases__, Python code blocks, etc.)
        """
        # Use the planner to work out the migrations we need to consider
        plan = self.plan([migration], [])
        # Step through and build up a ProjectState
        project_state = ProjectState()
        for forwards, migration in plan:
            if not forwards:
                raise ValueError("State migration plan contains backwards migration.")
            for action in migration.actions:
                action.alter_state(project_state)
        # Return it
        return project_state
