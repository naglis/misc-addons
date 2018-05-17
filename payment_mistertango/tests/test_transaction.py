# Copyright 2018 Naglis Jonaitis
# License AGPL-3 or later (https://www.gnu.org/licenses/agpl).

import base64
import uuid

from odoo import fields
from odoo.addons.payment.models.payment_acquirer import ValidationError
from odoo.tools import mute_logger

from .common import (
    TEST_AMOUNT,
    TEST_SECRET_KEY,
    TestMistertangoCommon,
    fake_callback,
    inc_byte,
)
from ..mistertango import (
    MISTERTANGO_PAYMENT_STATUS_CONFIRMED,
    MISTERTANGO_PAYMENT_STATUS_NOT_CONFIRMED,
)


class TestPaymentTransaction(TestMistertangoCommon):

    def feedback(self, description, override_data=None, **kwargs):
        data = override_data or fake_callback(description, **kwargs)
        return self.env['payment.transaction'].form_feedback(
            data, 'mistertango')

    def test_form_feedback_transaction_is_validated(self):
        status = self.feedback(self.tx_1.reference)
        self.assertTrue(status)
        self.assertEqual(self.tx_1.state, 'done')

    def test_form_feedback_callback_uuid_is_set_on_transaction(self):
        callback_uuid = str(uuid.uuid4())
        self.feedback(self.tx_1.reference, callback_uuid=callback_uuid)
        self.assertEqual(self.tx_1.mistertango_callback_uuid, callback_uuid)

    def test_form_feedback_validation_date_is_set_on_transaction(self):
        self.feedback(self.tx_1.reference)
        self.assertRegex(
            self.tx_1.date_validate,
            r'^%s \d\d:\d\d:\d\d$' % fields.Date.today())

    def test_form_feedback_acquirer_reference_is_set_on_transaction(self):
        acquirer_reference = 'FOOBAR'
        self.feedback(
            self.tx_1.reference, acquirer_reference=acquirer_reference)
        self.assertEqual(self.tx_1.acquirer_reference, acquirer_reference)

    def test_form_feedback_payment_type_is_set_on_transaction(self):
        payment_type = 'BITCOIN'
        self.feedback(self.tx_1.reference, payment_type=payment_type)
        self.assertEqual(self.tx_1.mistertango_payment_type, payment_type)

    def test_callback_status_not_confirmed_transaction_is_pending(self):
        '''Test that transaction is pending if status in the callback is not
        confirmed.'''
        status = self.feedback(
            self.tx_1.reference,
            status=MISTERTANGO_PAYMENT_STATUS_NOT_CONFIRMED)
        self.assertTrue(status)
        self.assertEqual(self.tx_1.state, 'pending')

    def test_callback_wrong_secret_key_used_feedback_raises_exception(self):
        with self.assertRaises(ValueError):
            self.feedback(self.tx_1.reference, override_data=fake_callback(
                self.tx_1.reference,
                secret_key=inc_byte(TEST_SECRET_KEY),
                status=MISTERTANGO_PAYMENT_STATUS_CONFIRMED),
            )

    def test_hash_value_changed_raises_exception(self):
        data = fake_callback(
            self.tx_1.reference,
            secret_key=inc_byte(TEST_SECRET_KEY),
            status=MISTERTANGO_PAYMENT_STATUS_CONFIRMED)
        data.update(
            hash=base64.b64encode(
                inc_byte(base64.b64decode(data['hash']))).decode('ascii'))
        with self.assertRaises(ValueError):
            self.feedback(self.tx_1.reference, override_data=data)

    @mute_logger('odoo.addons.payment_mistertango.models.payment_transaction')
    def test_form_feedback_missing_reference_not_ok(self):
        with self.assertRaises(ValidationError):
            self.assertFalse(self.feedback(''))

    @mute_logger('odoo.addons.payment.models.payment_acquirer')
    def test_form_feedback_amount_mismatch_one_cent_not_ok(self):
        self.assertFalse(
            self.feedback(self.tx_1.reference, amount=TEST_AMOUNT - 0.01))

    @mute_logger('odoo.addons.payment.models.payment_acquirer')
    def test_form_feedback_amount_mismatch_negative_not_ok(self):
        self.assertFalse(
            self.feedback(self.tx_1.reference, amount=-TEST_AMOUNT))

    @mute_logger('odoo.addons.payment.models.payment_acquirer')
    def test_form_feedback_currency_mismatch_not_ok(self):
        self.assertFalse(self.feedback(self.tx_1.reference, currency='USD'))

    @mute_logger('odoo.addons.payment.models.payment_acquirer')
    def test_form_feedback_empty_callback_uuid_not_ok(self):
        self.assertFalse(self.feedback(self.tx_1.reference, callback_uuid=''))

    @mute_logger('odoo.addons.payment.models.payment_acquirer')
    def test_form_feedback_unknown_status_not_ok(self):
        self.assertFalse(self.feedback(self.tx_1.reference, status='FOOBAR'))

    @mute_logger('odoo.addons.payment.models.payment_acquirer')
    def test_form_feedback_reference_mismatch_in_encrypted_data_not_ok(self):
        data = fake_callback(self.tx_1.reference + 'FOO')
        data.update(custom=fake_callback(self.tx_1.reference)['custom'])
        self.assertFalse(
            self.feedback(self.tx_1.reference, override_data=data))

    def test_same_callback_twice_transaction_not_changed(self):
        '''Test that a callback with the same UUID does not affect the
        transaction.'''
        common_kwargs = {
            'callback_uuid': str(uuid.uuid4()),
        }
        status_1 = self.feedback(
            self.tx_1.reference,
            status=MISTERTANGO_PAYMENT_STATUS_NOT_CONFIRMED,
            **common_kwargs)
        self.assertTrue(status_1)
        date_validate = self.tx_1.date_validate
        state = self.tx_1.state

        status_2 = self.feedback(
            self.tx_1.reference,
            status=MISTERTANGO_PAYMENT_STATUS_CONFIRMED,
            **common_kwargs)
        self.assertTrue(
            status_2,
            msg='Return status is not the same as after the first callback')
        self.assertEqual(
            self.tx_1.state, state,
            msg='Transaction state changed after second callback')
        self.assertEqual(
            self.tx_1.date_validate, date_validate,
            msg='Transaction validation date changed after second callback')
