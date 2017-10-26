# -*- coding: utf-8 -*-
# Copyright 2017 Naglis Jonaitis
# License AGPL-3 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import AbstractComponent, Component


class OpenProjectBaseBinder(AbstractComponent):
    _name = 'base.openproject.binder'
    _inherit = [
        'base.binder',
        'base.openproject.connector',
    ]
    _external_field = 'openproject_id'
    _usage = 'binder'


class OpenProjectBinder(Component):
    _name = 'openproject.binder'
    _inherit = 'base.openproject.binder'
    _apply_on = [
        'openproject.account.analytic.line',
        'openproject.mail.message',
        'openproject.project.project',
        'openproject.project.task',
        'openproject.project.task.type',
        'openproject.res.users',
    ]
