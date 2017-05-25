# -*- coding: utf-8 -*-
# This file is part of Odoo. The COPYRIGHT file at the top level of
# this module contains the full copyright notices and license terms.
{
    'name': 'OpenProject Timesheet Import',
    'version': '10.0.0.2.0',
    'author': 'Naglis Jonaitis',
    'category': 'Human Resources',
    'website': 'https://github.com/naglis/',
    'license': 'AGPL-3',
    'summary': 'OpenProject time entries CSV import.',
    'depends': [
        'hr_timesheet_sheet',
    ],
    'data': [
        'wizards/timesheet_import_view.xml',
    ],
    'installable': False,
    'application': False,
}
