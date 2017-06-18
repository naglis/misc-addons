# -*- coding: utf-8 -*-
{
    'name': 'Paysera Quality Sign',
    'version': '10.0.1.0.0',
    'author': 'Naglis Jonaitis',
    'category': 'Invoicing & Payments',
    'license': 'AGPL-3',
    'summary': 'Display Paysera Quality Sign on your website',
    'depends': [
        'payment_paysera',
        'website',
    ],
    'data': [
        'views/payment_acquirer.xml',
        'views/website_templates.xml',
    ],
    'installable': True,
    'application': False,
}
