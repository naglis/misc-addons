# Copyright 2018 Naglis Jonaitis
# License AGPL-3 or later (https://www.gnu.org/licenses/agpl).

import unittest

from odoo import tests
from odoo.tools import config as odoo_config


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

    def test_xmlrpc_endpoint_is_disabled(self):
        for endpoint in [
            '/xmlrpc/common',
            '/xmlrpc/2/common',
            '/xmlrpc/db',
            '/xmlrpc/2/db',
            '/xmlrpc/object',
            '/xmlrpc/2/object',
        ]:
            with self.subTest(endpoint=endpoint):
                response = self.url_open(
                    endpoint, data=XMLRPC_CALL_BODY, timeout=30)
                self.assertEqual(response.status_code, 404)
