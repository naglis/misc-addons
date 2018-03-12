# -*- coding: utf-8 -*-
# Copyright 2017 Naglis Jonaitis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import base64

from odoo import exceptions, tests

from ..utils import DEFAULT_DATE_FORMAT
from .common import build_csv

EMPLOYEE1_NAME = u'Jim Halpert'
EMPLOYEE2_NAME = u'Dwight Schrute'
PROJECT1_NAME = u'The Office'
COMMENT1 = u'Messing with Dwight'
COMMENT2 = u'Investigating'
HOURS1 = 1.4
HOURS2 = 2.3
HOURS3 = 3.9
DATE1 = u'2000-01-01'
DATE2 = u'2000-01-02'
DATE3 = u'2000-01-03'
ENTRY1 = {
    'date': DATE1,
    'user': EMPLOYEE1_NAME,
    'project': PROJECT1_NAME,
    'hours': unicode(HOURS1),
    'comment': COMMENT1,
}
ENTRY2 = {
    'date': DATE2,
    'user': EMPLOYEE2_NAME,
    'project': PROJECT1_NAME,
    'hours': unicode(HOURS2),
    'comment': COMMENT2,
}
ENTRY3 = ENTRY1.copy()
ENTRY3.update({
    'hours': unicode(HOURS3),
    'date': DATE3,
})
CSV1 = build_csv([ENTRY1])
CSV12 = build_csv([ENTRY1, ENTRY2])
CSV13 = build_csv([ENTRY1, ENTRY3])
CSV123 = build_csv([ENTRY1, ENTRY2, ENTRY3])


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
        self.project1 = self.env['project.project'].create({
            'name': PROJECT1_NAME,
            'allow_timesheets': True,
        })
        self.model = self.env['op.import']

    def assertLen(self, sequence, expected_length, msg=None):
        self.assertEqual(len(sequence), expected_length, msg=msg)

    def create_wizard(self, csv_file, **overrides):
        values = {
            'csv_file': base64.b64encode(csv_file),
            'date_format': DEFAULT_DATE_FORMAT,
        }
        if overrides:
            values.update(overrides)
        return self.model.create(values)

    def test_parse_csv_file_empty_CSV3_raises_ValidationError(self):
        wizard = self.create_wizard(build_csv([]))
        with self.assertRaises(exceptions.ValidationError):
            wizard.action_upload_file()

    def test_upload_file_one_entry_creates_one_line_with_correct_data(self):
        wizard = self.create_wizard(CSV1)
        wizard.action_upload_file()
        lines = wizard.time_entry_ids
        self.assertLen(lines, 1, 'Incorrect number of lines created')
        line = lines[0]
        self.assertEqual(
            line.op_employee_map_id.op_employee_name, EMPLOYEE1_NAME)
        self.assertEqual(line.project_id, self.project1)
        self.assertAlmostEqual(
            line.hours, HOURS1, places=2,
            msg='Incorrect worked hours value loaded',
        )
        self.assertEqual(line.comment, COMMENT1)

    def test_upload_file_employee_with_exact_name_is_found(self):
        wizard = self.create_wizard(CSV1)
        wizard.action_upload_file()
        lines = wizard.time_entry_ids.filtered(
            lambda e: e.op_employee_map_id.employee_id == self.employee1)
        self.assertLen(lines, 1)

    def test_import_file_timesheet_with_correct_data_is_created(self):
        wizard = self.create_wizard(CSV1)
        wizard.action_upload_file()
        action = wizard.action_import_file()
        lines = self.env['account.analytic.line'].browse(
            action.get('domain')[0][2])
        self.assertLen(lines, 1, 'Incorrect number of time entries created')
        line = lines[0]
        self.assertEqual(line.user_id, self.user1)
        self.assertEqual(line.date, DATE1)
        self.assertEqual(line.unit_amount, HOURS1)
