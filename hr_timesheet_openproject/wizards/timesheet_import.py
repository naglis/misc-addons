# -*- coding: utf-8 -*-
# This file is part of Odoo. The COPYRIGHT file at the top level of
# this module contains the full copyright notices and license terms.

import base64
import contextlib
import io

from openerp import _, api, exceptions, fields, models, tools
from openerp.addons.hr_timesheet_openproject import utils

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


class OPTimesheet(models.TransientModel):
    _name = 'op.timesheet'

    state = fields.Selection(
        selection=[('new', 'New'), ('draft', 'Draft'), ('done', 'Done')],
        string='State', readonly=True, default='new', required=True,
    )
    company_id = fields.Many2one(
        comodel_name='res.company', required=True, string='Company',
        default=lambda self: self.env.user.company_id,
    )
    account_id = fields.Many2one(
        comodel_name='account.analytic.account', string='Account',
        required=True,
    )
    date_from = fields.Date(
        string='Date From', help='Timesheet period beginning date')
    date_to = fields.Date(
        string='Date To', help='Timesheet period end date')
    csv_file = fields.Binary(
        string='CSV File', required=True,
        help='The CSV file which was exported from OpenProject',
    )
    encoding = fields.Selection(
        selection=ENCODINGS, required=True, default='utf-8')
    delimiter = fields.Selection(
        selection=DELIMITERS, required=True, default=',',
        help='The delimiter which separates column data in the CSV file',
    )
    ignore_totals = fields.Boolean(
        string='Ignore Totals', default=True,
        help='Don\'t include the totals line from the CSV file',
    )
    employee_map_ids = fields.One2many(
        comodel_name='op.timesheet.employee.map', inverse_name='import_id')

    @api.one
    @api.constrains('date_from', 'date_to')
    def _check_period(self):
        if (all((self.date_from, self.date_to)) and
                self.date_to < self.date_from):
            raise exceptions.ValidationError(
                _('Period end date can\'t be earlier than the start date!')
            )

    @api.multi
    def _get_wizard_action(
            self, name, view_xml_id='hr_timesheet_openproject.import_wizard'):
        self.ensure_one()

        view = self.env.ref(view_xml_id, raise_if_not_found=False)
        return {
            'name': name,
            'context': self.env.context,
            'views': [(view.id if view else False, 'form')],
            'res_model': 'op.timesheet',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': self.id,
        }

    @api.multi
    def _parse_csv_file(self):
        self.ensure_one()
        with contextlib.closing(
                io.BytesIO(base64.b64decode(self.csv_file))) as fobj:
            time_entries = utils.parse_op_timesheet_csv(
                fobj, encoding=self.encoding,
                delimiter=self.delimiter.encode('utf-8'),
            )

        if self.ignore_totals:
            time_entries.pop(time_entries.keys()[-1])

        empty_csv = (
            len(time_entries) == 0 or len(time_entries.values()[0]) == 0
        )
        if empty_csv:
            raise exceptions.ValidationError(
                _('There are no time entries in the CSV file!'
                  'Or maybe incorrect delimiter was specified?')
            )
        return time_entries

    @api.multi
    def action_upload_file(self):
        self.ensure_one()
        time_entries = self._parse_csv_file()
        entries = time_entries.values()[0]
        min_date, max_date = min(entries), max(entries)
        line_vals = []
        for name, entries in time_entries.iteritems():
            employee_matches = self.env['hr.employee'].search([
                ('name', 'ilike', name),
                ('company_id', '=', self.company_id.id),
            ], limit=1)
            employee_id = employee_matches[0].id if employee_matches else False

            line_vals.append((0, False, {
                'name': name,
                'employee_id': employee_id,
                'total_hours': sum(entries.itervalues())
            }))

        values = {
            'state': 'draft',
            'employee_map_ids': line_vals,
        }

        # If date_from/date_to are not set, set them from min/max dates in the
        # CSV files.
        if not self.date_from:
            values['date_from'] = min_date
        if not self.date_to:
            values['date_to'] = max_date

        self.write(values)
        return self._get_wizard_action(_('Map Employees'))

    @api.multi
    def action_import_file(self):
        self.ensure_one()

        min_date, max_date = map(
            fields.Date.from_string, (self.date_from, self.date_to))
        time_entries = self._parse_csv_file()
        for line in self.employee_map_ids:
            if not line.employee_id:
                continue
            line_vals = []
            sheet_obj = self.env['hr_timesheet_sheet.sheet'].with_context(
                user_id=line.employee_id.user_id.id)
            for dt, hours in time_entries[line.name].iteritems():
                if not min_date <= dt <= max_date:
                    continue
                if tools.float_is_zero(hours, precision_digits=2):
                    continue
                line_vals.append((0, False, {
                    'account_id': self.account_id.id,
                    'date': dt,
                    'journal_id': line.employee_id.journal_id.id,
                    'name': '/',
                    'unit_amount': hours,
                }))

            # Create the timesheet only if there is at least one line.
            if line_vals:
                line.timesheet_id = sheet_obj.create({
                    'date_from': self.date_from,
                    'date_to': self.date_to,
                    'employee_id': line.employee_id.id,
                    'timesheet_ids': line_vals,
                })
        self.state = 'done'

        # Delete lines without timesheet.
        self.employee_map_ids.filtered(lambda ln: not ln.timesheet_id).unlink()

        return self._get_wizard_action(
            _('Import Finished'),
            view_xml_id='hr_timesheet_openproject.import_wizard_finished')


class OPTimesheetEmployeeMap(models.TransientModel):
    _name = 'op.timesheet.employee.map'

    name = fields.Char(string='Employee Name', readonly=True)
    import_id = fields.Many2one(
        comodel_name='op.timesheet', ondelete='cascade')
    employee_id = fields.Many2one(
        comodel_name='hr.employee', string='Employee')
    total_hours = fields.Float(
        string='Hours', readonly=True, digits=(16, 2),
        help='Hours worked in the period of the timesheet')
    timesheet_id = fields.Many2one(
        comodel_name='hr_timesheet_sheet.sheet', string='Timesheet',
        readonly=True,
    )
