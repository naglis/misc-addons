# -*- coding: utf-8 -*-
# Copyright 2018 Naglis Jonaitis
# License AGPL-3 or later (https://www.gnu.org/licenses/agpl).

import unittest
import xmlrpclib

from odoo import release, tests
from odoo.tools import config as odoo_config

from .. import (
    disable_xmlrpc,
    enable_xmlrpc,
)

XMLRPC_CALL_BODY = '''<?xml version="1.0" encoding="utf-8"?>
<methodCall>
   <methodName>version</methodName>
   <params>
   </params>
</methodCall>'''


@unittest.skipIf(
    bool(odoo_config.get('workers')),
    'HTTP test cases do not work in worker mode',
)
class TestDisableXMLRPC(tests.common.HttpCase):

    def setUp(self):
        super(TestDisableXMLRPC, self).setUp()
        enable_xmlrpc()

    def tearDown(self):
        super(TestDisableXMLRPC, self).tearDown()
        enable_xmlrpc()

    def test_xmlrpc_endpoint_is_disabled_when_patched(self):
        disable_xmlrpc()
        for endpoint in [
            '/xmlrpc/common',
            '/xmlrpc/2/common',
            '/xmlrpc/db',
            '/xmlrpc/2/db',
            '/xmlrpc/object',
            '/xmlrpc/2/object',
        ]:
            response = self.url_open(
                endpoint, data=XMLRPC_CALL_BODY, timeout=30)
            self.assertEqual(response.code, 404)

    def test_xmlrpc_endpoint_is_enabled_when_unpatched(self):
        enable_xmlrpc()
        for endpoint in [
            '/xmlrpc/common',
            '/xmlrpc/2/common',
        ]:
            response = self.url_open(
                endpoint, data=XMLRPC_CALL_BODY, timeout=30)
            self.assertEqual(response.code, 200)
            result = xmlrpclib.loads(response.read())[0][0]
            self.assertEqual(result['server_serie'], release.serie)
