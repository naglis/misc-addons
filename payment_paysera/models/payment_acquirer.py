# Copyright 2018-2019 Naglis Jonaitis
# License AGPL-3 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models

from .. import paysera, utils
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
        groups='base.group_system',
    )
    paysera_sign_password = fields.Char(
        string='Sign password',
        size=255,
        required_if_provider='paysera',
        help=u'Project password, which can be found by logging in to '
             u'Paysera.com system, selecting “Service management” and '
             u'choosing “General settings” on a specific project.',
        groups='base.group_system',
    )
    paysera_validate_paid_amount = fields.Boolean(
        string='Validate Paid Amount',
        default=True,
        help='If enabled, the actual paid amount and currency will be '
             'validated against values stored on the transaction.'
             'If at least one of them does not match, the transaction will '
             'be put in "error" state, to be reviewed by a manager. '
             'This can happen e.g., if the customer pays in another currency.',
    )

    @api.multi
    def ensure_paysera(self):
        if not set(self.mapped('provider')) == {'paysera'}:
            raise ValueError('Expected Paysera acquirer: %s' % self)
        return self

    @api.model
    def _get_paysera_urls(self):
        '''Returns Paysera API URLs.'''
        return {
            'paysera_standard_api_url': paysera.PAYSERA_API_URL,
        }

    @api.model
    def _get_paysera_redirect_urls(self):
        '''
        Returns a dictionary of Paysera redirect URLs.

        - `accepturl`: full address (URL), to which the client is directed
        after a successful payment;
        - `cancelurl': full address (URL), to which the client is directed
        after an unsuccessful payment or cancellation;
        - `callbackurl`: full address (URL), to which a seller will get
        information about performed payment.
        '''
        full_url = utils.make_full_url_getter(self.env)
        return {
            'accepturl': full_url(PayseraController._accept_url),
            'cancelurl': full_url(PayseraController._cancel_url),
            'callbackurl': full_url(PayseraController._callback_url),
        }

    @api.multi
    def paysera_form_generate_values(self, values):
        '''Generates the values used to render the form button template.'''
        self.ensure_one().ensure_paysera()

        lang = values['billing_partner_lang'] or ''
        if '_' in lang:
            lang = LANG_MAP.get(lang.split('_')[0], '')

        country_code = (
            values['billing_partner_country'].code
            if values.get('billing_partner_country') else ''
        )
        currency = values['currency']
        paysera_params = dict(
            projectid=self.paysera_project_id,
            orderid=values['reference'],
            lang=lang,
            amount=paysera.get_amount_string(currency, values['amount']),
            currency=currency.name,
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
        paysera_params.update({
            k: v for k, v in self._get_paysera_redirect_urls().items()
            if k in ('accepturl', 'cancelurl', 'callbackurl')
        })
        values.update(paysera.get_form_values(
            paysera_params,
            self.paysera_sign_password,
        ))
        return values

    @api.multi
    def paysera_get_form_action_url(self):
        '''Returns the form action URL.'''
        self.ensure_one().ensure_paysera()
        return self._get_paysera_urls()['paysera_standard_api_url']
