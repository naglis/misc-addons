# -*- coding: utf-8 -*-
# This file is part of Odoo. The COPYRIGHT file at the top level of
# this module contains the full copyright notices and license terms.

import io

import unittest2

from .. import utils


class TestParse(unittest2.TestCase):

    def test_parse_empty_csv_returns_zero_entries(self):
        fobj = io.BytesIO(
            'Member,2000-01-01,2000-01-02\n'
        )
        entries = utils.parse_op_timesheet_csv(fobj)
        self.assertFalse(entries)

    def test_parse_cell_non_float_raises_invalid_time_entry_exception(self):
        fobj = io.BytesIO(
            'Member,2000-01-01,2000-01-02\n'
            'Nancy Wheeler,1.0,a'
        )
        with self.assertRaises(utils.InvalidTimeEntryException):
            utils.parse_op_timesheet_csv(fobj)

    def test_parse_totals_column_is_removed(self):
        fobj = io.BytesIO(
            'Member,2000-01-01,2000-01-02,Total\n'
            'Nancy Wheeler,1.0,1.2,2.2'
        )
        self.assertNotIn('Total', utils.parse_op_timesheet_csv(fobj))
