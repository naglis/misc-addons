# -*- coding: utf-8 -*-
# Copyright 2018 Naglis Jonaitis
# License AGPL-3 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models

from ..mistertango import (
    MISTERTANGO_LANGUAGES,
    MISTERTANGO_MARKETS,
    MISTERTANGO_SUPPORTED_CURRENCIES,
)


class PaymentAcquirer(models.Model):
    _inherit = 'payment.acquirer'

    provider = fields.Selection(
        selection_add=[
            ('mistertango', 'Mistertango'),
        ],
    )
    mistertango_username = fields.Char(
        string='Username',
        required_if_provider='mistertango',
        groups='base.group_user',
    )
    mistertango_secret_key = fields.Char(
        string='Secret Key',
        required_if_provider='mistertango',
        groups='base.group_user',
    )
    mistertango_payment_type = fields.Selection(
        string='Payment Type',
        selection=[
            ('bank_link', 'Bank Link'),
            ('bank_transfer', 'Bank Transfer'),
            ('bitcoin', 'Bitcoin'),
            ('credit_card', 'Credit Card'),
        ],
        help=(
            'If set, only this payment type will be available during payment. '
            'If not set, the user will be able to choose the payment type.'
        ),
    )
    mistertango_market = fields.Selection(
        string='Market',
        selection=MISTERTANGO_MARKETS,
    )
    mistertango_default_lang = fields.Selection(
        string='Default Language',
        selection=MISTERTANGO_LANGUAGES,
        help=(
            'If set, this language will be used by Mistertango by default. '
            'Otherwise the language will be decided based on customer data.'
        ),
    )

    @api.multi
    def mistertango_form_generate_values(self, values):
        '''Generates the values used to render the form button template.'''
        values = values.copy()
        lang = (self.mistertango_default_lang or
                values['billing_partner_lang'] or '')
        if '_' in lang:
            lang = lang.lower().split('_')[0]
        currency = values.get('currency', self.env['res.currency'])
        enabled = currency.name in MISTERTANGO_SUPPORTED_CURRENCIES
        values.update(
            button_attributes={
                'data-amount': values['amount'],
                'data-lang': lang,
                'data-currency': currency.name,
                'data-payer': values['billing_partner_email'],
                'data-payment-type': self.mistertango_payment_type,
                'data-recipient': self.mistertango_username,
                'data-reference': values['reference'],
                'data-market': self.mistertango_market or u'',
                'data-error-msg': u'' if enabled else _(
                    u'Mistertango supports only these currencies: %s.') % (
                        u', '.join(MISTERTANGO_SUPPORTED_CURRENCIES)),
            },
        )
        return values
