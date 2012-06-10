from django.utils import unittest
from ..exceptions import CircularDependency
from ..dependencies import depends, flatten


class DependencyTests(unittest.TestCase):
    """
    Tests the dependency resolution logic
    """

    def test_flatten(self):
        "Test that the flatten function works as intended"
        self.assertEqual(
            list(flatten([
                1,
                [2, 3, [4, 5]],
                [6],
                [7, "a", ["b"]],
            ])),
            [1, 2, 3, 4, 5, 6, 7, "a", "b"]
        )

    def test_depends_linear(self):
        "Very simple (linear) dependency test"
        target = 4
        links = {4: [3], 3: [2], 2: [1]}
        self.assertEqual(
            depends(target, lambda x: links.get(x, [])),
            [1, 2, 3, 4],
        )

    def test_depends_simple(self):
        "Simple (single cross-link) dependency test"
        target = 4
        links = {4: [3], 3: [2, 11], 2: [1]}
        self.assertEqual(
            depends(target, lambda x: links.get(x, [])),
            [1, 2, 11, 3, 4],
        )

    def test_depends_complex(self):
        "Triple cross-link dependency test"
        target = "b3"
        links = {
            "b3": ["a3", "b2", "c2"],
            "b2": ["a1", "b1"],
            "a3": ["a1", "b2"],
            "a2": ["a1"],
            "c3": ["c2"],
            "c2": ["c1"],
        }
        self.assertEqual(
            depends(target, lambda x: links.get(x, [])),
            ['c1', 'c2', 'b1', 'a1', 'b2', 'a3', 'b3'],
        )

    def test_circular(self):
        "Circular dependency test"
        target = "b3"
        links = {
            "b3": ["a3", "b2", "c2"],
            "b2": ["a1", "b1"],
            "a3": ["a1", "b2", "c3"],
            "a2": ["a1"],
            "c3": ["b3", "c2"],
            "c2": ["c1"],
        }
        self.assertRaises(
            CircularDependency,
            depends, target, lambda x: links.get(x, []),
        )
