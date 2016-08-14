# -*- coding: utf-8 -*-
# This file is part of OpenERP. The COPYRIGHT file at the top level of
# this module contains the full copyright notices and license terms.

import base64
import contextlib
import datetime
import io

from openerp import tools
from openerp.addons.hr_timesheet_openproject import utils
from openerp.osv import fields, osv
from openerp.tools.translate import _


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


def date_from_string(s):
    return datetime.datetime.strptime(
        s, tools.DEFAULT_SERVER_DATE_FORMAT).date()


class op_timesheet(osv.TransientModel):
    _name = 'op.timesheet'

    def _get_default_company(self, cr, uid, context=None):
        return self.pool.get('res.users').browse(
            cr, uid, uid, context).company_id.id

    def _check_period(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        wizard = self.browse(cr, uid, ids[0], context=context)
        if (all((wizard.date_from, wizard.date_to)) and
                wizard.date_to < wizard.date_from):
            return False
        return True

    _columns = {
        'state': fields.selection(
            selection=[('new', 'New'), ('draft', 'Draft'), ('done', 'Done')],
            string='State', readonly=True, required=True,
        ),
        'company_id': fields.many2one(
            'res.company', required=True, string='Company',
        ),
        'account_id': fields.many2one(
            'account.analytic.account', string='Account', required=True,
        ),
        'date_from': fields.date(
            string='Date From', help='Timesheet period beginning date',
        ),
        'date_to': fields.date(
            string='Date To', help='Timesheet period end date',
        ),
        'csv_file': fields.binary(
            string='CSV File', required=True,
            help='The CSV file which was exported from OpenProject',
        ),
        'encoding': fields.selection(
            selection=ENCODINGS, required=True,
        ),
        'delimiter': fields.selection(
            selection=DELIMITERS, required=True,
            help='The delimiter which separates column data in the CSV file',
        ),
        'ignore_totals': fields.boolean(
            string='Ignore Totals',
            help='Don\'t include the totals line from the CSV file',
        ),
        'employee_map_ids': fields.one2many(
            'op.timesheet.employee.map', 'import_id',
        ),
    }
    _defaults = {
        'company_id': _get_default_company,
        'delimiter': ',',
        'encoding': 'utf-8',
        'ignore_totals': True,
        'state': 'new',
    }
    _constraints = [
        (
            _check_period,
            'Error! Period end date can\'t be earlier than the start date!',
            ['date_from', 'date_to'],
        ),
    ]

    def _get_wizard_action(self, cr, uid, ids, name, context=None):
        if context is None:
            context = {}
        return {
            'name': name,
            'context': context,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'op.timesheet',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': ids[0],
        }

    def _parse_csv_file(self, cr, uid, id, context=None):
        if context is None:
            context = {}
        wizard = self.browse(cr, uid, id, context=context)[0]
        with contextlib.closing(
                io.BytesIO(base64.b64decode(wizard.csv_file))) as fobj:
            time_entries = utils.parse_op_timesheet_csv(
                fobj, encoding=wizard.encoding,
                delimiter=wizard.delimiter.encode('utf-8'),
            )

        if wizard.ignore_totals:
            time_entries.pop(time_entries.keys()[-1])

        empty_csv = (
            len(time_entries) == 0 or len(time_entries.values()[0]) == 0
        )
        if empty_csv:
            raise osv.except_osv(
                _('Error!'),
                _('There are no time entries in the CSV file!'
                  'Or maybe incorrect delimiter was specified?')
            )
        return time_entries

    def action_upload_file(self, cr, uid, id, context=None):
        if context is None:
            context = {}
        employee_obj = self.pool.get('hr.employee')
        time_entries = self._parse_csv_file(cr, uid, id, context=context)
        wizard = self.browse(cr, uid, id, context=context)[0]
        entries = time_entries.values()[0]
        min_date, max_date = min(entries), max(entries)
        line_vals = []
        for name, entries in time_entries.iteritems():
            employee_matches = employee_obj.search(cr, uid, [
                ('name', 'ilike', name),
                ('company_id', '=', wizard.company_id.id),
            ], limit=1, context=context)
            employee_id = employee_matches[0] if employee_matches else False
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
        if not wizard.date_from:
            values['date_from'] = min_date
        if not wizard.date_to:
            values['date_to'] = max_date

        wizard.write(values, context=context)
        return self._get_wizard_action(
            cr, uid, id, _('Map Employees'), context=context)

    def action_import_file(self, cr, uid, id, context=None):
        if context is None:
            context = {}
        wizard = self.browse(cr, uid, id, context=context)[0]
        min_date, max_date = map(
            date_from_string, (wizard.date_from, wizard.date_to))
        time_entries = self._parse_csv_file(cr, uid, id, context=None)
        sheet_obj = self.pool.get('hr_timesheet_sheet.sheet')
        for line in wizard.employee_map_ids:
            if not line.employee_id:
                continue
            line_vals = []
            for dt, hours in time_entries[line.name].iteritems():
                if not min_date <= dt <= max_date:
                    continue
                if tools.float_is_zero(hours, precision_digits=2):
                    continue
                line_vals.append((0, False, {
                    'account_id': wizard.account_id.id,
                    'date': dt,
                    'journal_id': line.employee_id.journal_id.id,
                    'name': '/',
                    'unit_amount': hours,
                }))

            # Create the timesheet only if there is at least one line.
            if line_vals:
                ctx = context.copy()
                ctx.update({'user_id': line.employee_id.user_id.id})
                timesheet_id = sheet_obj.create(cr, uid, {
                    'date_from': wizard.date_from,
                    'date_to': wizard.date_to,
                    'employee_id': line.employee_id.id,
                    'timesheet_ids': line_vals,
                }, context=ctx)
                line.write({'timesheet_id': timesheet_id}, context=context)

        wizard.state = 'done'
        return self._get_wizard_action(
            cr, uid, id, _('Import Finished'), context=context)


class op_timesheet_employee_map(osv.TransientModel):
    _name = 'op.timesheet.employee.map'

    _columns = {
        'name': fields.char(
            string='Employee Name', readonly=True,
        ),
        'import_id': fields.many2one(
            'op.timesheet', ondelete='cascade', required=True,
        ),
        'employee_id': fields.many2one(
            'hr.employee', string='Employee',
        ),
        'total_hours': fields.float(
            string='Hours', readonly=True, digits=(16, 2),
            help='Hours worked in the period of the timesheet',
        ),
        'timesheet_id': fields.many2one(
            'hr_timesheet_sheet.sheet', string='Timesheet', readonly=True,
        ),
    }
