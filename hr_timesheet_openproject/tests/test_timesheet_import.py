# -*- coding: utf-8 -*-
# This file is part of OpenERP. The COPYRIGHT file at the top level of
# this module contains the full copyright notices and license terms.

import base64

from openerp import tests
from openerp.osv import osv

EMPLOYEE1_NAME = 'Nancy Wheeler'
EMPLOYEE2_NAME = 'Will Byers'
CSV1 = '''Member,2000-01-01,2000-01-02
%s,1.2,1.3
''' % EMPLOYEE1_NAME
CSV2 = '''Member,2000-01-01
%s,1.2
Total,1.2
''' % EMPLOYEE1_NAME
CSV3 = '''Member,2000-01-01
'''
CSV4 = '''Member,2000-01-01,2000-01-02,2000-01-03
%s,1.2,"",1.3
%s,"",0.2,0.1
''' % (EMPLOYEE1_NAME, EMPLOYEE2_NAME)


class TestTimesheetImport(tests.common.TransactionCase):

    def setUp(self):
        super(TestTimesheetImport, self).setUp()
        cr, uid = self.cr, self.uid
        partner_obj, users_obj, employee_obj, account_obj, wizard_obj = map(
            self.registry, [
                'res.partner',
                'res.users',
                'hr.employee',
                'account.analytic.account',
                'op.timesheet',
            ]
        )
        self.partner1_id = partner_obj.create(cr, uid, {
            'name': EMPLOYEE1_NAME,
        })
        self.user1_id = users_obj.create(cr, uid, {
            'name': EMPLOYEE1_NAME,
            'login': 'nancy',
            'partner_id': self.partner1_id,
        })
        self.employee1_id = employee_obj.create(cr, uid, {
            'name': EMPLOYEE1_NAME,
            'user_id': self.user1_id,
        })
        self.account1_id = account_obj.create(cr, uid, {
            'name': 'Test Account',
            'type': 'normal',
        })
        self.model = wizard_obj

    def create_wizard(self, csv_file, **overrides):
        values = {
            'account_id': self.account1_id,
            'csv_file': base64.b64encode(csv_file),
            'ignore_totals': False,
        }
        if overrides:
            values.update(overrides)
        return self.model.browse(
            self.cr, self.uid, self.model.create(self.cr, self.uid, values),
        )

    def test_parse_csv_file_empty_CSV3_raises_ValidationError(self):
        wizard = self.create_wizard(CSV3)
        with self.assertRaises(osv.except_osv):
            wizard._parse_csv_file()

    def test_parse_csv_file_CSV2_ignore_totals_removes_last_line(self):
        wizard = self.create_wizard(CSV2, ignore_totals=True)
        entries = wizard._parse_csv_file()
        self.assertEqual(len(entries), 1, 'Incorrect number of lines returned')
        self.assertNotEqual(entries.keys()[0], 'Total')

    def test_date_to_earlier_than_date_from_raises_ValidationError(self):
        wizard = self.create_wizard(CSV1, date_from='2000-01-02')
        with self.assertRaises(osv.orm.except_orm):
            wizard.write({'date_to': '2000-01-01'})

    def test_upload_file_CSV1_correct_date_from_date_to_values_are_set(self):
        wizard = self.create_wizard(CSV1)
        wizard.action_upload_file()
        self.assertEqual(wizard.date_from, '2000-01-01')
        self.assertEqual(wizard.date_to, '2000-01-02')

    def test_upload_file_CSV1_creates_one_line_with_correct_data(self):
        wizard = self.create_wizard(CSV1)
        wizard.action_upload_file()
        lines = wizard.line_ids
        self.assertEqual(len(lines), 1, 'Incorrect number of lines created')
        line = lines[0]
        self.assertEqual(line.name, EMPLOYEE1_NAME)
        self.assertAlmostEqual(
            line.total_hours, 2.5, places=2,
            msg='Incorrect worked hours value loaded',
        )

    def test_upload_file_CSV1_employee_with_exact_name_is_found(self):
        wizard = self.create_wizard(CSV1)
        wizard.action_upload_file()
        lines = [
            ln for ln in wizard.line_ids
            if ln.employee_id.id == self.employee1_id
        ]
        self.assertEqual(len(lines), 1)

    def test_import_file_CSV4_timesheet_with_correct_data_is_created(self):
        wizard = self.create_wizard(CSV4)
        wizard.action_upload_file()
        wizard.action_import_file()
        lines = [ln for ln in wizard.line_ids if ln.timesheet_id]
        self.assertEqual(len(lines), 1, 'Incorrect number of lines created')
        line = lines[0]
        self.assertEqual(line.timesheet_id.employee_id.id, self.employee1_id)
        time_entries = sorted(
            line.timesheet_id.timesheet_ids, key=lambda e: e.date)
        self.assertEqual(
            len(time_entries), 2, 'Incorrect number of time entries created')
        self.assertEqual(time_entries[0].date, '2000-01-01')
        self.assertEqual(time_entries[0].unit_amount, 1.2)
        self.assertEqual(time_entries[1].date, '2000-01-03')
        self.assertEqual(time_entries[1].unit_amount, 1.3)

    def test_import_file_CSV4_date_from_01_01_to_01_02_creates_one_entry(self):
        wizard = self.create_wizard(
            CSV4, date_from='2000-01-01', date_to='2000-01-02')
        wizard.action_upload_file()
        wizard.action_import_file()
        lines = [ln for ln in wizard.line_ids if ln.timesheet_id]
        self.assertEqual(len(lines), 1, 'Incorrect number of lines created')
        line = lines[0]
        time_entries = sorted(
            line.timesheet_id.timesheet_ids, key=lambda e: e.date)
        self.assertEqual(
            len(time_entries), 1, 'Incorrect number of time entries created')
        self.assertEqual(time_entries[0].date, '2000-01-01')
        self.assertEqual(time_entries[0].unit_amount, 1.2)
