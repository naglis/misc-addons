# -*- coding: utf-8 -*-
# Copyright 2017 Naglis Jonaitis
# License AGPL-3 or later (https://www.gnu.org/licenses/agpl).

from .common import OpenProjectBackendTestCase, get_openproject_mocker
from ..const import (
    ACTIVITY_SYNC_ALL,
    ACTIVITY_SYNC_NONE,
    ACTIVITY_SYNC_UPDATES,
)


class TestActivityImport(OpenProjectBackendTestCase):

    def setUp(self):
        super(TestActivityImport, self).setUp()
        with get_openproject_mocker():
            self.backend.import_projects(delay=False)

    def _run_import(self, sync_activities=ACTIVITY_SYNC_ALL):
        self.backend.op_project_ids.write({
            'sync_activities': sync_activities,
        })
        with get_openproject_mocker():
            self.backend.import_project_work_packages(delay=False)

    def test_activity_import_disabled_no_activities_are_imported(self):
        self._run_import(ACTIVITY_SYNC_NONE)

        self.assertLen(self.backend.op_task_ids, 1)
        wp = self.backend.op_task_ids
        self.assertLen(wp.message_ids, 0)

    def test_activity_import_updates_only_no_activities_are_imported(self):
        self._run_import(ACTIVITY_SYNC_UPDATES)

        self.assertLen(self.backend.op_task_ids, 1)
        wp = self.backend.op_task_ids
        self.assertLen(wp.message_ids, 0)

    def test_activities_are_created(self):
        self._run_import()

        self.assertLen(self.backend.op_task_ids, 1)
        wp = self.backend.op_task_ids
        self.assertLen(wp.message_ids, 1)

        message = wp.message_ids
        self.assertEqual(message.body, '<p>Lorem ipsum dolor sit amet.</p>')
        self.assertEqual(
            message.subtype_id,
            self.browse_ref(
                'connector_openproject.mail_message_subtype_wp_comment'))
