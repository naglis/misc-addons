# -*- coding: utf-8 -*-

from odoo import api, models


class Website(models.Model):
    _inherit = 'website'

    @api.model
    def _get_paysera_verification_codes(self):
        return self.env['payment.acquirer'].search([
            ('provider', '=', 'paysera'),
            ('website_published', '=', True),
            '!',
            ('paysera_verification_code', '=?', ''),
        ]).mapped('paysera_verification_code')
