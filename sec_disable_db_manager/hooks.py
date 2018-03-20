# -*- coding: utf-8 -*-
# Copyright Odoo S.A.
# Copyright 2018 Naglis Jonaitis
# License LGPL-3 or later (https://www.gnu.org/licenses/lgpl).

import logging

import odoo
from decorator import decorator
from odoo.exceptions import AccessDenied
from odoo.service import db

_logger = logging.getLogger(__name__)


# Based on original function by Odoo S.A.: https://git.io/vxn5M
# Modified to conform to PEP-8.
def check_db_management_enabled(method):
    def if_db_mgt_enabled(method, self, *args, **kwargs):
        if not odoo.tools.config['list_db']:
            _logger.error('Database management functions blocked, '
                          'admin disabled database listing')
            raise AccessDenied()
        return method(self, *args, **kwargs)
    return decorator(if_db_mgt_enabled, method)


def disable_db_service():
    for func_name in (
        'exp_create_database',
        'exp_duplicate_database',
        'exp_drop',
        'exp_dump',
        'dump_db_manifest',
        'dump_db',
        'exp_restore',
        'restore_db',
        'exp_rename',
        'exp_change_admin_password',
        'exp_migrate_databases',
    ):
        setattr(
            db, func_name, check_db_management_enabled(getattr(db, func_name)))
