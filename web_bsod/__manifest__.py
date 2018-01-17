# -*- coding: utf-8 -*-
# Copyright 2018 Naglis Jonaitis
# License LGPL-3 or later (https://www.gnu.org/licenses/lgpl).
{
    'name': 'Blue Screen of Death',
    'version': '11.0.1.0.0',
    'author': 'Naglis Jonaitis',
    'category': 'Technical Settings',
    'website': (
        'https://naglis.me/post/custom-exception-handling-in-odoo-client/'),
    'license': 'LGPL-3',
    'summary': 'Sometimes a simple error dialog is just not enough',
    'depends': [
        'web',
    ],
    'data': [
        'views/assets.xml',
    ],
    'qweb': [
        'static/src/xml/crash_manager.xml',
    ],
    'images': [
        'static/description/main_screenshot.gif',
    ],
    'installable': True,
    'application': False,
}
