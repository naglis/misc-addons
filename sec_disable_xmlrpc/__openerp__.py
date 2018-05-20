# -*- coding: utf-8 -*-
# Copyright 2018 Naglis Jonaitis
# License AGPL-3 or later (https://www.gnu.org/licenses/agpl).
{
    'name': 'Disable XML-RPC',
    'version': '9.0.1.0.1',
    'author': 'Naglis Jonaitis',
    'website': 'https://naglis.me/',
    'license': 'AGPL-3',
    'post_load': 'disable_xmlrpc',
    'summary': 'Disable Odoo XML-RPC endpoints',
    'description': '''
===============
Disable XML-RPC
===============

Reduce attack surface by disabling Odoo XML-RPC endpoints.
    ''',
    'category': 'Security',
    'depends': [
        'sec_base_patch',
    ],
    'images': [
        'static/description/main_screenshot.png',
    ],
    'installable': True,
}
