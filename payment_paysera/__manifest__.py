# -*- coding: utf-8 -*-
{
    'name': 'Paysera Payment Acquirer',
    'category': 'eCommerce',
    'license': 'AGPL-3',
    'summary': 'Support for Paysera payments',
    'version': '10.0.2.0.1',
    'author': 'Naglis Jonaitis',
    'depends': [
        'payment',
    ],
    'external_dependencies': {
        'python': [
            'cryptography',
        ],
    },
    'data': [
        'views/payment_acquirer.xml',
        'views/website_templates.xml',
        'data/payment_acquirer.xml',
    ],
    'images': [
        'static/description/main_screenshot.jpg',
    ],
    'installable': True,
    'application': False,
}
