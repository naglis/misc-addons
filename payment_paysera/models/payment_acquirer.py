# -*- coding: utf-8 -*-
# Copyright 2018 Naglis Jonaitis
# License AGPL-3 or later (https://www.gnu.org/licenses/agpl).

import urllib.parse

from odoo import api, fields, models, tools

from .. import paysera
from ..controllers.main import PayseraController

# ISO-639-1 -> ISO-639-2/B
LANG_MAP = {
    'lt': 'LIT',
    'lv': 'LAV',
    'et': 'EST',
    'ru': 'RUS',
    'en': 'ENG',
    'de': 'GER',
    'pl': 'POL',
}


class PaymentAcquirer(models.Model):
    _inherit = 'payment.acquirer'

    provider = fields.Selection(
        selection_add=[
            ('paysera', 'Paysera'),
        ],
    )
    paysera_project_id = fields.Char(
        string='Project ID',
        size=11,
        required_if_provider='paysera',
        help='Unique Paysera project number',
        groups='base.group_user',
    )
    paysera_sign_password = fields.Char(
        string='Sign password',
        size=255,
        required_if_provider='paysera',
        help='Project password, which can be found by logging in to '
             'Paysera.com system, selecting “Service management” and '
             'choosing “General settings” on a specific project.',
        groups='base.group_user',
    )

    @api.model
    def _get_paysera_urls(self):
        '''Returns Paysera API URLs.'''
        return {
            'paysera_standard_api_url': paysera.PAYSERA_API_URL,
        }

    @api.multi
    def paysera_form_generate_values(self, values):
        '''Generates the values used to render the form button template.'''
        self.ensure_one()
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')

        def full_url(path):
            return urllib.parse.urljoin(base_url, path)

        lang = values['billing_partner_lang'] or ''
        if '_' in lang:
            lang = LANG_MAP.get(lang.split('_')[0], '')

        country_code = (
            values['billing_partner_country'].code
            if values['billing_partner_country'] else ''
        )
        paysera_params = dict(
            projectid=self.paysera_project_id,
            orderid=values['reference'],
            lang=lang,
            amount='%d' % int(tools.float_round(values['amount'], 2) * 100),
            currency=values['currency'] and values['currency'].name or '',
            accepturl=full_url(PayseraController._accept_url),
            cancelurl=full_url(PayseraController._cancel_url),
            callbackurl=full_url(PayseraController._callback_url),
            country=country_code,
            p_firstname=values['billing_partner_first_name'],
            p_lastname=values['billing_partner_last_name'],
            p_email=values['billing_partner_email'],
            p_street=values['billing_partner_address'],
            p_city=values['billing_partner_city'],
            p_zip=values['billing_partner_zip'],
            p_countrycode=country_code,
            test='1' if self.environment == 'test' else '0',
            version=paysera.PAYSERA_API_VERSION,
        )
        values.update(paysera.get_form_values(
            paysera_params,
            bytes(self.paysera_sign_password, 'ascii'),
        ))
        return values

    @api.multi
    def paysera_get_form_action_url(self):
        '''Returns the form action URL.'''
        self.ensure_one()
        return self._get_paysera_urls()['paysera_standard_api_url']
