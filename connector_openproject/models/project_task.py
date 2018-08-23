# -*- coding: utf-8 -*-
# Copyright 2017-2018 Naglis Jonaitis
# License AGPL-3 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class OpenProjectProjectTask(models.Model):
    _name = 'openproject.project.task'
    _inherit = [
        'openproject.binding',
        'openproject.age.mixin',
        'openproject.syncable.mixin',
        'openproject.external.url.mixin',
    ]
    _inherits = {
        'project.task': 'odoo_id',
    }
    _description = 'OpenProject Work Package'

    odoo_id = fields.Many2one(
        comodel_name='project.task',
        string='Odoo Work Package',
        ondelete='cascade',
        required=True,
    )


class OpenProjectProjectTaskType(models.Model):
    _name = 'openproject.project.task.type'
    _inherit = [
        'openproject.binding',
    ]
    _inherits = {
        'project.task.type': 'odoo_id',
    }
    _description = 'OpenProject Status'

    odoo_id = fields.Many2one(
        comodel_name='project.task.type',
        string='Odoo Task Stage',
        ondelete='cascade',
        required=True,
    )
