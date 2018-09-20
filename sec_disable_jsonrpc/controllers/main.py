# -*- coding: utf-8 -*-
# Copyright 2018 Naglis Jonaitis
# License AGPL-3 or later (https://www.gnu.org/licenses/agpl).

from odoo import http
import werkzeug.exceptions


class CommonController(http.CommonController):

    @http.route()
    def jsonrpc(self, *args, **kwargs):
        raise werkzeug.exceptions.NotFound()
