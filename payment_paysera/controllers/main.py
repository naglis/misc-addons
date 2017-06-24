# -*- coding: utf-8 -*-

from odoo import http
from odoo.http import request

import werkzeug


class PayseraController(http.Controller):
    _accept_url = '/payment/paysera/accept'
    _cancel_url = '/payment/paysera/cancel'
    _callback_url = '/payment/paysera/callback'

    @http.route([
        '/payment/paysera/accept',
    ], type='http', auth='none', methods=['GET'])
    def paysera_payment_accept(self, **params):
        # We receive payment info when the user is redirected after a
        # successfull payment, too, although the status will most likely be `2`
        # (pending) at this point.
        request.env['payment.transaction'].sudo().form_feedback(
            params, 'paysera')

        return werkzeug.utils.redirect('/shop/payment/validate')

    @http.route([
        '/payment/paysera/cancel',
    ], type='http', auth='none', methods=['GET'])
    def paysera_payment_cancel(self, **params):
        return werkzeug.utils.redirect('/shop/payment')

    @http.route([
        '/payment/paysera/callback',
    ], type='http', auth='none', methods=['GET', 'POST'], csrf=False)
    def paysera_payment_callback(self, **post_data):
        request.env['payment.transaction'].sudo().form_feedback(
            post_data, 'paysera')
        return 'OK'
