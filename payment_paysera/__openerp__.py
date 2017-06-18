# -*- coding: utf-8 -*-
{
    'name': 'Paysera Payment Acquirer',
    'category': 'Hidden',
    'license': 'AGPL-3',
    'summary': 'Support for Paysera payments',
    'version': '8.0.2.0.0',
    'author': 'Naglis Jonaitis',
    'depends': [
        'payment',
    ],
    'external_dependencies': {
        'python': [
            'cryptography',
        ]
    },
    'data': [
        'views/payment_acquirer.xml',
        'views/website_templates.xml',
        'data/payment_acquirer.xml',
    ],
    'installable': False,
    'application': False,
}
