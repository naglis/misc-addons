# -*- coding: utf-8 -*-
# Copyright 2017 Versada UAB
# License AGPL-3 or later (https://www.gnu.org/licenses/agpl).
{
    'name': 'OpenProject Initial User Mapping',
    'version': '10.0.1.0.0',
    'author': 'Versada',
    'category': 'Extra Tools',
    'website': 'https://versada.eu',
    'license': 'AGPL-3',
    'summary': 'Map OpenProject users with existing Odoo users',
    'depends': [
        'connector_openproject',
    ],
    'data': [
        'wizards/op_user_map.xml',
    ],
    'installable': True,
    'application': False,
}
