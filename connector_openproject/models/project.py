# -*- coding: utf-8 -*-
# Copyright 2017 Naglis Jonaitis
# License AGPL-3 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class OpenProjectProjectProject(models.Model):
    _name = 'openproject.project.project'
    _inherit = [
        'openproject.binding',
        'openproject.age.mixin',
        'openproject.syncable.mixin',
    ]
    _inherits = {
        'project.project': 'odoo_id',
    }
    _description = 'OpenProject Project'

    odoo_id = fields.Many2one(
        comodel_name='project.project',
        string='Odoo Project',
        ondelete='cascade',
        required=True,
    )
    last_work_package_update = fields.Datetime(
        string='Work Packages Last Updated',
        help='Date and time of the last time project\'s work packages were '
             'synced with OpenProject',
    )
    last_time_entry_update = fields.Datetime(
        string='Time Entries Last Updated',
        help='Date and time of the last time project\'s time entries were '
             'synced with OpenProject',
    )
    # TODO(naglis): Allow to select to sync only comments or updates.
    sync_activities = fields.Selection(
        string='Sync Activities',
        selection=[
            ('all', 'Comments and Updates'),
            ('none', 'Nothing'),
        ],
        required=True,
        default='all',
    )
