# -*- coding: utf-8 -*-
# Copyright 2017 Naglis Jonaitis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'OpenProject Timesheet Import',
    'version': '10.0.0.2.0',
    'author': 'Naglis Jonaitis',
    'category': 'Human Resources',
    'website': 'https://github.com/naglis/',
    'license': 'AGPL-3',
    'summary': 'Import timesheets from OpenProject',
    'depends': [
        'hr_timesheet_sheet',
    ],
    'data': [
        'wizards/timesheet_import_view.xml',
    ],
    'installable': False,
    'application': False,
}
