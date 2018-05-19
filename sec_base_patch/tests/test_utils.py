# Copyright 2018 Naglis Jonaitis
# License AGPL-3 or later (https://www.gnu.org/licenses/agpl).

import unittest

from . import common
from ..utils import (
    is_patched,
    patch_func,
    unpatch_func,
)


class TestPatchUtils(unittest.TestCase):

    def tearDown(self):
        super().tearDown()
        unpatch_func(common, 'func_a')

    def test_simple_patch(self):
        self.assertTrue(patch_func(common, 'func_a', lambda: -2))
        self.assertEqual(common.func_a(), -2)

    def test_func_not_patched_repeatedly(self):
        patch_func(common, 'func_a', lambda: -2)
        self.assertFalse(patch_func(common, 'func_a', lambda: 11))
        self.assertEqual(common.func_a(), -2)

    def test_unpatch_function_is_unpatched(self):
        patch_func(common, 'func_a', lambda: -2)
        self.assertTrue(unpatch_func(common, 'func_a'))
        self.assertEqual(common.func_a(), 42)

    def test_unpatch_func_on_not_patched_func_returns_false(self):
        self.assertFalse(is_patched(common.func_a, 'func_a'))
        self.assertFalse(unpatch_func(common, 'func_a'))

    def test_is_patched_on_patch_func_returns_true(self):
        patch_func(common, 'func_a', lambda: -2)
        self.assertTrue(is_patched(common.func_a, 'func_a'))

    def test_is_patched_on_unpatched_func_returns_false(self):
        patch_func(common, 'func_a', lambda: -2)
        unpatch_func(common, 'func_a')
        self.assertFalse(is_patched(common.func_a, 'func_a'))
