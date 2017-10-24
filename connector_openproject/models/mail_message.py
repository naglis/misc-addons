# -*- coding: utf-8 -*-
# Copyright 2017 Naglis Jonaitis
# License AGPL-3 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class OpenProjectMailMessage(models.Model):
    _name = 'openproject.mail.message'
    _inherit = [
        'openproject.binding',
        'openproject.age.mixin',
    ]
    _inherits = {
        'mail.message': 'odoo_id',
    }
    _description = 'OpenProject Activity'

    odoo_id = fields.Many2one(
        comodel_name='mail.message',
        string='Odoo Mail Message',
        ondelete='cascade',
        required=True,
    )
