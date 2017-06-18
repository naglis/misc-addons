# -*- coding: utf-8 -*-

import urlparse

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
             'Paysera.com system, selecting “Service management” and choosing '
             '“General settings” on a specific project.',
        groups='base.group_user',
    )

    @api.model
    def _get_providers(self):
        providers = super(PaymentAcquirer, self)._get_providers()
        providers.append(['paysera', 'Paysera'])
        return providers

    @api.model
    def _get_paysera_urls(self):
        '''Returns Paysera API URLs.'''
        return {
            'paysera_standard_api_url': paysera.PAYSERA_API_URL,
        }

    @api.multi
    def paysera_form_generate_values(self, partner, tx):
        '''Generates the values used to render the form button template.'''
        self.ensure_one()
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')

        def full_url(path):
            return urlparse.urljoin(base_url, path)

        lang = partner['lang'] or ''
        if '_' in lang:
            lang = LANG_MAP.get(lang.split('_')[0], '')

        paysera_params = dict(
            projectid=self.paysera_project_id,
            orderid=tx['reference'],
            lang=lang,
            amount='%d' % int(tools.float_round(tx['amount'], 2) * 100),
            currency=tx['currency'] and tx['currency'].name or '',
            accepturl=full_url(PayseraController._accept_url),
            cancelurl=full_url(PayseraController._cancel_url),
            callbackurl=full_url(PayseraController._callback_url),
            country=partner['country'] and partner['country'].code or '',
            p_firstname=partner['first_name'],
            p_lastname=partner['last_name'],
            p_email=partner['email'],
            p_street=partner['address'],
            p_city=partner['city'],
            p_zip=partner['zip'],
            p_countrycode=partner['country'] and partner['country'].code or '',
            test='1' if self.environment == 'test' else '0',
            version=paysera.PAYSERA_API_VERSION,
        )
        paysera_tx = dict(tx)
        paysera_tx.update(paysera.get_form_values(
            paysera_params,
            self.paysera_sign_password,
        ))
        return partner, paysera_tx

    @api.multi
    def paysera_get_form_action_url(self):
        '''Returns the form action URL.'''
        self.ensure_one()
        return self._get_paysera_urls()['paysera_standard_api_url']
