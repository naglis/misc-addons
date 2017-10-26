# -*- coding: utf-8 -*-
# Copyright 2017 Naglis Jonaitis
# License AGPL-3 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.addons.queue_job.job import job


class OpenProjectUser(models.Model):
    _name = 'openproject.res.users'
    _inherit = [
        'openproject.binding',
        'openproject.age.mixin',
    ]
    _inherits = {
        'res.users': 'odoo_id',
    }
    _description = 'OpenProject User'

    odoo_id = fields.Many2one(
        comodel_name='res.users',
        string='Odoo User',
        ondelete='cascade',
        required=True,
    )

    @api.model
    @job(default_channel='root.openproject')
    def import_avatar(self, backend, url, record_id):
        '''Import user's avatar image.'''
        with backend.work_on(self._name) as work:
            importer = work.component(usage='image.importer')
            return importer.run(
                url, self._name, record_id, 'image',
                timeout=backend.timeout or None)
