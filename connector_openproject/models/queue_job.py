# -*- coding: utf-8 -*-
# Copyright 2017-2018 Naglis Jonaitis
# License AGPL-3 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class QueueJob(models.Model):
    _inherit = 'queue.job'

    @api.multi
    def related_action_openproject_link(self):
        '''Open the record on the OpenProject instance.'''
        self.ensure_one()
        backend, external_id = self.args[:2]

        with backend.work_on(self.model_name) as work:
            url = work.component(usage='binder').get_external_url(external_id)
            if url:
                return {
                    'type': 'ir.actions.act_url',
                    'target': 'new',
                    'url': url,
                }
