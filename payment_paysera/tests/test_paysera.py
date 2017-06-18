# -*- coding: utf-8 -*-

import unittest
import xml.etree.ElementTree as ET

from openerp.addons.payment.models.payment_acquirer import ValidationError
from openerp.addons.payment.tests.common import PaymentAcquirerCommon
from openerp.tools import mute_logger

from .. import paysera

PAYSERA_PROJECT_ID = '53203'
PAYSERA_SIGN_PASSWORD = '7324e13b502b18674c59bb2015818e78'
PAYSERA_TEST_DATA = (
    u'bGFuZz0mcmVmZXJlbmNlPVNPMDEyJnBfY2l0eT1TaW4rQ2l0eSZwcm9qZWN0aWQ9NTMyMDMm'
    u'Y3VycmVuY3lfaWQ9MSZjdXJyZW5jeT1FVVImcF9lbWFpbD1ub3JiZXJ0LmJ1eWVyJTQwZXhh'
    u'bXBsZS5jb20mcF9zdHJlZXQ9SHVnZStTdHJlZXQrMiUyRjU0MyZwYXJ0bmVyPXJlcy5wYXJ0'
    u'bmVyJTI4MyUyQyUyOSZwX2NvdW50cnljb2RlPUJFJm9yZGVyaWQ9U08wMTImY291bnRyeT1C'
    u'RSZwX2ZpcnN0bmFtZT1CdXllciZwX3ppcD0xMDAwJmFtb3VudD0zMjAwMCZ2ZXJzaW9uPTEu'
    u'NiZwX2xhc3RuYW1lPU5vcmJlcnQmdGVzdD0xJnJldHVybl91cmw9JTJGc2hvcCUyRnBheW1l'
    u'bnQlMkZ2YWxpZGF0ZSZwYXltZW50PWRpcmVjdGViYmUmcGF5dGV4dD1VJUM1JUJFc2FreW1h'
    u'cytuciUzQStTTzAxMitodHRwJTNBJTJGJTJGbG9jYWxob3N0K3Byb2pla3RlLislMjhQYXJk'
    u'YXYlQzQlOTdqYXMlM0ErTmFnbGlzK0pvbmFpdGlzJTI5JnN0YXR1cz0xJnJlcXVlc3RpZD02'
    u'MzA1NzE5NCZwYXlhbW91bnQ9MzIwMDAmcGF5Y3VycmVuY3k9RVVSJm5hbWU9VUFCJnN1cmVu'
    u'YW1lPU1vayVDNCU5N2ppbWFpLmx0'
)
PAYSERA_TEST_SS1 = u'e899774b6649616cc841113512111120'
PAYSERA_TEST_SS2 = (
    u'uRdNt8ugz2JhxiEeS8BNUBrujDwsfMwgY7iugUcFbqQVg-M2VfICrGt3kVyEP9IDx4ywxa-w'
    u'w85UPFlUlutZnslodkb7cmdNidw9CBJxKdp0NK7ESlRWiSAnVqT8LdgZP42IU2M3OyIs1nM9'
    u'TMG3GevU04FbCBTCg_NM2EGUolc='
)
PAYSERA_TEST_POST_DATA = {
    'data': PAYSERA_TEST_DATA,
    'ss1': PAYSERA_TEST_SS1,
    'ss2': PAYSERA_TEST_SS2,
}


class PayseraUtils(unittest.TestCase):

    def test_get_form_values(self):
        test_data = {
            u'ačiū': u'prašom',
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
            'currency': self.currency_euro,
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
            'SO012', 320.00, self.currency_euro_id, partner_id=None,
            partner_values=self.buyer_values)[0]

        root = ET.fromstring(res)
        self.assertEqual(
            root.attrib.get('action'),
            paysera.PAYSERA_API_URL,
            'Wrong form POST url',
        )

    @mute_logger('openerp.addons.payment_paysera.models.payment_transaction',
                 'ValidationError')
    def test_transaction_management(self):
        self.assertTestEnv()

        '''
        FORM_VALUES = {
            'lang': '',
            'reference': u'SO012',
            'p_city': 'Sin City',
            'projectid': '53203',
            'currency_id': 1,
            'currency': u'EUR',
            'p_email': 'norbert.buyer@example.com',
            'p_street': 'Huge Street 2/543',
            'cancelurl': 'http://localhost:8069/payment/paysera/cancel',
            'partner': res.partner(3,),
            'p_countrycode': u'BE',
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

        # Should raise an error about non-existent order ID.
        with self.assertRaises(ValidationError):
            self.tx_obj.form_feedback(PAYSERA_TEST_POST_DATA, 'paysera')

        tx = self.tx_obj.create({
            'amount': 32000,
            'acquirer_id': self.acquirer.id,
            'currency_id': self.currency_euro_id,
            'reference': 'SO012',
            'partner_id': self.buyer_id,
        })

        # Validate again.
        self.tx_obj.form_feedback(PAYSERA_TEST_POST_DATA, 'paysera')

        # Check transaction state.
        self.assertEqual(
            tx.state, 'done',
            'paysera: validation did not put tx into done state')
