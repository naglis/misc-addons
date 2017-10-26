# -*- coding: utf-8 -*-
# Copyright 2017 Naglis Jonaitis
# License AGPL-3 or later (https://www.gnu.org/licenses/agpl).

from .common import OpenProjectBackendTestCase, get_openproject_mocker


class TestWorkPackageImport(OpenProjectBackendTestCase):

    def setUp(self):
        super(TestWorkPackageImport, self).setUp()
        with get_openproject_mocker():
            self.backend.import_projects(delay=False)

    def test_work_package_is_created(self):
        with get_openproject_mocker():
            self.backend.import_project_work_packages(delay=False)
            wp = self.env['openproject.project.task'].search([
                ('backend_id', '=', self.backend.id),
            ])
            self.assertLen(wp, 1)
            self.assertEqual(wp.openproject_id, '1528')
            self.assertEqual(wp.name, 'Develop API')
            self.assertEqual(wp.date_start, '2014-08-30 00:00:00')
            self.assertEqual(wp.date_deadline, '2014-09-01')
            self.assertEqual(wp.project_id.name, 'A project')
            self.assertEqual(wp.user_id.name, 'John Sheppard')
            self.assertEqual(wp.stage_id.name, 'New')
            self.assertEqual(
                wp.description, '<p>Develop super cool OpenProject API.</p>')
            self.assertAlmostEqual(wp.planned_hours, 2.0, places=2)
            self.assertEqual(wp.op_create_date, '2014-08-29 12:40:53')
            self.assertEqual(wp.op_write_date, '2014-08-29 12:44:41')

    def test_user_dependency_is_created(self):
        with get_openproject_mocker():
            self.backend.import_project_work_packages(delay=False)
            user = self.backend.op_user_ids
            self.assertLen(user, 1)
            self.assertEqual(user.openproject_id, '1')
            self.assertEqual(user.name, 'John Sheppard')
            self.assertEqual(user.email, 'shep@mail.com')
            self.assertEqual(user.op_create_date, '2014-05-21 08:51:20')
            self.assertEqual(user.op_write_date, '2014-05-21 08:51:20')
