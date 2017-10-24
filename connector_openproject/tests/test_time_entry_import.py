# -*- coding: utf-8 -*-
# Copyright 2017 Naglis Jonaitis
# License AGPL-3 or later (https://www.gnu.org/licenses/agpl).

from .common import OpenProjectBackendTestCase, get_openproject_mocker


class TestTimeEntryImport(OpenProjectBackendTestCase):

    def test_time_entry_is_created(self):
        with get_openproject_mocker():
            self.backend.import_projects(delay=False)
            self.backend.op_project_ids.filtered(
                lambda p: not p.openproject_id == '6').write(
                    {'op_sync': False})
            self.backend.import_project_time_entries(delay=False)
            time_entry = self.backend.op_time_entry_ids
            self.assertLen(time_entry, 1)
            self.assertAlmostEqual(time_entry.unit_amount, 3.23, places=2)
            self.assertRegexpMatches(time_entry.name, r'Some text.*')
            self.assertEqual(time_entry.date, '2015-03-20')
            self.assertEqual(time_entry.op_create_date, '2015-03-20 12:56:56')
            self.assertEqual(time_entry.op_write_date, '2015-03-20 12:56:56')
