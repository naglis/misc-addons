# -*- coding: utf-8 -*-
# Copyright 2017 Naglis Jonaitis
# License AGPL-3 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models

from ..const import (
    ACTIVITY_SYNC_NONE,
    ACTIVITY_SYNC_COMMENTS,
    ACTIVITY_SYNC_UPDATES,
    ACTIVITY_SYNC_ALL,
)


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
    sync_activities = fields.Selection(
        string='Sync Activities',
        selection=[
            (ACTIVITY_SYNC_NONE, 'Nothing'),
            (ACTIVITY_SYNC_COMMENTS, 'Only Comments'),
            (ACTIVITY_SYNC_UPDATES, 'Only Status Updates'),
            (ACTIVITY_SYNC_ALL, 'Comments and Status Updates'),
        ],
        required=True,
        default='none',
    )
    sync_wp_description = fields.Boolean(
        string='Sync Work Package Description',
        help='In unchecked, work package description will not be stored.',
        default=False,
    )
