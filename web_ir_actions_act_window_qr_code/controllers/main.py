# -*- coding: utf-8 -*-
# Copyright 2018 Naglis Jonaitis
# License LGPL-3 or later (https://www.gnu.org/licenses/lgpl).

import io

import qrcode

from odoo import _, exceptions, http


class QRCodeController(http.Controller):

    @http.route([
        '/web/qrcode',
    ], type='json', auth='user')
    def qrcode(self, data):
        # TODO: Make QR code parameters configurable.
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        try:
            qr.make(fit=True)
        except qrcode.exceptions.DataOverflowError:
            raise exceptions.ValidationError(_(
                u'Data size exceeds the QR code storage capacity.'))

        buf = io.BytesIO()
        qr.make_image().save(buf)

        return {
            'image': buf.getvalue(),
        }
