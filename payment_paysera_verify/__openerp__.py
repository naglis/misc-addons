# -*- coding: utf-8 -*-
{
    'name': 'Paysera Verification',
    'version': '8.0.1.0.0',
    'author': 'Naglis Jonaitis',
    'category': 'Invoicing & Payments',
    'license': 'AGPL-3',
    'summary': 'Verify ownership of your site with Paysera.',
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
