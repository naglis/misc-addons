# -*- coding: utf-8 -*-
# Copyright 2018 Naglis Jonaitis
# License AGPL-3 or later (https://www.gnu.org/licenses/agpl).

import logging

import defusedxml.xmlrpc  # pylint: disable=missing-import-error
import odoo

DEFAULT_MAX_DATA = 45 * 1024 * 1024  # 45 MB
_ORIGINAL_MAX_DATA = defusedxml.xmlrpc.MAX_DATA
_logger = logging.getLogger(__name__)


def install_defusedxml():
    max_data = odoo.tools.config.get('defused_xml_max_data', DEFAULT_MAX_DATA)
    try:
        max_data = int(max_data)
    except (TypeError, ValueError):
        _logger.error(
            u'Expected an integer for "defused_xml_max_data" '
            u'configuration value, got %r. '
            u'Falling back to the default value.',
            max_data)
        max_data = DEFAULT_MAX_DATA
    _logger.info(
        u'Installing defused XML for XML-RPC (max_data=%d)', max_data)
    defusedxml.xmlrpc.monkey_patch()
    defusedxml.xmlrpc.MAX_DATA = max_data


def uninstall_defusedxml():
    '''Unmonkey-patch xmlrpclib and restore original MAX_DATA value.'''
    defusedxml.xmlrpc.unmonkey_patch()
    defusedxml.xmlrpc.MAX_DATA = _ORIGINAL_MAX_DATA
