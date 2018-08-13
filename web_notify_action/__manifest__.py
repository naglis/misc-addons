# Copyright 2018 Naglis Jonaitis
# License LGPL-3 or later (https://www.gnu.org/licenses/agpl).
{
    'name': 'User Action Notifications',
    'version': '11.0.1.0.1',
    'author': 'Naglis Jonaitis',
    'category': 'Technical Settings',
    'website': 'https://naglis.me/',
    'summary': 'Server-initiated action notifications on steroids!',
    'license': 'LGPL-3',
    'depends': [
        'bus',
    ],
    'data': [
        'views/templates.xml',
    ],
    'qweb': [
        'static/src/xml/action_notification.xml',
    ],
    'installable': True,
}
