# -*- coding: utf-8 -*-
# Copyright 2017-2018 Naglis Jonaitis
# License AGPL-3 or later (https://www.gnu.org/licenses/agpl).

import json

import requests_mock

from odoo.modules import get_resource_path
from odoo.addons.component.tests import common


def make_test_data_filename_getter(module_name):

    def getter(filename):
        return get_resource_path(module_name, 'tests', 'data', filename)

    return getter


test_file = make_test_data_filename_getter('connector_openproject')


def json_test_file(filename, path_getter=test_file):
    with open(path_getter(filename)) as f:
        return json.load(f)


def get_openproject_mocker(projects_response_file='projects.json'):
    mocker = requests_mock.Mocker()

    mocker.get(
        'mock://localhost/api/v3/users/1',
        json=json_test_file('users_1.json'))
    mocker.get('https://gravatar/avatar', headers={
        'Content-Type': 'image/png',
    }, body=open(test_file('image.png')))
    mocker.get(
        'mock://localhost/api/v3/projects',
        json=json_test_file(projects_response_file),
    )
    mocker.get(
        'mock://localhost/api/v3/statuses/1',
        json=json_test_file('statuses_1.json'))
    mocker.get(
        'mock://localhost/api/v3/work_packages',
        json=json_test_file('work_packages_project_6.json'))
    mocker.get(
        'mock://localhost/api/v3/work_packages/1528',
        json=json_test_file('work_packages_1528.json'))
    mocker.get(
        'mock://localhost/api/v3/work_packages/1528/activities',
        json=json_test_file('work_packages_1528_activities.json'))
    mocker.get(
        'mock://localhost/api/v3/time_entries',
        json=json_test_file('project_1_time_entries.json'))

    return mocker


class OpenProjectBackendTestCase(common.TransactionComponentCase):

    def setUp(self):
        super(OpenProjectBackendTestCase, self).setUp()
        self.backend = self.env.ref('connector_openproject.backend_1')

    def assertLen(self, collection, expected, msg=None):
        actual = len(collection)
        self.assertEqual(
            actual,
            expected,
            msg=msg or (
                'Wrong number of items in collection, '
                'expected: %d, got: %d' % (expected, actual)),
        )
