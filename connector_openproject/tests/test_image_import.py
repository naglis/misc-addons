# -*- coding: utf-8 -*-
# Copyright 2017 Naglis Jonaitis
# License AGPL-3 or later (https://www.gnu.org/licenses/agpl).

from .common import OpenProjectBackendTestCase, get_openproject_mocker


class TestOpenProjectImageImporter(OpenProjectBackendTestCase):

    def setUp(self):
        super(TestOpenProjectImageImporter, self).setUp()
        self.binding = self.env['openproject.res.users'].create({
            'backend_id': self.backend.id,
            'odoo_id': self.env.user.id,
            'image': False,
        })

    def test_image_import(self):
        with get_openproject_mocker():
            self.binding.import_avatar(
                self.backend, 'https://gravatar/avatar', self.binding.id)
        self.assertTrue(self.binding.image)
