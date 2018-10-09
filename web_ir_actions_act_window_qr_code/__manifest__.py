# -*- coding: utf-8 -*-
# Copyright 2018 Naglis Jonaitis
# License LGPL-3 or later (https://www.gnu.org/licenses/lgpl).
{
    'name': 'QR Code Window Action',
    'version': '12.0.1.0.0',
    'author': 'Naglis Jonaitis',
    'category': 'Technical Settings',
    'website': 'https://naglis.me/',
    'license': 'LGPL-3',
    'summary': 'Display QR code pop-ups from Python code',
    'depends': [
        'web',
    ],
    'external_dependencies': {
        'python': [
            'qrcode',
        ],
    },
    'data': [
        'views/templates.xml',
    ],
    'qweb': [
        'static/src/xml/qrcode_action.xml',
    ],
    'images': [
        'static/description/main_screenshot.png',
    ],
    'installable': True,
}
