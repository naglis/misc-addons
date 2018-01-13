# -*- coding: utf-8 -*-
# Copyright 2018 Naglis Jonaitis
# License AGPL-3 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class PaymentAcquirer(models.Model):
    _inherit = 'payment.acquirer'

    paysera_verification_code = fields.Char(
        string='Paysera Verification Code',
        help='Site verification code which can be found by logging into your '
             'Paysera account.',
    )
