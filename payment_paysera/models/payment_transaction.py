# -*- coding: utf-8 -*-

import base64
import logging
import urlparse

from odoo import _, api, fields, models
from odoo.addons.payment.models.payment_acquirer import ValidationError

from .. import paysera

_LOG = logging.getLogger(__name__)


def decode_form_data(encoded_data):
    '''
    Decodes base64 encoded string, parses it and returns a dict of parameters

    :param encoded_data: base64 encoded URL parameters list
    :type encoded_data: str
    :rtype: dict
    '''
    decoded = base64.b64decode(encoded_data.encode('ascii'), altchars='-_')
    parsed = urlparse.parse_qsl(decoded, keep_blank_values=True)
    return {k: v.decode('utf-8') for k, v in parsed}


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    @api.model
    def _paysera_form_get_tx_from_data(self, data):
        '''Extracts the order ID from received data.

        Returns the corresponding transaction.'''
        # Decode the encoded parameters and write them into `data` dict.
        data['params'] = decode_form_data(data.get('data', ''))

        reference = data['params'].get('orderid')
        if not reference:
            msg = u'Paysera: missing order ID in received data'
            _LOG.error(msg)
            raise ValidationError(msg)

        txs = self.env['payment.transaction'].search([
            ('reference', '=', reference)
        ])
        if not txs or len(txs) > 1:
            msg = u'Paysera: received data for reference ID: %s' % reference
            if not txs:
                msg += u'; no order found'
            else:
                msg += u'; multiple orders found'
            _LOG.error(msg)
            raise ValidationError(msg)
        return txs[0]

    @api.model
    def _paysera_form_get_invalid_parameters(self, tx, data):
        '''Checks received parameters and returns a list of tuples.

        Tuple format: (parameter_name, received_value, expected_value).

        Errors will be raised for each invalid parameter.
        Transaction will not be validated if there is at least one
        invalid parameter.'''
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
            the_data, tx.acquirer_id.paysera_sign_password)
        if not ss1_computed == ss1_received:
            invalid_parameters.append(('ss1', ss1_received, ss1_computed))

        ss2_received = data.get('ss2')
        if not paysera.verify_rsa_signature(ss2_received, the_data):
            invalid_parameters.append(('ss2', ss2_received, 'VALID_SS2'))

        # Check if `projectid`'s match.
        if not params.get('projectid') == tx.acquirer_id.paysera_project_id:
            invalid_parameters.append((
                'projectid',
                params.get('projectid'),
                tx.acquirer_id.paysera_project_id
            ))
        return invalid_parameters

    @api.model
    def _paysera_form_validate(self, tx, data):
        # Transaction has already been completed or canceled.
        # We should not handle this request.
        if tx.state in ('done', 'cancel'):
            return False

        params = data['params']
        status = params.get('status', paysera.PAYSERA_STATUS_PAYMENT_ACCEPTED)

        ret_val = True
        if status == paysera.PAYSERA_STATUS_NOT_EXECUTED:
            tx.write({
                'state': 'cancel',
            })
        elif status == paysera.PAYSERA_STATUS_PAYMENT_SUCCESSFULL:
            _LOG.info(u'Order ID %s paid' % params.get('orderid'))
            tx.write({
                'state': 'done',
                'date_validate': fields.datetime.now(),
                'state_message': params.get('paytext', ''),
                'acquirer_reference': params.get('requestid'),
            })
        elif status == paysera.PAYSERA_STATUS_PAYMENT_ACCEPTED:
            tx.write({
                'state': 'pending',
                'state_message': params.get('paytext', ''),
                'acquirer_reference': params.get('requestid'),
            })
        elif status == paysera.PAYSERA_STATUS_ADDITIONAL_INFO:
            pass
        else:
            error = _(u'Paysera: unknown payment status: %s') % status
            _LOG.error(error)
            tx.write({
                'state': 'error',
                'state_message': error,
            })
            ret_val = False
        return ret_val
