# -*- coding: utf-8 -*-
# Copyright 2018 Naglis Jonaitis
# License AGPL-3 or later (https://www.gnu.org/licenses/agpl).

import logging

from odoo.addons.sec_base_patch.utils import (
    patch_func,
    unpatch_func,
)
from odoo.service import wsgi_server

_logger = logging.getLogger(__name__)


def disable_xmlrpc():
    _logger.info('Disabling XML-RPC')
    return patch_func(
        wsgi_server, 'wsgi_xmlrpc', lambda environ, start_response: None)


def enable_xmlrpc():
    _logger.info('Re-enabling XML-RPC')
    return unpatch_func(wsgi_server, 'wsgi_xmlrpc')
