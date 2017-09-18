# -*- coding: utf-8 -*-

import odoo


class TestCallback(odoo.tests.HttpCase):

    def test_cancel_callback_returns_redirect(self):
        resp = self.url_open('/payment/paysera/cancel')
        self.assertTrue(resp.geturl().endswith('/shop/payment'))
