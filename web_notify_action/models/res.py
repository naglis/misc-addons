# Copyright 2018-2019 Naglis Jonaitis
# License LGPL-3 or later (https://www.gnu.org/licenses/lgpl).

from odoo import api, models, tools


class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.multi
    def _notify_action(self, params):
        return self.env['notify.action']._notify_users(
            tools.OrderedSet(self.ids), params)
