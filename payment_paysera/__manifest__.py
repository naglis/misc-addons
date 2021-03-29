# Copyright 2018-2019 Naglis Jonaitis
# License AGPL-3 or later (https://www.gnu.org/licenses/agpl).
{
    'name': 'Paysera Payment Acquirer',
    'category': 'eCommerce',
    'license': 'AGPL-3',
    'summary': 'Support for Paysera payments',
    'version': '12.0.1.2.0',
    'author': 'Naglis Jonaitis',
    'depends': [
        'payment',
        'website_payment',
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
    'post_init_hook': 'create_missing_journal_for_acquirers',
    'installable': True,
}
