# -*- coding: utf-8 -*-
# Copyright 2018 Naglis Jonaitis
# License AGPL-3 or later (https://www.gnu.org/licenses/agpl).

import requests_mock

from .common import (
    OpenProjectBackendTestCase,
    get_openproject_mocker,
    json_test_file,
)


class TestUserImport(OpenProjectBackendTestCase):

    def test_user_is_created(self):
        with get_openproject_mocker():
            with self.backend.work_on('openproject.res.users') as work:
                importer = work.component(usage='record.importer')
                importer.run('1')

        user = self.backend.op_user_ids
        self.assertLen(user, 1)
        self.assertEqual(user.openproject_id, '1')
        self.assertEqual(user.name, u'John Sheppärd')
        self.assertEqual(user.login, 'john_sheppard')
        self.assertEqual(user.email, 'shep@mail.com')
        self.assertEqual(user.op_create_date, '2014-05-21 08:51:20')
        self.assertEqual(user.op_write_date, '2014-05-21 08:51:20')

    def test_deleted_user_is_marked_as_inactive(self):
        with requests_mock.Mocker() as m:
            m.get(
                'http://openproject/api/v3/users/1',
                json=json_test_file('users_1_deleted.json'))
            with self.backend.work_on('openproject.res.users') as work:
                importer = work.component(usage='record.importer')
                importer.run('1')

        user = self.backend.with_context(active_test=False).op_user_ids
        self.assertLen(user, 1)
        self.assertFalse(user.active)
        self.assertEqual(
            user.login, '__op_%s_deleted_user_1' % self.backend.id)

    def test_locked_user_is_marked_as_inactive(self):
        with requests_mock.Mocker() as m:
            m.get(
                'http://openproject/api/v3/users/1',
                json=json_test_file('users_1_locked.json'))
            with self.backend.work_on('openproject.res.users') as work:
                importer = work.component(usage='record.importer')
                importer.run('1')

        user = self.backend.with_context(active_test=False).op_user_ids
        self.assertLen(user, 1)
        self.assertFalse(user.active)
