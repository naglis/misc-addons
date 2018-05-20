# -*- coding: utf-8 -*-
# Copyright 2018 Naglis Jonaitis
# License AGPL-3 or later (https://www.gnu.org/licenses/agpl).
{
    'name': 'Defuse XML-RPC',
    'version': '10.0.1.0.1',
    'author': 'Naglis Jonaitis',
    'category': 'Security',
    'website': 'https://naglis.me/',
    'license': 'AGPL-3',
    'post_load': 'install_defusedxml',
    'summary': 'Mitigate XML attacks in Odoo\'s XML-RPC',
    'description': '''
==============
Defuse XML-RPC
==============

This module mitigates several XML-related attacks which are possible via Odoo's
XML-RPC, most notably:

- Billion Laughs (also known as the exponential entity expansion) attack;
- gzip decompression bombs.
''',
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
