# -*- coding: utf-8 -*-
# This file is part of Odoo. The COPYRIGHT file at the top level of
# this module contains the full copyright notices and license terms.

import base64

from openerp import exceptions, tests

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
        self.partner1 = self.env['res.partner'].create({
            'name': EMPLOYEE1_NAME,
        })
        self.user1 = self.env['res.users'].create({
            'name': EMPLOYEE1_NAME,
            'login': 'nancy',
            'partner_id': self.partner1.id,
        })
        self.employee1 = self.env['hr.employee'].create({
            'name': EMPLOYEE1_NAME,
            'user_id': self.user1.id,
        })
        self.account1 = self.env['account.analytic.account'].create({
            'name': 'Test Account',
            'type': 'normal',
        })
        self.model = self.env['op.timesheet']

    def create_wizard(self, csv_file, **overrides):
        values = {
            'account_id': self.account1.id,
            'csv_file': base64.b64encode(csv_file),
            'ignore_totals': False,
        }
        if overrides:
            values.update(overrides)
        return self.env['op.timesheet'].create(values)

    def test_parse_csv_file_empty_CSV3_raises_ValidationError(self):
        wizard = self.create_wizard(CSV3)
        with self.assertRaises(exceptions.ValidationError):
            wizard._parse_csv_file()

    def test_parse_csv_file_CSV2_ignore_totals_removes_last_line(self):
        wizard = self.create_wizard(CSV2, ignore_totals=True)
        entries = wizard._parse_csv_file()
        self.assertEqual(len(entries), 1, 'Incorrect number of lines returned')
        self.assertNotEqual(entries.keys()[0], 'Total')

    def test_date_to_earlier_than_date_from_raises_ValidationError(self):
        wizard = self.create_wizard(CSV1, date_from='2000-01-02')
        with self.assertRaises(exceptions.ValidationError):
            wizard.date_to = '2000-01-01'

    def test_upload_file_CSV1_correct_date_from_date_to_values_are_set(self):
        wizard = self.create_wizard(CSV1)
        wizard.action_upload_file()
        self.assertEqual(wizard.date_from, '2000-01-01')
        self.assertEqual(wizard.date_to, '2000-01-02')

    def test_upload_file_CSV1_creates_one_line_with_correct_data(self):
        wizard = self.create_wizard(CSV1)
        wizard.action_upload_file()
        lines = wizard.employee_map_ids
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
        lines = wizard.employee_map_ids.filtered(
            lambda m: m.employee_id == self.employee1)
        self.assertEqual(len(lines), 1)

    def test_import_file_CSV4_timesheet_with_correct_data_is_created(self):
        wizard = self.create_wizard(CSV4)
        wizard.action_upload_file()
        wizard.action_import_file()
        lines = wizard.employee_map_ids.filtered(lambda l: l.timesheet_id)
        self.assertEqual(len(lines), 1, 'Incorrect number of lines created')
        line = lines[0]
        self.assertEqual(line.timesheet_id.employee_id, self.employee1)
        time_entries = line.timesheet_id.timesheet_ids.sorted(lambda e: e.date)
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
        lines = wizard.employee_map_ids.filtered(lambda l: l.timesheet_id)
        self.assertEqual(len(lines), 1, 'Incorrect number of lines created')
        line = lines[0]
        time_entries = line.timesheet_id.timesheet_ids.sorted(lambda e: e.date)
        self.assertEqual(
            len(time_entries), 1, 'Incorrect number of time entries created')
        self.assertEqual(time_entries[0].date, '2000-01-01')
        self.assertEqual(time_entries[0].unit_amount, 1.2)
