# -*- coding: utf-8 -*-
# This file is part of OpenERP. The COPYRIGHT file at the top level of
# this module contains the full copyright notices and license terms.
{
    'name': 'OpenProject Timesheet Import',
    'version': '7.0.0.2.0',
    'author': 'Naglis Jonaitis',
    'category': 'Human Resources',
    'website': 'https://github.com/naglis/',
    'licence': 'AGPL-3',
    'summary': 'OpenProject time entries CSV import.',
    'description': 'Allows import of employee time entries from OpenProject.',
    'depends': [
        'hr_timesheet_sheet',
    ],
    'data': [
        'wizards/timesheet_import_view.xml',
    ],
    'installable': True,
    'application': False,
}
