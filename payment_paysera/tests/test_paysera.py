# -*- coding: utf-8 -*-
# Copyright 2018 Naglis Jonaitis
# License AGPL-3 or later (https://www.gnu.org/licenses/agpl).

import unittest
import xml.etree.ElementTree as ET

from odoo.addons.payment.models.payment_acquirer import ValidationError
from odoo.addons.payment.tests.common import PaymentAcquirerCommon
from odoo.tools import mute_logger

from .. import paysera

PAYSERA_PROJECT_ID = '53203'
PAYSERA_SIGN_PASSWORD = b'7324e13b502b18674c59bb2015818e78'
PAYSERA_TEST_DATA = (
    b'bGFuZz0mcmVmZXJlbmNlPVNPMDEyJnBfY2l0eT1TaW4rQ2l0eSZwcm9qZWN0aWQ9NTMyMDMm'
    b'Y3VycmVuY3lfaWQ9MSZjdXJyZW5jeT1FVVImcF9lbWFpbD1ub3JiZXJ0LmJ1eWVyJTQwZXhh'
    b'bXBsZS5jb20mcF9zdHJlZXQ9SHVnZStTdHJlZXQrMiUyRjU0MyZwYXJ0bmVyPXJlcy5wYXJ0'
    b'bmVyJTI4MyUyQyUyOSZwX2NvdW50cnljb2RlPUJFJm9yZGVyaWQ9U08wMTImY291bnRyeT1C'
    b'RSZwX2ZpcnN0bmFtZT1CdXllciZwX3ppcD0xMDAwJmFtb3VudD0zMjAwMCZ2ZXJzaW9uPTEu'
    b'NiZwX2xhc3RuYW1lPU5vcmJlcnQmdGVzdD0xJnJldHVybl91cmw9JTJGc2hvcCUyRnBheW1l'
    b'bnQlMkZ2YWxpZGF0ZSZwYXltZW50PWRpcmVjdGViYmUmcGF5dGV4dD1VJUM1JUJFc2FreW1h'
    b'cytuciUzQStTTzAxMitodHRwJTNBJTJGJTJGbG9jYWxob3N0K3Byb2pla3RlLislMjhQYXJk'
    b'YXYlQzQlOTdqYXMlM0ErTmFnbGlzK0pvbmFpdGlzJTI5JnN0YXR1cz0xJnJlcXVlc3RpZD02'
    b'MzA1NzE5NCZwYXlhbW91bnQ9MzIwMDAmcGF5Y3VycmVuY3k9RVVSJm5hbWU9VUFCJnN1cmVu'
    b'YW1lPU1vayVDNCU5N2ppbWFpLmx0'
)
PAYSERA_TEST_SS1 = 'e899774b6649616cc841113512111120'
PAYSERA_TEST_SS2 = (
    'uRdNt8ugz2JhxiEeS8BNUBrujDwsfMwgY7iugUcFbqQVg-M2VfICrGt3kVyEP9IDx4ywxa-w'
    'w85UPFlUlutZnslodkb7cmdNidw9CBJxKdp0NK7ESlRWiSAnVqT8LdgZP42IU2M3OyIs1nM9'
    'TMG3GevU04FbCBTCg_NM2EGUolc='
)
PAYSERA_TEST_POST_DATA = {
    'data': PAYSERA_TEST_DATA,
    'ss1': PAYSERA_TEST_SS1,
    'ss2': PAYSERA_TEST_SS2,
}


class PayseraUtils(unittest.TestCase):

    def test_get_form_values(self):
        test_data = {
            'ačiū': 'prašom',
        }
        form_values = paysera.get_form_values(test_data, PAYSERA_SIGN_PASSWORD)
        self.assertEqual(
            form_values['signature'],
            '78663a229e34a6f0b1067779d0fe8ba0',
            'Wrong signature',
        )

    def test_validate_rsa_signature_valid_signature_returns_True(self):
        self.assertTrue(paysera.verify_rsa_signature(
            PAYSERA_TEST_SS2, PAYSERA_TEST_DATA))

    def test_validate_rsa_signature_tampered_data_returns_False(self):
        paysera_test_data_tampered = PAYSERA_TEST_DATA[:-1]
        self.assertFalse(paysera.verify_rsa_signature(
            PAYSERA_TEST_SS2, paysera_test_data_tampered))


class PayseraCommon(PaymentAcquirerCommon):

    def setUp(self):
        super(PayseraCommon, self).setUp()
        self.tx_obj = self.env['payment.transaction']
        self.acquirer = self.env.ref(
            'payment_paysera.payment_acquirer_paysera')

        self.tx_values = {
            'reference': 'SO012',
            'currency': self.currency_euro.id,
            'amount': 320.00,
        }
        self.acquirer.write({
            'paysera_project_id': '53203',
            'paysera_sign_password': '7323e13b502b18674c59bb2015818e78',
        })

    def assertTestEnv(self):
        self.assertEqual(
            self.acquirer.environment, 'test', 'Not a test environment')

    def test_form_render(self):
        self.assertTestEnv()

        res = self.acquirer.render(
            'SO012', 320.00, self.currency_euro.id, values=self.buyer_values)

        root = ET.fromstring(res)
        self.assertEqual(
            root.attrib.get('action'),
            paysera.PAYSERA_API_URL,
            'Wrong form POST url',
        )

    @mute_logger('odoo.addons.payment_paysera.models.payment_transaction',
                 'ValidationError')
    def test_transaction_management(self):
        '''
        PAYSERA_TEST_DATA = {
            'lang': '',
            'reference': 'SO012',
            'p_city': 'Sin City',
            'projectid': '53203',
            'currency_id': 1,
            'currency': 'EUR',
            'p_email': 'norbert.buyer@example.com',
            'p_street': 'Huge Street 2/543',
            'cancelurl': 'http://localhost:8069/payment/paysera/cancel',
            'partner': res.partner(3,),
            'p_countrycode': 'BE',
            'callbackurl': 'http://localhost:8069/payment/paysera/callback',
            'orderid': 'SO012',
            'country': 'BE',
            'p_firstname': 'Buyer',
            'p_zip': '1000',
            'amount': '32000',
            'version': '1.6',
            'p_lastname': 'Norbert',
            'test': '1',
            'accepturl': 'http://localhost:8069/payment/paysera/accept',
            'return_url': '/shop/payment/validate'
        }
        '''

        self.assertTestEnv()

        # Should raise an error about non-existent order ID.
        with self.assertRaises(ValidationError):
            self.tx_obj.form_feedback(PAYSERA_TEST_POST_DATA, 'paysera')

        tx = self.tx_obj.create({
            'amount': 32000,
            'acquirer_id': self.acquirer.id,
            'currency_id': self.currency_euro.id,
            'reference': 'SO012',
            'partner_id': self.buyer_id,
        })

        # Validate again.
        self.tx_obj.form_feedback(PAYSERA_TEST_POST_DATA, 'paysera')

        # Check transaction state.
        self.assertEqual(
            tx.state, 'done',
            'paysera: validation did not put tx into done state')
