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
        'data/payment_acquirer.xml',
        'views/payment_acquirer.xml',
        'views/website_templates.xml',
    ],
    'installable': True,
    'application': False,
}
