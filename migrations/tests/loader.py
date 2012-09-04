import os
from django.utils import unittest
from ..loader import Loader
from ..migration import Migration
from ..exceptions import AmbiguousMigration, NonexistentMigration, UnmigratedApp


class LoaderTests(unittest.TestCase):
    """
    Tests the migration dependency manager/planner
    """

    def get_test_loader(self):
        "Creates a loader for the tests"
        loader = Loader({
            "app1": os.path.join(os.path.dirname(__file__), "loader_files", "app1"),
            "app2": os.path.join(os.path.dirname(__file__), "loader_files", "app2"),
        })
        loader.load_all()
        loader.calculate_dependencies()
        return loader

    def test_load(self):
        "Tests the basics of the loader"
        loader = self.get_test_loader()
        # Make sure things look good
        self.assertEqual(
            set(loader.migrations.keys()),
            set(["app1", "app2"]),
        )
        self.assertEqual(
            set(loader.migrations["app1"].keys()),
            set(["0000_root", "0001_initial", "0002_yob"]),
        )
        self.assertEqual(
            set(loader.migrations["app2"].keys()),
            set(["0000_root", "0001_initial"]),
        )
        self.assertEqual(
            loader.migrations["app1"]["0001_initial"].app_label,
            "app1"
        )
        self.assertEqual(
            loader.migrations["app1"]["0001_initial"].name,
            "0001_initial"
        )
        self.assertEqual(
            len(loader.migrations["app1"]["0001_initial"].actions[0].fields),
            2,
        )
        # Make sure the dependencies loaded correctly
        self.assertEqual(
            loader.dependencies[Migration("app1", "0001_initial")],
            [Migration("app1", "0000_root")],
        )
        self.assertEqual(
            loader.reverse_dependencies[Migration("app1", "0001_initial")],
            [Migration("app1", "0002_yob")],
        )
        self.assertEqual(
            loader.dependencies[Migration("app1", "0002_yob")],
            [Migration("app1", "0001_initial"), Migration("app2", "0001_initial")],
        )
        self.assertEqual(
            loader.reverse_dependencies[Migration("app2", "0001_initial")],
            [Migration("app1", "0002_yob")],
        )
        self.assertEqual(
            loader.reverse_dependencies[Migration("app1", "0002_yob")],
            [],
        )

    def test_get(self):
        "Tests get_migration and get_migration_by_prefix"
        loader = self.get_test_loader()
        self.assertEqual(loader.get_migration("app1", "0002_yob"), Migration("app1", "0002_yob"))
        self.assertEqual(
            loader.get_migration_by_prefix("app1", "0002"),
            loader.get_migration("app1", "0002_yob"),
        )
        self.assertRaises(
            AmbiguousMigration,
            loader.get_migration_by_prefix, "app1", "000",
        )
        self.assertRaises(
            NonexistentMigration,
            loader.get_migration_by_prefix, "app1", "0003",
        )
        self.assertRaises(
            NonexistentMigration,
            loader.get_migration, "app1", "0002",
        )
        self.assertRaises(
            UnmigratedApp,
            loader.get_migration, "app3", "0001",
        )
        self.assertRaises(
            UnmigratedApp,
            loader.get_migration_by_prefix, "app3", "0001",
        )

    def test_get_top(self):
        "Tests get_top_migration"
        loader = self.get_test_loader()
        self.assertEqual(
            loader.get_top_migration("app1"),
            loader.get_migration("app1", "0002_yob"),
        )
        self.assertEqual(
            loader.get_top_migration("app2"),
            loader.get_migration("app2", "0001_initial"),
        )
        self.assertRaises(
            UnmigratedApp,
            loader.get_top_migration, "app3",
        )

    def test_plan_onedep(self):
        "Test a simple dependency plan"
        loader = self.get_test_loader()
        self.assertEqual(
            loader.plan(
                [Migration("app1", "0002_yob")],
                []
            ),
            [
                (True, Migration("app2", "0001_initial")),
                (True, Migration("app1", "0001_initial")),
                (True, Migration("app1", "0002_yob")),
            ],
        )

    def test_plan_single(self):
        "A simple one-step plan"
        loader = self.get_test_loader()
        self.assertEqual(
            loader.plan(
                [Migration("app1", "0001_initial")],
                []
            ),
            [
                (True, Migration("app1", "0001_initial")),
            ],
        )

    def test_plan_noop(self):
        "A no-op (target is most recently applied)"
        loader = self.get_test_loader()
        self.assertEqual(
            loader.plan(
                [Migration("app1", "0002_yob")],
                [
                    Migration("app1", "0001_initial"),
                    Migration("app1", "0002_yob"),
                    Migration("app2", "0001_initial"),
                ],
            ),
            [],
        )

    def test_plan_no_crossremove(self):
        "Tests that asserting just after a certain migration does not cross apps"
        loader = self.get_test_loader()
        # Then, a partial undo
        self.assertEqual(
            loader.plan(
                [Migration("app2", "0001_initial")],
                [
                    Migration("app1", "0001_initial"),
                    Migration("app1", "0002_yob"),
                    Migration("app2", "0001_initial"),
                ],
            ),
            [],
        )

    def test_plan_partial_undo(self):
        "Tests partially unmigrating an app"
        loader = self.get_test_loader()
        # Then, a partial undo
        self.assertEqual(
            loader.plan(
                [Migration("app1", "0001_initial")],
                [
                    Migration("app1", "0001_initial"),
                    Migration("app1", "0002_yob"),
                    Migration("app2", "0001_initial"),
                ],
            ),
            [
                (False, Migration("app1", "0002_yob")),
            ],
        )

    def test_plan_full_one(self):
        "Tests partially unmigrating an app"
        loader = self.get_test_loader()
        # Then, a partial undo
        self.assertEqual(
            loader.plan(
                [Migration("app2", "0000_root")],
                [
                    Migration("app1", "0001_initial"),
                    Migration("app1", "0002_yob"),
                    Migration("app2", "0001_initial"),
                ],
            ),
            [
                (False, Migration("app1", "0002_yob")),
                (False, Migration("app2", "0001_initial")),
            ],
        )

    def test_plan_full_undo(self):
        "Tests fully unmigrating all apps"
        loader = self.get_test_loader()
        self.assertEqual(
            loader.plan(
                [Migration("app1", "0000_root"), Migration("app2", "0000_root")],
                [
                    Migration("app1", "0001_initial"),
                    Migration("app1", "0002_yob"),
                    Migration("app2", "0001_initial"),
                ],
            ),
            [
                (False, Migration("app1", "0002_yob")),
                (False, Migration("app1", "0001_initial")),
                (False, Migration("app2", "0001_initial")),
            ],
        )

    def test_state_empty(self):
        "Tests that the first state of the first migration is empty"
        loader = self.get_test_loader()
        action_states = loader.action_states(loader.get_migration("app1", "0001_initial"))
        self.assertEqual(action_states[0][1].models, {})

    def test_state_full(self):
        "Tests that state() of app1 is correct after both migrations"
        loader = self.get_test_loader()
        action_states = loader.action_states(loader.get_migration("app1", "0002_yob"))
        # Make sure the models are there from both apps at the start (because of dependency)
        self.assertListEqual(
            action_states[0][1].models.keys(),
            [
                ("app1", "Author"),
                ("app2", "Book"),
            ],
        )
        # Make sure Author has the right fields at the end
        self.assertListEqual(
            [x for x, y in action_states[-1][2].models["app1", "Author"].fields],
            ["id", "name", "yob"],
        )
