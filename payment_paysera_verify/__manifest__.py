# -*- coding: utf-8 -*-
# Copyright 2018 Naglis Jonaitis
# License AGPL-3 or later (https://www.gnu.org/licenses/agpl).
{
    'name': 'Paysera Verification',
    'version': '10.0.1.0.0',
    'author': 'Naglis Jonaitis',
    'category': 'Extra Tools',
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
