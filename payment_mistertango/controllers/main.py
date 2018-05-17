# Copyright 2018 Naglis Jonaitis
# License AGPL-3 or later (https://www.gnu.org/licenses/agpl).

import logging

from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)


class MistertangoController(http.Controller):

    @http.route([
        '/payment/mistertango/callback',
    ], type='http', methods=['POST'], auth='none', csrf=False)
    def mistertango_payment_callback(self, **data):
        sudo_tx_obj = request.env['payment.transaction'].sudo()

        # Check if such callback UUID was already handled and if so, return
        # immediately.
        callback_uuid = data.get('callback_uuid')
        if callback_uuid and sudo_tx_obj.search_count([
            ('acquirer_id.provider', '=', 'mistertango'),
            ('mistertango_callback_uuid', '=', callback_uuid),
        ]):
            return b'OK'

        try:
            ok = sudo_tx_obj.form_feedback(data, 'mistertango')
        except Exception:
            _logger.exception(
                'An error occurred while handling Mistertango callback')
            ok = False
        return b'OK' if ok else b'NOT OK'
