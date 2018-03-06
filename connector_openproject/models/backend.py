# -*- coding: utf-8 -*-
# Copyright 2017 Naglis Jonaitis
# License AGPL-3 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models

from ..const import (
    DEFAULT_PAGE_SIZE,
    DEFAULT_TIMEOUT,
)
from ..utils import job_func, last_update, op_filter


def project_is_syncable(project):
    return project.op_sync and project.active


class OpenProjectBackend(models.Model):
    _name = 'openproject.backend'
    _description = 'OpenProject Backend'
    _inherit = 'connector.backend'

    @api.model
    def select_versions(self):
        return [
            ('7.3', '7.3+'),
        ]

    version = fields.Selection(
        selection='select_versions',
        required=True,
        default='7.3',
    )
    active = fields.Boolean(
        default=True,
    )
    debug = fields.Boolean(
        help='Output requests/responses to/from OpenProject API to the logs',
    )
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.user.company_id.id,
    )
    instance_url = fields.Char(
        string='OpenProject URL',
        help='URL to the OpenProject instance',
        required=True,
    )
    sync_project_status = fields.Boolean(
        string='Synchronize Project Status',
        help='If enabled, archived/unarchived projects on the OpenProject '
             'instance will be marked as inactive/active in Odoo.',
        default=True,
    )

    api_key = fields.Char(
        string='API Key',
        help='The API key of the OpenProject user used for synchronization',
        required=True,
    )
    timeout = fields.Integer(
        help='HTTP request timeout in seconds (0 - no timeout).',
        default=DEFAULT_TIMEOUT,
    )
    page_size = fields.Integer(
        string='Page Size',
        help='Number of elements to retrieve from OpenProject in one request',
        default=DEFAULT_PAGE_SIZE,
    )

    op_user_ids = fields.One2many(
        comodel_name='openproject.res.users',
        inverse_name='backend_id',
        string='OpenProject Users',
    )
    op_project_ids = fields.One2many(
        comodel_name='openproject.project.project',
        inverse_name='backend_id',
        string='OpenProject Projects',
    )
    op_task_ids = fields.One2many(
        comodel_name='openproject.project.task',
        inverse_name='backend_id',
        string='OpenProject Work Packages',
    )
    op_time_entry_ids = fields.One2many(
        comodel_name='openproject.account.analytic.line',
        inverse_name='backend_id',
        string='OpenProject Time Entries',
    )

    user_count = fields.Integer(
        string='Users',
        compute='_compute_record_count',
        store=True,
    )
    project_count = fields.Integer(
        string='Projects',
        compute='_compute_record_count',
        store=True,
    )
    task_count = fields.Integer(
        string='Work Packages',
        compute='_compute_record_count',
        store=True,
    )
    time_entry_count = fields.Integer(
        string='Time Entries',
        compute='_compute_record_count',
        store=True,
    )

    @api.depends('op_user_ids', 'op_project_ids', 'op_task_ids',
                 'op_time_entry_ids')
    def _compute_record_count(self):
        for rec in self:
            rec.user_count = len(rec.op_user_ids)
            rec.project_count = len(rec.op_project_ids)
            rec.task_count = len(rec.op_task_ids)
            rec.time_entry_count = len(rec.op_time_entry_ids)

    @api.multi
    def toggle_debug(self):
        '''
        Inverse the value of the field ``debug`` on the records in ``self``.
        '''
        for rec in self:
            rec.debug = not rec.debug

    @api.multi
    def import_projects(self, delay=True):
        for rec in self:
            model = rec.env['openproject.project.project']
            job_func(model, 'import_batch', delay=delay)(
                rec, delay=delay, chunked=not delay)
        return True

    @api.multi
    def import_project_work_packages(self, delay=True):
        for rec in self:
            for project in rec.op_project_ids.filtered(project_is_syncable):
                filters = [
                    op_filter('project', '=', project.openproject_id),
                ]
                with last_update(project, 'last_work_package_update') as last:
                    # TODO(naglis): Allow to override with `force=True` etc.
                    if last:
                        filters.append(
                            op_filter('updatedAt', '<>d', last.isoformat(),
                                      None))
                    job_func(
                        rec.env['openproject.project.task'],
                        'import_batch',
                        delay=delay)(
                            rec, filters=filters, delay=delay,
                            chunked=not delay)

    @api.multi
    def import_project_time_entries(self, delay=True):
        for rec in self:
            for project in rec.op_project_ids.filtered(project_is_syncable):
                filters = [
                    op_filter('project', '=', project.openproject_id),
                ]
                with last_update(project, 'last_time_entry_update'):
                    # XXX(naglis): Currently there is no updatedAt filter for
                    # time entries. See also: goo.gl/Kst39h
                    job_func(
                        rec.env['openproject.account.analytic.line'],
                        'import_batch',
                        delay=delay)(
                            rec, filters=filters, delay=delay, chunked=True)

    @api.model
    def _cron_sync(self, domain=None):
        backends = self.search(domain or [])
        # Work package and time entry import jobs are bootstraped by the
        # project import job.
        backends.import_projects()
