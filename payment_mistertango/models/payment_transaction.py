# -*- coding: utf-8 -*-
# Copyright 2018-2019 Naglis Jonaitis
# License AGPL-3 or later (https://www.gnu.org/licenses/agpl).

import json
import logging

from odoo import api, fields, models
from odoo.addons.payment.models.payment_acquirer import ValidationError

from ..mistertango import (
    MISTERTANGO_PAYMENT_STATUSES,
    MISTERTANGO_PAYMENT_STATUS_CONFIRMED,
    MISTERTANGO_PAYMENT_STATUS_NOT_CONFIRMED,
    MISTERTANGO_PAYMENT_TYPES,
    decrypt,
)

_logger = logging.getLogger(__name__)


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    mistertango_callback_uuid = fields.Char(
        string='Callback UUID',
        readonly=True,
    )
    mistertango_payment_type = fields.Selection(
        string='Payment Type',
        selection=list(MISTERTANGO_PAYMENT_TYPES.items()),
        readonly=True,
        help='Indicates which method was used to complete the payment.',
    )

    @api.model
    def _mistertango_form_get_tx_from_data(self, data):
        '''Extracts the order ID from received data.

        Returns the corresponding transaction.'''

        # We use the plaintext data here as we do not yet know which acquirer
        # is being used.
        custom_data = json.loads(data['custom'])

        reference = custom_data.get('description')
        if not reference:
            msg = u'Order ID missing in callback data'
            _logger.error(msg)
            raise ValidationError(msg)

        txs = self.env['payment.transaction'].search([
            ('reference', '=', reference),
        ])
        if not txs or len(txs) > 1:
            raise ValidationError(
                u'Callback data received for reference ID: "%s", '
                u'either zero or multiple order found' % reference)
        return txs[0]

    @api.multi
    def _mistertango_form_get_invalid_parameters(self, data):
        '''Checks received parameters and returns a list of tuples.

        Tuple format: (parameter_name, received_value, expected_value).

        Transaction will not be validated if there is at least one
        invalid parameter.'''
        self.ensure_one()

        invalid_parameters = []

        def check_keys_not_empty(dict_, keys, expected='SOME_VALUE'):
            for key in keys:
                value = dict_.get(key)
                if not value:
                    invalid_parameters.append((key, value, expected))

        def check_same_values(d1, d2, keys):
            for key in keys:
                value1, value2 = d1.get(key), d2.get(key)
                if not value1 == value2:
                    invalid_parameters.append((key, value1, value2))

        check_keys_not_empty(data, ('callback_uuid', 'custom', 'hash'))

        # By 'safe' below is meant for data which came from the encrypted hash,
        # not that it is actually safe (ie. authenticated).

        # Decrypt and load custom data from 'hash'.
        secret_key = self.acquirer_id.mistertango_secret_key.encode('utf-8')
        unsafe_data = data
        safe_data = json.loads(decrypt(unsafe_data['hash'], secret_key))
        unsafe_custom = json.loads(unsafe_data['custom'])
        safe_custom = json.loads(safe_data['custom'])

        check_keys_not_empty(safe_custom, ('description',))
        check_same_values(data, safe_data, ['callback_uuid'])

        if not safe_custom['description'] == self.reference:
            invalid_parameters.append((
                'description', safe_custom['description'], self.reference))

        safe_payment_data = safe_custom['data']
        if not safe_payment_data['currency'] == self.currency_id.name:
            invalid_parameters.append((
                'currency',
                safe_payment_data['currency'], self.currency_id.name))

        check_same_values(safe_custom, unsafe_custom, ['description'])
        check_same_values(
            safe_payment_data, unsafe_custom.get('data', {}),
            ['currency', 'amount', 'status'])

        amount = float(safe_payment_data['amount'])
        if not self.currency_id.compare_amounts(self.amount, amount) == 0:
            invalid_parameters.append(('amount', amount, self.amount))

        if safe_payment_data['status'] not in MISTERTANGO_PAYMENT_STATUSES:
            invalid_parameters.append((
                'status', safe_payment_data['status'],
                MISTERTANGO_PAYMENT_STATUSES))

        return invalid_parameters

    def _mistertango_form_validate(self, data):
        self.ensure_one()
        callback_uuid = data['callback_uuid']
        # This callback was already processed, do nothing.
        if self.mistertango_callback_uuid == callback_uuid:
            return True

        secret_key = self.acquirer_id.mistertango_secret_key.encode('utf-8')
        safe_data = json.loads(decrypt(data['hash'], secret_key))
        custom = json.loads(safe_data['custom'])
        payment_data = custom['data']

        status = payment_data['status']
        values = {
            'mistertango_callback_uuid': callback_uuid,
            'acquirer_reference': payment_data['description'],
            'date_validate': fields.Datetime.now(),
        }
        if status == MISTERTANGO_PAYMENT_STATUS_CONFIRMED:
            values.update(state='done')
        elif status == MISTERTANGO_PAYMENT_STATUS_NOT_CONFIRMED:
            values.update(state='pending')

        payment_type = custom.get('type')
        if payment_type in MISTERTANGO_PAYMENT_TYPES:
            values.update(mistertango_payment_type=payment_type)

        self.write(values)
        return True
