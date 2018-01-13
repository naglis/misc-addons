# -*- coding: utf-8 -*-
# Copyright 2018 Naglis Jonaitis
# License AGPL-3 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class Website(models.Model):
    _inherit = 'website'

    @api.model
    def _get_paysera_project_ids(self):
        return self.env['payment.acquirer'].search([
            ('provider', '=', 'paysera'),
            ('environment', '=', 'prod'),
            ('website_published', '=', True),
            ('paysera_show_quality_sign', '=', True),
        ], limit=1).sudo().mapped('paysera_project_id')
