import sys
from django.core.management import BaseCommand
from ...commands import migrate
from ...exceptions import UnmigratedApp, NonexistentMigration, AmbiguousMigration


class Command(BaseCommand):

    def handle(self, app=None, target=None, **kwargs):
        try:
            migrate(app, target)
        except UnmigratedApp, e:
            print >>sys.stderr, e
            sys.exit(1)
        except NonexistentMigration, e:
            print >>sys.stderr, e
            sys.exit(1)
        except AmbiguousMigration, e:
            print >>sys.stderr, e
            sys.exit(1)
