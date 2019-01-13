# -*- coding: utf-8 -*-
# Copyright 2018-2019 Naglis Jonaitis
# License LGPL-3 or later (https://www.gnu.org/licenses/lgpl).
{
    'name': 'Disable Database Manager',
    'version': '10.0.1.0.1',
    'author': 'Naglis Jonaitis',
    'category': 'Security',
    'website': 'https://naglis.me/',
    'license': 'LGPL-3',
    'depends': [
        'web',
    ],
    'data': [
    ],
    'images': [
        'static/description/main_screenshot.png',
    ],
    'installable': True,
    'auto_install': False,
    'post_load': 'disable_db_service',
}
