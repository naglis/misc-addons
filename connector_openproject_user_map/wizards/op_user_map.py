# -*- coding: utf-8 -*-
# Copyright 2017 Naglis Jonaitis
# License AGPL-3 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, exceptions, fields, models
from odoo.addons.connector_openproject.exceptions import (
    OpenProjectAPIPermissionError,
)
from odoo.addons.connector_openproject.const import DEFAULT_PAGE_SIZE
from odoo.addons.connector_openproject.utils import paginate


class OpenProjectUserMap(models.TransientModel):
    _name = 'op.user.map'
    _description = 'OpenProject User Mapping'

    backend_id = fields.Many2one(
        comodel_name='openproject.backend',
        string='Backend',
        ondelete='cascade',
        readonly=True,
        required=True,
    )
    state = fields.Selection(
        selection=[
            ('new', 'New'),
            ('map', 'Map'),
        ],
        required=True,
        default='new',
    )
    map_line_ids = fields.One2many(
        comodel_name='op.user.map.line',
        inverse_name='map_id',
        string='Mapping Lines',
    )

    @api.model
    def default_get(self, fields):
        res = super(OpenProjectUserMap, self).default_get(fields)
        if self.env.context.get('active_id'):
            res['backend_id'] = self.env.context['active_id']
        return res

    @api.multi
    def _get_wizard_action(
            self, name, view_xml_id='connector_openproject.user_map_wizard'):
        self.ensure_one()
        view = self.env.ref(view_xml_id, raise_if_not_found=False)
        return {
            'name': name,
            'context': self.env.context,
            'views': [
                (view.id if view else False, 'form'),
            ],
            'res_model': 'op.user.map',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': self.id,
        }

    @api.multi
    def action_get_users(self):
        self.ensure_one()
        line_vals = []
        with self.backend_id.work_on('openproject.res.users') as work:
            adapter = work.component(usage='backend.adapter')
            try:
                total = adapter.get_total()
                for offset in paginate(DEFAULT_PAGE_SIZE, total):
                    for record in adapter.get_collection(
                            offset=offset, page_size=DEFAULT_PAGE_SIZE):
                        # FIXME(naglis):
                        # mapper.map_record(record).values(fields=[...]) does
                        # not work for some reason.
                        line_vals.append({
                            'openproject_id': record['id'],
                            'name': record['name'],
                        })
            except OpenProjectAPIPermissionError:
                raise exceptions.UserError(
                    _(u'The OpenProject synchronization user has insuffiecient'
                      u' permissions for this operation. Please use an '
                      u'administrator\'s API key for the initial user '
                      u' mapping.'))

            self.write({
                'map_line_ids': [(0, 0, v) for v in line_vals],
                'state': 'map',
            })

        return self._get_wizard_action(_('Map users'))

    @api.multi
    def action_create_bindings(self):
        self.ensure_one()
        with self.backend_id.work_on('openproject.res.users') as work:
            # FIXME(naglis): There must be a better way?
            adapter = work.component(usage='backend.adapter')
            mapper = work.component(usage='import.mapper')
            binder = work.component(usage='binder')
            for line in self.map_line_ids.filtered('user_id'):
                record = adapter.get_single(line.openproject_id)
                values = mapper.map_record(record).values(for_create=False)
                values.update(odoo_id=line.user_id.id)
                binding = work.model.create(values)
                binder.bind(line.openproject_id, binding)
        return {
            'type': 'ir.actions.act_window_close',
        }


class OpenProjectUserMapLine(models.TransientModel):
    _name = 'op.user.map.line'
    _description = 'OpenProject User Mapping Line'
    _order = 'name'

    map_id = fields.Many2one(
        comodel_name='op.user.map',
        string='Mapping',
        ondelete='cascade',
        required=True,
    )
    openproject_id = fields.Char(
        string='OpenProject ID',
        required=True,
        readonly=True,
    )
    name = fields.Char(readonly=True)
    user_id = fields.Many2one(
        comodel_name='res.users',
        string='Odoo User',
        ondelete='cascade',
    )
