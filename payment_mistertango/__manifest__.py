# -*- coding: utf-8 -*-
# Copyright 2018 Naglis Jonaitis
# License AGPL-3 or later (https://www.gnu.org/licenses/agpl).
{
    'name': 'Mistertango Payment Acquirer',
    'version': '10.0.1.0.3',
    'author': 'Naglis Jonaitis',
    'category': 'eCommerce',
    'website': 'https://naglis.me/',
    'license': 'AGPL-3',
    'summary': 'Collect payments via Mistertango.com',
    'description': '''
============================
Mistertango Payment Acquirer
============================

Mistertango payment acquirer implementation.
''',
    'depends': [
        'payment',
        'website',
    ],
    'external_dependencies': {
        'python': [
            'cryptography',
        ],
    },
    'data': [
        'views/payment_acquirer.xml',
        'views/payment_transaction.xml',
        'views/website_templates.xml',
        'data/payment_acquirer.xml',
    ],
    'demo': [
        'demo/payment_transaction.xml',
    ],
    'images': [
        'static/description/main_screenshot.png',
    ],
    'installable': True,
    'application': False,
}
