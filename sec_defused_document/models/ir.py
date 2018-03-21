# Copyright Odoo S.A.
# Copyright 2018 Naglis Jonaitis
# License LGPL-3 or later (https://www.gnu.org/licenses/lgpl).

import io
import logging
import zipfile

from odoo import models
from odoo.addons.document.models.ir_attachment import textToString

_logger = logging.getLogger(__name__)

try:
    from defusedxml import minidom
except ImportError:
    _logger.info(
        'defusedxml is not installed. XML-based attacks via attachment '
        'indexing will not be defused.')
    from xml.dom import minidom


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    # '_index_' methods from Odoo community edition, changed to use
    # `defusedxml.minidom`, if available and to conform to line length
    # requirements.
    # Source: https://git.io/vxCQS
    def _index_docx(self, bin_data):
        '''Index Microsoft .docx documents'''
        buf = u""
        f = io.BytesIO(bin_data)
        if zipfile.is_zipfile(f):
            try:
                zf = zipfile.ZipFile(f)
                content = minidom.parseString(zf.read("word/document.xml"))
                for val in ["w:p", "w:h", "text:list"]:
                    for element in content.getElementsByTagName(val):
                        buf += textToString(element) + "\n"
            except Exception:
                pass
        return buf

    def _index_pptx(self, bin_data):
        '''Index Microsoft .pptx documents'''

        buf = u""
        f = io.BytesIO(bin_data)
        if zipfile.is_zipfile(f):
            try:
                zf = zipfile.ZipFile(f)
                zf_filelist = [x for x in zf.namelist()
                               if x.startswith('ppt/slides/slide')]
                for i in range(1, len(zf_filelist) + 1):
                    content = minidom.parseString(
                        zf.read('ppt/slides/slide%s.xml' % i))
                    for val in ["a:t"]:
                        for element in content.getElementsByTagName(val):
                            buf += textToString(element) + "\n"
            except Exception:
                pass
        return buf

    def _index_xlsx(self, bin_data):
        '''Index Microsoft .xlsx documents'''

        buf = u""
        f = io.BytesIO(bin_data)
        if zipfile.is_zipfile(f):
            try:
                zf = zipfile.ZipFile(f)
                content = minidom.parseString(zf.read("xl/sharedStrings.xml"))
                for val in ["t"]:
                    for element in content.getElementsByTagName(val):
                        buf += textToString(element) + "\n"
            except Exception:
                pass
        return buf

    def _index_opendoc(self, bin_data):
        '''Index OpenDocument documents (.odt, .ods...)'''

        buf = u""
        f = io.BytesIO(bin_data)
        if zipfile.is_zipfile(f):
            try:
                zf = zipfile.ZipFile(f)
                content = minidom.parseString(zf.read("content.xml"))
                for val in ["text:p", "text:h", "text:list"]:
                    for element in content.getElementsByTagName(val):
                        buf += textToString(element) + "\n"
            except Exception:
                pass
        return buf
