# Copyright 2018-2019 Naglis Jonaitis
# License LGPL-3 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class NotifyAction(models.AbstractModel):
    _name = 'notify.action'

    @api.model
    def _notify_users(self, user_ids, params):
        # Refer to the notification handling code client-side for a reference
        # on possible options in `params`.
        self.env['bus.bus'].sendmany([(
            (self.env.cr.dbname, 'web_notify_action.notify_action', uid),
            params,
        ) for uid in user_ids])
        return True
