# Copyright 2018 Naglis Jonaitis
# License LGPL-3 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.bus.controllers.main import BusController
from odoo.http import request


class NotifyActionBusController(BusController):

    def _poll(self, dbname, channels, last, options):
        if request.session.uid:
            channels.append((
                request.db,
                'web_notify_action.notify_action',
                request.env.user.id,
            ))
        return super(NotifyActionBusController, self)._poll(
            dbname, channels, last, options)
