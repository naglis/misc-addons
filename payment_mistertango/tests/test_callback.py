# Copyright 2018 Naglis Jonaitis
# License AGPL-3 or later (https://www.gnu.org/licenses/agpl).

import unittest

from odoo import tests
from odoo.tools import mute_logger

from .common import (
    fake_callback,
    in_worker_mode,
)


@unittest.skipIf(
    in_worker_mode(), 'HTTP test cases do not work in worker mode')
class TestCallback(tests.HttpCase):

    @mute_logger('odoo.addons.payment_mistertango.controllers.main')
    def test_not_existing_so_not_ok(self):
        data = fake_callback('non-existing-so')
        resp = self.url_open(
            '/payment/mistertango/callback', data=data, timeout=30)
        self.assertEqual(resp.content, b'NOT OK')

    def test_callback_uuid_already_handled_returns_ok(self):
        tx = self.browse_ref('payment_mistertango.transaction_2')
        data = fake_callback(
            tx.reference, callback_uuid=tx.mistertango_callback_uuid)
        resp = self.url_open(
            '/payment/mistertango/callback', data=data, timeout=30)
        self.assertEqual(resp.content, b'OK')
