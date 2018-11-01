# Copyright 2018 Naglis Jonaitis
# License AGPL-3 or later (https://www.gnu.org/licenses/agpl).

from odoo import http
from odoo.addons.base.controllers import rpc
import werkzeug.exceptions


class RPC(rpc.RPC):

    @http.route()
    def jsonrpc(self, *args, **kwargs):
        raise werkzeug.exceptions.NotFound()
