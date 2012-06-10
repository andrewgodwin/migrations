import sys
from django.core.management import BaseCommand
from ...migrator import Migrator
from ...loader import Loader
from ...exceptions import UnmigratedApp, NonexistentMigration, AmbiguousMigration, NonexistentDependency


class Command(BaseCommand):

    def handle(self, app=None, target=None, **kwargs):
        # Construct tne migrator and calculate the plan
        try:
            loader = Loader.from_settings()
            loader.load_all()
            loader.calculate_dependencies()
            migrator = PrettyMigrator(loader)
            plan = migrator.calculate_plan(app, target)
        except UnmigratedApp, e:
            print >>sys.stderr, "Error:", e
            sys.exit(1)
        except NonexistentMigration, e:
            print >>sys.stderr, "Error:", e
            sys.exit(1)
        except NonexistentDependency, e:
            print >>sys.stderr, "Error:", e
            sys.exit(1)
        except AmbiguousMigration, e:
            print >>sys.stderr, "Error:", e
            sys.exit(1)
        # Run the plan
        if plan:
            migrator.execute_plan(plan)
        else:
            print "No migrations required."


class PrettyMigrator(Migrator):
    """
    Subclass of Migrator that nicely logs what's happening.
    """

    def log_migration_start(self, migration, forwards):
        print "Running %s..." % migration

    def log_migration_end(self, migration, forwards):
        print "%s complete." % migration

    def log_action_start(self, migration, action, forwards):
        print " -> %s" % action
