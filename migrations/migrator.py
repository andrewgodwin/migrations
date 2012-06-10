from django.db import DEFAULT_DB_ALIAS
from .models import AppliedMigration


class Migrator(object):
    """
    Handles execution of migrations.
    """

    def __init__(self, loader):
        self.loader = loader

    def calculate_plan(self, app=None, target=None, database=DEFAULT_DB_ALIAS):
        """
        Entrypoint for a migration command.
        Plans the execution, and then executes it.
        """
        # Work out what targets they want
        if app is None:
            targets = [self.loader.get_top_migration(app_label) for app_label in self.loader.migrations.keys()]
        elif app is not None and target is None:
            targets = [self.loader.get_top_migration(app)]
        else:
            targets = [self.loader.get_migration_by_prefix(app, target)]
        # Make a plan for that, taking already-applied ones into account
        return self.loader.plan(targets, [(a.app_label, a.name) for a in AppliedMigration.objects.using(database)])

    def execute_plan(self, plan, database=DEFAULT_DB_ALIAS):
        "Executes the supplied plan"
        for forwards, migration in plan:
            self.log_migration_start(migration, forwards)
            action_states = self.loader.action_states(migration, forwards)
            for action, from_state, to_state in action_states:
                self.log_action_start(migration, action, forwards)
                action.alter_database(from_state, to_state, database, forwards)
                self.log_action_end(migration, action, forwards)
            self.log_migration_end(migration, forwards)

    def log_migration_start(self, migration, forwards):
        pass

    def log_migration_end(self, migration, forwards):
        pass

    def log_action_start(self, migration, action, forwards):
        pass

    def log_action_end(self, migration, action, forwards):
        pass
