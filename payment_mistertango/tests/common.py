# -*- coding: utf-8 -*-
# Copyright 2018 Naglis Jonaitis
# License AGPL-3 or later (https://www.gnu.org/licenses/agpl).

import base64
import json
import os
import uuid

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import (
    Cipher,
    algorithms,
    modes,
)
from odoo.addons.payment.tests.common import PaymentAcquirerCommon
from odoo.tools import config as odoo_config

from ..mistertango import STRIP_CHARS

TEST_AMOUNT = 3.14
TEST_SECRET_KEY = 'Z0AqcwDbFkMNIgbzYalOlKwcNSHNEU'


def in_worker_mode():
    return bool(odoo_config.get('workers'))


def _encrypt(plaintext, key):
    key = key.ljust(32, b'\0')
    plaintext = plaintext.strip(STRIP_CHARS)

    backend = default_backend()
    algorithm = algorithms.AES(key)
    iv_size = algorithm.block_size / 8
    iv = os.urandom(iv_size)
    mode = modes.CBC(iv)
    cipher = Cipher(algorithm, mode, backend=backend)

    encryptor = cipher.encryptor()
    # Mistertango uses zero byte padding AKA null padding.
    plaintext = _null_pad(plaintext, algorithm.block_size / 8)
    ciphertext = encryptor.update(plaintext) + encryptor.finalize()
    ciphertext = '%s%s' % (iv, ciphertext)

    result = base64.b64encode(ciphertext)
    return result.strip(STRIP_CHARS)


def _null_pad(string, block_size):
    if not string:
        return string
    if block_size <= 0:
        raise ValueError('Invalid block size')
    width = len(string) + block_size - len(string) % block_size
    return string.ljust(width, b'\0')


def inc_byte(string, pos=0):
    if not string:
        return string
    c = chr((ord(string[pos]) + 1) % 256)
    return string[:pos] + c + string[pos + 1:]


def fake_callback(description, secret_key=TEST_SECRET_KEY, amount=TEST_AMOUNT,
                  currency='EUR', callback_uuid=None,
                  invoice_uuid=None, status='CONFIRMED',
                  acquirer_reference='FOO',
                  payment_type='MISTERTANGO',
                  paid_partly=False, **kwargs):
    if callback_uuid is None:
        callback_uuid = str(uuid.uuid4())
    if invoice_uuid is None:
        invoice_uuid = str(uuid.uuid4())
    custom = {
        'invoice': invoice_uuid,
        'status': 'paid',
        'data': {
            'amount': str(amount),
            'currency': currency,
            'description': acquirer_reference,
            'paid_partly': paid_partly,
            'status': status,
        },
        'custom_data': [
        ],
        'type': payment_type,
        'custom_type': '',
        'description': description,
        'contact': {
            'email': '',
            'contact_details': [
            ],
            'shipping_details': [
            ],
        },
    }
    values = {
        'amount': '',
        'callback_uuid': callback_uuid,
        'custom': json.dumps(custom),
        'currency': '',
        'details': '',
        'order_type': '',
        'order_uuid': '',
        'status': '',
        'uid': '',
    }
    data_hash = _encrypt(json.dumps(values), secret_key)
    values.update({'hash': data_hash})
    return values


class TestMistertangoCommon(PaymentAcquirerCommon):

    def setUp(self):
        super(TestMistertangoCommon, self).setUp()
        self.acquirer = self.browse_ref('payment_mistertango.acquirer_1')
        self.tx_1 = self.browse_ref('payment_mistertango.transaction_1')
        self.acquirer.mistertango_secret_key = TEST_SECRET_KEY
