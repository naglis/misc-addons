# Copyright 2018 Naglis Jonaitis
# License LGPL-3 or later (https://www.gnu.org/licenses/lgpl).

import io
import zipfile

from odoo.tests import common

# XML bomb example from Wikipedia
# Source: https://en.wikipedia.org/wiki/Billion_laughs_attack#Code_example
MALICIOUS_XML = '''<?xml version="1.0"?>
<!DOCTYPE lolz [
 <!ENTITY lol "lol">
 <!ELEMENT lolz (#PCDATA)>
 <!ENTITY lol1 "&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;">
 <!ENTITY lol2 "&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;">
 <!ENTITY lol3 "&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;">
 <!ENTITY lol4 "&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;">
 <!ENTITY lol5 "&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;">
 <!ENTITY lol6 "&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;">
 <!ENTITY lol7 "&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;">
 <!ENTITY lol8 "&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;">
 <!ENTITY lol9 "&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;">
]>
<lolz>&lol9;</lolz>
'''


def build_malicious_xml_zip(xml_bomb_path):
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, mode='w') as zf:
        zf.writestr(xml_bomb_path, MALICIOUS_XML)
    return zip_buffer.getvalue()


class TestIrAttachment(common.TransactionCase):
    '''The failure of these tests would most likely result in timeout.'''

    def test_index_docx_with_malicious_xml_returns_empty_string(self):
        self.assertFalse(self.env['ir.attachment']._index_docx(
            build_malicious_xml_zip('word/document.xml')))

    def test_index_pptx_with_malicious_xml_returns_empty_string(self):
        self.assertFalse(self.env['ir.attachment']._index_pptx(
            build_malicious_xml_zip('ppt/slides/slide1.xml')))

    def test_index_xlsx_with_malicious_xml_returns_empty_string(self):
        self.assertFalse(self.env['ir.attachment']._index_xlsx(
            build_malicious_xml_zip('xl/sharedStrings.xml')))

    def test_index_opendoc_with_malicious_xml_returns_empty_string(self):
        self.assertFalse(self.env['ir.attachment']._index_opendoc(
            build_malicious_xml_zip('content.xml')))
