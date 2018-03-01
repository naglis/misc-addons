# -*- coding: utf-8 -*-
# Copyright 2018 Naglis Jonaitis
# License AGPL-3 or later (https://www.gnu.org/licenses/agpl).

from .common import OpenProjectBackendTestCase, get_openproject_mocker


class TestProjectStatusSync(OpenProjectBackendTestCase):

    def setUp(self):
        super(TestProjectStatusSync, self).setUp()
        with get_openproject_mocker():
            self.backend.import_projects(delay=False)

    def test_project_archived_on_op_is_marked_inactive(self):
        with get_openproject_mocker(
                projects_response_file='projects_one_archived.json'):
            self.backend.import_projects(delay=False)

        with self.backend.work_on('openproject.project.project') as work:
            binder = work.component(usage='binder')
            self.assertTrue(binder.to_internal('6').active)
            self.assertFalse(binder.to_internal('14').active)

    def test_project_unarchived_on_op_is_marked_active(self):
        # Mark as archived.
        with get_openproject_mocker(
                projects_response_file='projects_one_archived.json'):
            self.backend.import_projects(delay=False)

        with get_openproject_mocker():
            self.backend.import_projects(delay=False)

        with self.backend.work_on('openproject.project.project') as work:
            binder = work.component(usage='binder')
            self.assertTrue(binder.to_internal('14').active)
