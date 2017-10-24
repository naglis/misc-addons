# -*- coding: utf-8 -*-
# Copyright 2017 Naglis Jonaitis
# License AGPL-3 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import AbstractComponent


class BaseOpenProjectConnectorComponent(AbstractComponent):
    _name = 'base.openproject.connector'
    _inherit = 'base.connector'
    _collection = 'openproject.backend'
