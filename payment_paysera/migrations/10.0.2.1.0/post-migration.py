# -*- coding: utf-8 -*-
# Copyright 2019 Naglis Jonaitis
# License AGPL-3 or later (https://www.gnu.org/licenses/agpl).

from odoo import SUPERUSER_ID, api


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env['payment.acquirer'].search([
        ('provider', '=', 'paysera'),
    ]).write({
        'paysera_validate_paid_amount': False,
    })
