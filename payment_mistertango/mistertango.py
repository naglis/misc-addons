# -*- coding: utf-8 -*-
# Copyright 2018 Naglis Jonaitis
# License AGPL-3 or later (https://www.gnu.org/licenses/agpl).

import base64
import collections
import logging

_logger = logging.getLogger(__name__)

try:
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives.ciphers import (
        Cipher,
        algorithms,
        modes,
    )
except ImportError:  # pragma: no cover
    _logger.warning(
        u'"cryptography" Python package is either not installed, '
        u'or the installed version is incompatible.')

MISTERTANGO_PAYMENT_STATUS_CONFIRMED = 'CONFIRMED'
MISTERTANGO_PAYMENT_STATUS_NOT_CONFIRMED = 'UNCONFIRMED'
MISTERTANGO_PAYMENT_STATUSES = frozenset([
    MISTERTANGO_PAYMENT_STATUS_CONFIRMED,
    MISTERTANGO_PAYMENT_STATUS_NOT_CONFIRMED,
])
MISTERTANGO_SUPPORTED_CURRENCIES = (
    'EUR',
)
MISTERTANGO_MARKETS = (
    ('LT', u'Lithuania'),
    ('LV', u'Latvia'),
    ('EE', u'Estonia'),
    ('FI', u'Finland'),
    ('FR', u'France'),
    ('NL', u'Netherlands'),
    ('IT', u'Italy'),
    ('ES', u'Spain'),
    ('SK', u'Slovakia'),
    ('DE', u'Germany'),
    ('UA', u'Ukraine'),
    ('HU', u'Hungary'),
    ('RO', u'Romania'),
    ('BG', u'Bulgaria'),
    ('CZ', u'Czech Republic'),
)
MISTERTANGO_LANGUAGES = (
    ('lt', u'Lithuanian'),
    ('en', u'English'),
    ('lv', u'Latvian'),
    ('et', u'Estonian'),
    ('ru', u'Russian'),
    ('fi', u'Finnish'),
    ('fr', u'French'),
    ('nl', u'Dutch'),
    ('it', u'Italian'),
    ('es', u'Spanish'),
    ('uk', u'Ukrainian'),
    ('hu', u'Hungarian'),
    ('ro', u'Romanian'),
    ('bg', u'Bulgarian'),
    ('cs', u'Czech'),
    ('sk', u'Slovak'),
    ('de', u'German'),
)
MISTERTANGO_PAYMENT_TYPES = collections.OrderedDict([
    ('MISTERTANGO', u'Paid via Mistertango wallet'),
    ('BITCOIN', u'Paid with Bitcoin e-currency'),
    ('BANK_LINK', u'Paid via fast payment'),
    ('CREDIT_CARD', u'Paid with credit card'),
    ('BANK_TRANSFER', u'Paid via bank transfer (wired payment)'),
])

STRIP_CHARS = ' \t\n\r\0\x0B'


def decrypt(encoded_text, key):
    key = key.ljust(32, b'\0')

    backend = default_backend()
    encoded_text = encoded_text.strip(STRIP_CHARS)
    ciphertext_dec = base64.b64decode(encoded_text)

    algorithm = algorithms.AES(key)
    iv_size = algorithm.block_size / 8
    iv = ciphertext_dec[:iv_size]
    ciphertext_dec = ciphertext_dec[iv_size:]
    cipher = Cipher(algorithm, modes.CBC(iv), backend=backend)
    decryptor = cipher.decryptor()

    plaintext = decryptor.update(ciphertext_dec) + decryptor.finalize()
    return plaintext.strip(STRIP_CHARS)
