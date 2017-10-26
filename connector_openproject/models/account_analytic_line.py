# -*- coding: utf-8 -*-
# Copyright 2017 Naglis Jonaitis
# License AGPL-3 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class OpenProjectAccountAnalyticLine(models.Model):
    _name = 'openproject.account.analytic.line'
    _inherit = [
        'openproject.binding',
        'openproject.age.mixin',
    ]
    _inherits = {
        'account.analytic.line': 'odoo_id',
    }
    _description = 'OpenProject Time Entry'

    odoo_id = fields.Many2one(
        comodel_name='account.analytic.line',
        string='Odoo Timesheet Line',
        ondelete='cascade',
        required=True,
    )
