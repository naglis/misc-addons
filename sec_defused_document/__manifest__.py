# Copyright 2018 Naglis Jonaitis
# License LGPL-3 or later (https://www.gnu.org/licenses/lgpl).
{
    'name': 'Defuse Document Index',
    'version': '11.0.1.0.0',
    'author': 'Naglis Jonaitis',
    'category': 'Security',
    'website': 'https://naglis.me/',
    'license': 'LGPL-3',
    'summary': 'Prevent XML based attacks via Odoo document indexing feature',
    'depends': [
        'document',
    ],
    'external_dependencies': {
        'python': [
            'defusedxml',
        ],
    },
    'images': [
        'static/description/main_screenshot.png',
    ],
    'installable': True,
    'auto_install': True,
}
