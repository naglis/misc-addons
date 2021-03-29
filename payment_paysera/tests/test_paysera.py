# Copyright 2018-2019 Naglis Jonaitis
# License AGPL-3 or later (https://www.gnu.org/licenses/agpl).

import collections
import unittest
import xml.etree.ElementTree as ET

from mock import patch
from odoo import exceptions
from odoo.addons.payment.models.payment_acquirer import ValidationError
from odoo.addons.payment.tests.common import PaymentAcquirerCommon
from odoo.tests import common
from odoo.tools import mute_logger

from .. import paysera

PAYSERA_PROJECT_ID = '53203'
PAYSERA_SIGN_PASSWORD_1 = '7323e13b502b18674c59bb2015818e78'
PAYSERA_SIGN_PASSWORD_2 = '7324e13b502b18674c59bb2015818e78'
PAYSERA_TEST_DICT = collections.OrderedDict([
    ('lang', ''),
    ('reference', 'SO012'),
    ('p_city', 'Sin City'),
    ('projectid', '53203'),
    ('currency_id', '1'),
    ('currency', 'EUR'),
    ('p_email', 'norbert.buyer@example.com'),
    ('p_street', 'Huge Street 2/543'),
    ('partner', 'res.partner(3,)'),
    ('p_countrycode', 'BE'),
    ('orderid', 'SO012'),
    ('country', 'BE'),
    ('p_firstname', 'Buyer'),
    ('p_zip', '1000'),
    ('amount', '32000'),
    ('version', '1.6'),
    ('p_lastname', 'Norbert'),
    ('test', '1'),
    ('return_url', '/shop/payment/validate'),
    ('payment', 'directebbe'),
    (
        'paytext',
        'Užsakymas nr: SO012 http://localhost projekte. (Pardavėjas: Naglis '
        'Jonaitis)',
    ),
    ('status', '1'),
    ('requestid', '63057194'),
    ('payamount', '32000'),
    ('paycurrency', 'EUR'),
    ('name', 'UAB'),
    ('surename', 'Mokėjimai.lt'),
])
PAYSERA_TEST_DATA = paysera.get_form_values(
    PAYSERA_TEST_DICT, PAYSERA_SIGN_PASSWORD_1)['data']
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
LOGGER_NAME_ACQUIRER = 'odoo.addons.payment.models.payment_acquirer'
LOGGER_NAME_MODELS = 'odoo.models'


def dummy_verify_rsa_signature(signature, data):
    return True


class PayseraUtils(unittest.TestCase):

    def test_get_form_values(self):
        test_data = {
            'ačiū': 'prašom',
        }
        form_values = paysera.get_form_values(
            test_data, PAYSERA_SIGN_PASSWORD_2)
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
        self.acquirer.write({
            'paysera_project_id': '53203',
            'paysera_sign_password': PAYSERA_SIGN_PASSWORD_1,
        })

    def assertTestEnv(self):
        self.assertEqual(
            self.acquirer.environment, 'test', 'Not a test environment')

    def create_transaction(self, **overrides):
        values = {
            'amount': 320.0,
            'acquirer_id': self.acquirer.id,
            'currency_id': self.currency_euro.id,
            'reference': 'SO012',
            'partner_id': self.buyer_id,
        }
        values.update(overrides)
        return self.tx_obj.create(values)

    def test_form_render(self):
        self.assertTestEnv()

        res = self.acquirer.render(
            'SO012', 320.00, self.currency_euro.id, values=self.buyer_values)

        root = ET.fromstring(res)

        data_set = root.findall('input[@name="data_set"]')
        self.assertEqual(
            len(data_set),
            1,
            'paysera: Found %d "data_set" input instead of 1' % len(data_set),
        )
        self.assertEqual(
            data_set[0].get('data-action-url'),
            paysera.PAYSERA_API_URL,
            'Wrong form POST url',
        )

    @mute_logger('odoo.addons.payment_paysera.models.payment_transaction',
                 'ValidationError')
    def test_transaction_management(self):
        self.assertTestEnv()

        with self.assertRaisesRegex(
            ValidationError,
            r'.*received data for reference ID.*no order found.*',
        ):
            self.tx_obj.form_feedback(PAYSERA_TEST_POST_DATA, 'paysera')

        tx = self.create_transaction()

        # Validate again.
        self.tx_obj.form_feedback(PAYSERA_TEST_POST_DATA, 'paysera')

        # Check transaction state.
        self.assertEqual(
            tx.state, 'done',
            'paysera: validation did not put tx into done state')

    def test_amount_mismatch_transaction_not_validated(self):
        self.assertTestEnv()
        tx = self.create_transaction(amount=319.99)

        with mute_logger(LOGGER_NAME_ACQUIRER):
            self.tx_obj.form_feedback(PAYSERA_TEST_POST_DATA, 'paysera')

        # Check transaction was not validated.
        self.assertEqual(tx.state, 'draft')
        # Set the correct amount.
        tx.amount = 320.0
        # Validate again.
        self.tx_obj.form_feedback(PAYSERA_TEST_POST_DATA, 'paysera')
        # Check transaction is not validated.
        self.assertEqual(tx.state, 'done')

    def test_currency_mismatch_transaction_not_validated(self):
        self.assertTestEnv()
        tx = self.create_transaction(currency_id=self.ref('base.USD'))

        with mute_logger(LOGGER_NAME_ACQUIRER):
            self.tx_obj.form_feedback(PAYSERA_TEST_POST_DATA, 'paysera')

        # Check transaction was not validated.
        self.assertEqual(tx.state, 'draft')
        # Set the correct currency.
        tx.currency_id = self.currency_euro
        # Validate again.
        self.tx_obj.form_feedback(PAYSERA_TEST_POST_DATA, 'paysera')
        # Check transaction is not validated.
        self.assertEqual(tx.state, 'done')

    def test_test_mode_mismatch_transaction_not_validated(self):
        tx = self.create_transaction()
        tx.acquirer_id.environment = 'prod'

        with mute_logger(LOGGER_NAME_ACQUIRER):
            self.tx_obj.form_feedback(PAYSERA_TEST_POST_DATA, 'paysera')

        # Check transaction was not validated.
        self.assertEqual(tx.state, 'draft')
        # Set the correct acquirer environment.
        tx.acquirer_id.environment = 'test'
        # Validate again.
        self.tx_obj.form_feedback(PAYSERA_TEST_POST_DATA, 'paysera')
        # Check transaction is not validated.
        self.assertEqual(tx.state, 'done')

    def test_transaction_in_error_mode_is_not_validated(self):
        self.assertTestEnv()
        tx = self.create_transaction(state='error')

        self.tx_obj.form_feedback(PAYSERA_TEST_POST_DATA, 'paysera')

        self.assertEqual(tx.state, 'error')

    def test_paid_amount_mismatch_transaction_set_to_error_state(self):
        self.acquirer.paysera_validate_paid_amount = True
        test_dict = PAYSERA_TEST_DICT.copy()
        test_dict.update({
            'payamount': '32001',
        })
        post_data = paysera.get_form_values(
            test_dict, self.acquirer.paysera_sign_password)
        post_data.update({
            'ss1': post_data.pop('signature'),
            'ss2': 'foo',
        })
        tx = self.create_transaction()

        with patch.object(
                paysera, 'verify_rsa_signature', dummy_verify_rsa_signature):
            self.tx_obj.form_feedback(post_data, 'paysera')

        self.assertEqual(tx.state, 'error')
        self.assertRegex(
            tx.state_message, r'.*amount.*does not match.*')

    def test_paid_currency_mismatch_transaction_set_to_error_state(self):
        self.acquirer.paysera_validate_paid_amount = True
        test_dict = PAYSERA_TEST_DICT.copy()
        test_dict.update({
            'paycurrency': 'USD',
        })
        post_data = paysera.get_form_values(
            test_dict, self.acquirer.paysera_sign_password)
        post_data.update({
            'ss1': post_data.pop('signature'),
            'ss2': 'foo',
        })
        tx = self.create_transaction()

        with patch.object(
                paysera, 'verify_rsa_signature', dummy_verify_rsa_signature):
            self.tx_obj.form_feedback(post_data, 'paysera')

        self.assertEqual(tx.state, 'error')
        self.assertRegex(
            tx.state_message, r'.*currency.*does not match.*')

    def test_get_paysera_redirect_urls(self):
        """Test paysera redirect urls with website domain.

        In this case web.base.url is different than website domain.
        """
        my_website_domain = 'http://www.example.com'
        website = self.env.ref('website.website2')
        website.domain = my_website_domain
        self.acquirer.website_id = website.id
        expected_result = {
            'accepturl': my_website_domain + '/payment/paysera/accept',
            'cancelurl': my_website_domain + 'payment/paysera/cancel',
            'callbackurl': my_website_domain + 'payment/paysera/callback'
        }
        self.assertEqual(
            self.acquirer._get_paysera_redirect_urls(), expected_result
        )


class TestPayseraAccess(common.TransactionCase):

    def setUp(self):
        super(TestPayseraAccess, self).setUp()
        self.user = self.env.ref('base.user_demo')
        self.group_employee = self.env.ref('base.group_user')
        self.group_admin = self.env.ref('base.group_system')
        self.user.write({
            'groups_id': [
                (5,),
                (4, self.group_employee.id),
            ],
        })
        self.acquirer = self.env.ref(
            'payment_paysera.payment_acquirer_paysera').sudo(user=self.user.id)

    @mute_logger(LOGGER_NAME_MODELS)
    def test_employee_cannot_read_project_id_and_sign_password(self):
        with self.assertRaises(exceptions.AccessError):
            self.acquirer.read(['paysera_project_id'])
        with self.assertRaises(exceptions.AccessError):
            self.acquirer.read(['paysera_sign_password'])

    @mute_logger(LOGGER_NAME_MODELS)
    def test_employee_cannot_write_project_id_and_sign_password(self):
        with self.assertRaises(exceptions.AccessError):
            self.acquirer.write({
                'paysera_project_id': '123',
            })
        with self.assertRaises(exceptions.AccessError):
            self.acquirer.write({
                'paysera_sign_password': 'foo',
            })

    def test_admin_employee_can_read_project_id_and_sign_password(self):
        self.user.write({
            'groups_id': [
                (4, self.group_admin.id),
            ],
        })
        try:
            self.acquirer.read(['paysera_project_id'])
        except exceptions.AccessError:
            self.fail('Admin user cannot read `paysera_project_id`.')
        try:
            self.acquirer.read(['paysera_sign_password'])
        except exceptions.AccessError:
            self.fail('Admin user cannot read `paysera_sign_password`.')

    def test_admin_employee_can_write_project_id_and_sign_password(self):
        self.user.write({
            'groups_id': [
                (4, self.group_admin.id),
            ],
        })
        try:
            self.acquirer.write({'paysera_project_id': 'foo'})
        except exceptions.AccessError:
            self.fail('Admin user cannot write `paysera_project_id`.')
        try:
            self.acquirer.write({'paysera_sign_password': '123'})
        except exceptions.AccessError:
            self.fail('Admin user cannot write `paysera_sign_password`.')


class TestGetAmountString(common.SingleTransactionCase):

    def test_amount_formatted_correctly(self):
        EUR = self.env.ref('base.EUR')
        test_cases = [
            (EUR, 0.0, '0'),
            (EUR, 1.00, '100'),
            (EUR, -1.23, '-123'),
            (EUR, 1.1 + 2.2, '330'),
            (EUR, 316.46, '31646'),
            (EUR, 1.11999999, '112'),
            (EUR, 39.0 / 100.0 + 1, '139'),
        ]
        for currency, amount, expected in test_cases:
            actual = paysera.get_amount_string(currency, amount)
            self.assertEqual(expected, actual)
