# -*- coding: utf-8 -*-
# Copyright 2017 Naglis Jonaitis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import base64
import contextlib
import io

from odoo import _, api, exceptions, fields, models

from .. import utils

ENCODINGS = [
    ('utf-8', 'UTF-8'),
    ('utf-16', 'UTF-16'),
    ('utf-32', 'UTF-32'),
]
DELIMITERS = [
    (',', 'Comma (,)'),
    (':', 'Colon (:)'),
    (';', 'Semicolon (;)'),
    ('|', 'Pipe (|)'),
    ('\t', 'Tab'),
]
DATE_FORMATS = [
    ('%Y-%m-%d', '2006-01-02'),
    ('%d/%m/%Y', '02/01/2006'),
    ('%d.%m.%Y', '02.01.2006'),
    ('%d-%m-%Y', '02-01-2006'),
    ('%m/%d/%Y', '01/02/2006'),
    ('%d %b %Y', '02 Jan 2006'),
    ('%d %B %Y', '02 January 2006'),
    ('%b %d, %Y', 'Jan 02, 2006'),
    ('%B %d, %Y', 'January 02, 2006'),
]

date_from_string = fields.Date.from_string


class OPImportRelated(models.AbstractModel):
    _name = 'op.import.related'

    import_id = fields.Many2one(
        comodel_name='op.import',
        ondelete='cascade',
        string='OpenProject CSV Import Wizard',
        required=True,
    )


class OPImport(models.TransientModel):
    _name = 'op.import'

    source = fields.Selection(
        selection=[
            ('from_file', 'From File'),
        ],
        default='from_file',
        required=True,
    )
    state = fields.Selection(
        selection=[
            ('new', 'New'),
            ('map_data', 'Map Data'),
        ],
        default='new',
        required=True,
        readonly=True,
    )
    csv_file = fields.Binary(
        string='CSV File',
        help='The CSV file which was exported from OpenProject',
    )
    encoding = fields.Selection(
        selection=ENCODINGS,
        required=True,
        default='utf-8',
    )
    delimiter = fields.Selection(
        selection=DELIMITERS,
        required=True,
        default=',',
        help='The delimiter which separates column data in the CSV file',
    )
    skip_first = fields.Boolean(
        string='Skip First Line',
        help='First line of the file is the header and should be ignored.',
        default=True,
    )
    date_format = fields.Selection(
        string='Date Format',
        required=True,
        selection=DATE_FORMATS,
        help='Date format used in the CSV file. '
             'This depends on your OpenProject settings.',
    )
    time_entry_ids = fields.One2many(
        comodel_name='op.time.entry',
        inverse_name='import_id',
    )
    op_employee_ids = fields.One2many(
        comodel_name='op.employee.map',
        inverse_name='import_id',
        string='OpenProject Employee Mapping',
    )
    op_project_ids = fields.One2many(
        comodel_name='op.project.map',
        inverse_name='import_id',
        string='OpenProject Project Mapping',
    )

    @api.multi
    def _parse_csv_file(self):
        self.ensure_one()
        csv_file = base64.b64decode(self.csv_file)
        with contextlib.closing(io.BytesIO(csv_file)) as fobj:
            return utils.parse_op_timesheet_csv(
                fobj,
                skip_first=self.skip_first,
                encoding=self.encoding,
                date_fmt=self.date_format,
                delimiter=self.delimiter.encode('utf-8'),
            )

    @api.multi
    def action_upload_file(self):
        self.ensure_one()
        project_map_obj = self.env['op.project.map']
        employee_map_obj = self.env['op.employee.map']
        time_entries = self._parse_csv_file()

        available_projects, available_users = {}, {}
        for p in self.env['project.project'].search([]):
            available_projects[p.name.lower()] = p.id
        for u in self.env['hr.employee'].search([]):
            available_users[u.name.lower()] = u.id

        time_entry_vals = []
        op_employee_map, op_project_map = {}, {}
        for entry in time_entries:
            employee_name = entry['user']
            project_name = entry['project']

            if employee_name not in op_employee_map:
                op_employee_map[employee_name] = employee_map_obj.create({
                    'import_id': self.id,
                    'op_employee_name': employee_name,
                    'employee_id': available_users.get(
                        employee_name.lower(), False),
                }).id

            if project_name not in op_project_map:
                op_project_map[project_name] = project_map_obj.create({
                    'import_id': self.id,
                    'op_project_name': project_name,
                    'project_id': available_projects.get(
                        project_name.lower(), False),
                }).id

            time_entry_vals.append((0, 0, {
                'date': entry['date'],
                'op_employee_map_id': op_employee_map[employee_name],
                'op_project_map_id': op_project_map[project_name],
                'work_package': entry['wp'],
                'hours': entry['hours'],
                'comment': entry['comment'] or u'/',
            }))

        if not time_entry_vals:
            raise exceptions.ValidationError(
                _('There are no time entries in the CSV file! '
                  'Or maybe incorrect delimiter was specified?'))

        self.write({
            'state': 'map_data',
            'time_entry_ids': time_entry_vals,
        })

        action = self.get_formview_action()
        action.update(
            name=_('Map Data'),
            target='new',
        )
        return action

    @api.multi
    def action_import_file(self):
        self.ensure_one()
        res_ids = []
        for employee_map in self.op_employee_ids.filtered('employee_id'):
            aal_obj = self.env['account.analytic.line']
            for time_entry in employee_map.time_entry_ids:
                res_ids.append(aal_obj.create(
                    time_entry._prepare_analytic_line_values(),
                ).id)
        return {
            'type': 'ir.actions.act_window',
            'name': _('Created time entries'),
            'res_model': aal_obj._name,
            'view_mode': 'tree,form',
            'domain': [('id', 'in', res_ids)],
            'context': self.env.context,
        }


class OPTimeEntry(models.TransientModel):
    _name = 'op.time.entry'
    _inherit = 'op.import.related'

    date = fields.Date(
        help='Date when the work took place.',
        required=True,
    )
    op_employee_map_id = fields.Many2one(
        comodel_name='op.employee.map',
        string='Employee',
        ondelete='cascade',
        required=True,
        readonly=True,
    )
    op_project_map_id = fields.Many2one(
        comodel_name='op.project.map',
        string='Project',
        ondelete='cascade',
        required=True,
        readonly=True,
    )
    work_package = fields.Integer(
        string='Work Package',
        default=0,
        help='Work package number',
    )
    hours = fields.Float(
        readonly=True,
        digits=(16, 2),
        help='Time spent.',
    )
    comment = fields.Char(
        default='/',
        required=True,
        help='A short description on where the time was spent on.',
    )
    project_id = fields.Many2one(
        related='op_project_map_id.project_id',
        string='Project',
        readonly=True,
    )

    @api.multi
    def _prepare_analytic_line_values(self):
        self.ensure_one()
        return {
            'date': self.date,
            'name': self.comment,
            'unit_amount': self.hours,
            'project_id': self.project_id.id,
            'user_id': self.op_employee_map_id.employee_id.user_id.id,
        }


class OPEmployeeMap(models.TransientModel):
    _name = 'op.employee.map'
    _inherit = 'op.import.related'
    _order = 'op_employee_name'

    op_employee_name = fields.Char(
        'OpenProject Employee Name',
        readonly=True,
        required=True,
    )
    employee_id = fields.Many2one(
        comodel_name='hr.employee',
        string='Employee',
    )
    time_entry_ids = fields.One2many(
        comodel_name='op.time.entry',
        inverse_name='op_employee_map_id',
        string='Time Entries',
    )


class OPProjectMap(models.TransientModel):
    _name = 'op.project.map'
    _inherit = 'op.import.related'
    _order = 'op_project_name'

    op_project_name = fields.Char(
        'OpenProject Project Name',
        readonly=True,
        required=True,
    )
    project_id = fields.Many2one(
        comodel_name='project.project',
        string='Project',
    )
