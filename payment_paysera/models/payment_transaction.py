# Copyright 2018-2019 Naglis Jonaitis
# License AGPL-3 or later (https://www.gnu.org/licenses/agpl).

import logging

from odoo import _, api, fields, models
from odoo.addons.payment.models.payment_acquirer import ValidationError

from .. import paysera, utils

_LOG = logging.getLogger(__name__)


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    @api.model
    def _paysera_form_get_tx_from_data(self, data):
        '''Extracts the order ID from received data.

        Returns the corresponding transaction.'''
        # Decode the encoded parameters and write them into `data` dict.
        data['params'] = utils.decode_form_data(data.get('data', ''))

        reference = data['params'].get('orderid')
        if not reference:
            msg = 'Paysera: missing order ID in received data'
            _LOG.error(msg)
            raise ValidationError(msg)

        txs = self.env['payment.transaction'].search([
            ('reference', '=', reference),
        ])
        if not txs or len(txs) > 1:
            msg = 'Paysera: received data for reference ID: %s' % reference
            if not txs:
                msg += '; no order found'
            else:
                msg += '; multiple orders found'
            _LOG.error(msg)
            raise ValidationError(msg)
        return txs[0]

    @api.multi
    def _paysera_form_get_invalid_parameters(self, data):
        '''Checks received parameters and returns a list of tuples.

        Tuple format: (parameter_name, received_value, expected_value).

        Errors will be raised for each invalid parameter.
        Transaction will not be validated if there is at least one
        invalid parameter.'''
        self.ensure_one()
        self.acquirer_id.ensure_paysera()

        invalid_parameters = []

        def check_keys_not_empty(dict_, keys, example='SOME_VALUE'):
            for key in keys:
                value = dict_.get(key)
                if not value:
                    invalid_parameters.append((key, value, example))

        check_keys_not_empty(data, ('data', 'ss1', 'ss2'))

        params = data.get('params', {})
        check_keys_not_empty(params, ('projectid', 'requestid'))

        the_data = data.get('data')

        ss1_received = data.get('ss1')
        ss1_computed = paysera.md5_sign(
            the_data, self.acquirer_id.paysera_sign_password)
        if not ss1_computed == ss1_received:
            invalid_parameters.append(('ss1', ss1_received, ss1_computed))

        ss2_received = data.get('ss2')
        if not paysera.verify_rsa_signature(ss2_received, the_data):
            invalid_parameters.append(('ss2', ss2_received, 'VALID_SS2'))

        # Check `amount` is the same as stored on transaction.
        amount_received = params.get('amount')
        amount_expected = paysera.get_amount_string(
            self.currency_id, self.amount)
        if amount_received != amount_expected:
            invalid_parameters.append(
                ('amount', amount_received, amount_expected))

        # Check `currency` is the same as stored on transaction.
        currency_received = params.get('currency')
        if currency_received != self.currency_id.name:
            invalid_parameters.append(
                ('currency', currency_received, self.currency_id.name))

        # Check test mode parameter is the same as on acquirer.
        test_mode_received = params.get('test')
        test_mode_expected = (
            '1' if self.acquirer_id.environment == 'test' else '0')
        if test_mode_received != test_mode_expected:
            invalid_parameters.append(
                ('test', test_mode_received, test_mode_expected))

        # Check if `projectid`'s match.
        if not params.get('projectid') == self.acquirer_id.paysera_project_id:
            invalid_parameters.append((
                'projectid',
                params.get('projectid'),
                self.acquirer_id.paysera_project_id,
            ))
        return invalid_parameters

    @api.multi
    def _paysera_validate_paid_amount(self, amount, currency):
        self.ensure_one()
        self.acquirer_id.ensure_paysera()

        if not (amount or currency):
            return True

        amount_expected = paysera.get_amount_string(
            self.currency_id, self.amount)
        currency_expected = self.currency_id.name

        return amount == amount_expected and currency == currency_expected

    @api.multi
    def _paysera_form_validate(self, data):
        self.ensure_one()
        self.acquirer_id.ensure_paysera()

        # Only handle draft and pending transactions.
        if self.state not in ('draft', 'pending'):
            return False

        params = data['params']
        status = params.get('status')
        validate_amount = self.acquirer_id.paysera_validate_paid_amount

        ret_val = True
        tx_values = {
            'acquirer_reference': params.get('requestid', ''),
        }
        if status == paysera.PAYSERA_STATUS_NOT_EXECUTED:
            self._set_transaction_cancel()
            self.write(tx_values)
        elif status == paysera.PAYSERA_STATUS_PAYMENT_SUCCESSFULL:
            paid_amount, paid_currency = (
                params['payamount'], params['paycurrency'])
            if validate_amount and not self._paysera_validate_paid_amount(
                    paid_amount, paid_currency):
                state_msg = _(
                    'The amount/currency (in cents) on the transaction ('
                    '%(transaction_amount)s %(transaction_currency)s) does '
                    'not match the actually paid amount/currency '
                    '(%(paid_amount)s %(paid_currency)s).',
                ) % {
                    'transaction_amount': paysera.get_amount_string(
                        self.currency_id, self.amount),
                    'transaction_currency': self.currency_id.name,
                    'paid_amount': paid_amount,
                    'paid_currency': paid_currency,
                }
                self._set_transaction_error(state_msg)
                self.write(tx_values)
                ret_val = False
            else:
                _LOG.info(
                    'Transaction "%s" sucessfully validated', self.reference)
                tx_values.update(state_message=params.get('paytext', ''))
                self._set_transaction_done()
                self.write(tx_values)
        elif status == paysera.PAYSERA_STATUS_PAYMENT_ACCEPTED:
            self._set_transaction_pending()
            self.write(tx_values)
        elif status == paysera.PAYSERA_STATUS_ADDITIONAL_INFO:
            # NOTE: Currently we do not handle this status.
            pass
        else:
            error = _('Paysera: unknown payment status: %s') % status
            _LOG.error(error)
            self._set_transaction_error(error)
            self.write(tx_values)
            ret_val = False
        return ret_val
