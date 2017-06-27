# -*- coding: utf-8 -*-
# Copyright 2017 Naglis Jonaitis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import unittest

from .common import build_csv_io
from .. import utils


class TestParse(unittest.TestCase):

    def test_parse_empty_csv_returns_zero_entries(self):
        fobj = build_csv_io([])
        entries = utils.parse_op_timesheet_csv(fobj, skip_first=True)
        self.assertFalse(entries)

    def test_parse_cell_non_float_raises_invalid_time_entry_exception(self):
        fobj = build_csv_io([{
            'date': u'2000-01-02',
            'user': u'Jim Halpert',
            'project': u'The Office',
            'hours': u'foo',
            'comment': u'Messing with Dwight',
        }])
        with self.assertRaises(utils.InvalidTimeEntryException):
            utils.parse_op_timesheet_csv(fobj)
