from django.db import DEFAULT_DB_ALIAS
from .loader import Loader
from .models import AppliedMigration


def migrate(app=None, target=None, database=DEFAULT_DB_ALIAS):
    """
    Entrypoint for a migration command.
    Loads the migrations, plans the execution, and then executes it.
    """
    # Load the migrations
    loader = Loader.from_settings()
    loader.load_all()
    loader.calculate_dependencies()
    # Work out what targets they want
    if app is None:
        targets = [loader.get_top_migration(app_label) for app_label in loader.migrations.keys()]
    elif app is not None and target is None:
        targets = [loader.get_top_migration(app)]
    else:
        targets = [loader.get_migration_by_prefix(app, target)]
    # Make a plan for that, taking already-applied ones into account
    plan = loader.plan(targets, [(a.app_label, a.name) for a in AppliedMigration.objects.using(database)])
    print plan
