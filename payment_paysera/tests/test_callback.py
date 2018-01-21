# -*- coding: utf-8 -*-
# Copyright 2018 Naglis Jonaitis
# License AGPL-3 or later (https://www.gnu.org/licenses/agpl).

import odoo


class TestCallback(odoo.tests.HttpCase):

    def test_cancel_callback_returns_redirect(self):
        resp = self.url_open('/payment/paysera/cancel')
        self.assertTrue(resp.url.endswith('/shop/payment'))
