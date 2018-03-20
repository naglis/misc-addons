# -*- coding: utf-8 -*-
# Copyright 2018 Naglis Jonaitis
# License LGPL-3 or later (https://www.gnu.org/licenses/lgpl).

import jinja2

import odoo
from odoo.addons.web.controllers.main import env as jinja2_env

if not odoo.tools.config['list_db']:
    jinja2_env.loader = jinja2.PackageLoader(
        'odoo.addons.sec_disable_db_manager', 'views')
