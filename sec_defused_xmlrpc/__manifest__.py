# -*- coding: utf-8 -*-
# Copyright 2018 Naglis Jonaitis
# License AGPL-3 or later (https://www.gnu.org/licenses/agpl).
{
    'name': 'Defuse XML-RPC',
    'version': '11.0.1.0.1',
    'author': 'Naglis Jonaitis',
    'category': 'Security',
    'website': 'https://naglis.me/',
    'license': 'AGPL-3',
    'post_load': 'install_defusedxml',
    'summary': 'Mitigate XML attacks in Odoo\'s XML-RPC',
    'external_dependencies': {
        'python': [
            'defusedxml',
        ],
    },
    'images': [
        'static/description/main_screenshot.png',
    ],
    'installable': True,
}
