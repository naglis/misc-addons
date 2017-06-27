# -*- coding: utf-8 -*-

from openerp import _, api, exceptions, fields, models


class PaymentAcquirer(models.Model):
    _inherit = 'payment.acquirer'

    paysera_show_quality_sign = fields.Boolean(
        string='Show Paysera Quality Sign',
        help='If checked, the Paysera Quality Sign will be displayed on your '
             'website',
    )

    @api.multi
    @api.constrains('provider', 'paysera_show_quality_sign',
                    'website_published', 'environment')
    def _check_paysera_show_quality_sign(self):
        count = self.search_count([
            ('environment', '=', 'prod'),
            ('paysera_show_quality_sign', '=', True),
            ('provider', '=', 'paysera'),
            ('website_published', '=', True),
        ])
        if count > 1:
            raise exceptions.ValidationError(
                _('The Paysera Quality Sign can be displayed only for a '
                  'single production acquirer, visible on the website!'))
