# -*- coding: utf-8 -*-
# Copyright 2017-2018 Naglis Jonaitis
# License AGPL-3 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.addons.queue_job.job import job, related_action

from ..utils import job_func, paginate


class OpenProjectSyncableMixin(models.AbstractModel):
    _name = 'openproject.syncable.mixin'

    op_sync = fields.Boolean(
        string='Sync with OpenProject',
        default=True,
    )


class OpenProjectAgeMixin(models.AbstractModel):
    _name = 'openproject.age.mixin'

    op_create_date = fields.Datetime(
        string='OpenProject Create Date',
        readonly=True,
    )
    op_write_date = fields.Datetime(
        string='OpenProject Last Update Date',
        readonly=True,
    )


class OpenProjectExternalURLMixin(models.AbstractModel):
    _name = 'openproject.external.url.mixin'

    @api.multi
    def action_open_external_url(self):
        '''
        Returns an `ir.actions.act_url` action to open the resource's URL on
        the OpenProject instance.
        '''
        self.ensure_one()
        with self.backend_id.work_on(self._name) as work:
            external_url = work.component(
                usage='binder').get_external_url(self.openproject_id)
            return {
                'type': 'ir.actions.act_url',
                'url': external_url,
                'target': 'new',
            } if external_url else {}


class OpenProjectBinding(models.AbstractModel):
    _name = 'openproject.binding'
    _inherit = 'external.binding'
    _description = 'OpenProject Binding (abstract)'

    _sql_constraints = [
        (
            'code_uniq',
            'UNIQUE(backend_id, openproject_id)',
            'OpenProject ID must be unique!',
        ),
    ]

    backend_id = fields.Many2one(
        comodel_name='openproject.backend',
        string='Backend',
        required=True,
        readonly=True,
        ondelete='cascade',
    )
    openproject_id = fields.Char(
        'OpenProject ID',
        index=True,
        readonly=True,
        help='Record\'s identifier on the OpenProject instance',
    )

    @api.model
    @job(default_channel='root.openproject')
    @related_action(action='related_action_openproject_link')
    def import_record(self, backend, external_id, force=False):
        '''Import a single record from OpenProject.'''
        with backend.work_on(self._name) as work:
            importer = work.component(usage='record.importer')
            return importer.run(external_id, force=force)

    @api.model
    @job(default_channel='root.openproject')
    def import_batch(self, backend, filters=None, delay=True, chunked=False):
        '''Import records from OpenProject.'''
        with backend.work_on(self._name) as work:
            adapter = work.component(usage='backend.adapter')
            if adapter.paginated:
                total = adapter.get_total(filters=filters)
                for offset in paginate(backend.page_size, total):
                    job_func(
                        self,
                        'import_batch_chunk',
                        delay=delay)(
                            backend, offset, filters=filters,
                            chunked=chunked)
            else:
                importer = work.component(usage='batch.importer')
                return importer.run(
                    job_options={'delay': delay},
                    filters=filters)

    @api.model
    @job(default_channel='root.openproject')
    def import_batch_chunk(self, backend, offset, filters=None, chunked=False):
        '''Import a chunk of OpenProject records at once.'''
        with backend.work_on(self._name) as work:
            importer = work.component(usage='batch.importer')
            return importer.run(
                job_options={'delay': not chunked}, filters=filters,
                offset=offset)
