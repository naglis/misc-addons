# -*- coding: utf-8 -*-
# Copyright 2017-2018 Naglis Jonaitis
# License AGPL-3 or later (https://www.gnu.org/licenses/agpl).

from .common import OpenProjectBackendTestCase, get_openproject_mocker


class TestProjectImport(OpenProjectBackendTestCase):

    def test_projects_are_created(self):
        with get_openproject_mocker():
            self.backend.import_projects(delay=False)
            projects = self.backend.op_project_ids
            self.assertLen(projects, 2)
            self.assertItemsEqual(
                projects.mapped('openproject_id'), ('6', '14'))
            self.assertItemsEqual(
                projects.mapped('name'), ('A project', 'Another project'))
            project_1 = projects[0]
            self.assertEqual(project_1.label_tasks, 'Work Packages')
            self.assertEqual(project_1.op_create_date, '2015-07-06 13:28:14')
            self.assertEqual(project_1.op_write_date, '2015-10-01 09:55:02')

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
