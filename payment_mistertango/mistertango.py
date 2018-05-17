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
        '"cryptography" Python package is either not installed, '
        'or the installed version is incompatible.')

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
    ('LT', 'Lithuania'),
    ('LV', 'Latvia'),
    ('EE', 'Estonia'),
    ('FI', 'Finland'),
    ('FR', 'France'),
    ('NL', 'Netherlands'),
    ('IT', 'Italy'),
    ('ES', 'Spain'),
    ('SK', 'Slovakia'),
    ('DE', 'Germany'),
    ('UA', 'Ukraine'),
    ('HU', 'Hungary'),
    ('RO', 'Romania'),
    ('BG', 'Bulgaria'),
    ('CZ', 'Czech Republic'),
)
MISTERTANGO_LANGUAGES = (
    ('lt', 'Lithuanian'),
    ('en', 'English'),
    ('lv', 'Latvian'),
    ('et', 'Estonian'),
    ('ru', 'Russian'),
    ('fi', 'Finnish'),
    ('fr', 'French'),
    ('nl', 'Dutch'),
    ('it', 'Italian'),
    ('es', 'Spanish'),
    ('uk', 'Ukrainian'),
    ('hu', 'Hungarian'),
    ('ro', 'Romanian'),
    ('bg', 'Bulgarian'),
    ('cs', 'Czech'),
    ('sk', 'Slovak'),
    ('de', 'German'),
)
MISTERTANGO_PAYMENT_TYPES = collections.OrderedDict([
    ('MISTERTANGO', 'Paid via Mistertango wallet'),
    ('BITCOIN', 'Paid with Bitcoin e-currency'),
    ('BANK_LINK', 'Paid via fast payment'),
    ('CREDIT_CARD', 'Paid with credit card'),
    ('BANK_TRANSFER', 'Paid via bank transfer (wired payment)'),
])

STRIP_CHARS = b' \t\n\r\0\x0B'


def decrypt(b64_ciphertext: bytes, key: bytes) -> bytes:
    key = key.ljust(32, b'\0')

    backend = default_backend()
    b64_ciphertext = b64_ciphertext.strip(STRIP_CHARS)
    ciphertext_dec = base64.b64decode(b64_ciphertext)

    algorithm = algorithms.AES(key)
    iv_size = algorithm.block_size // 8
    iv = ciphertext_dec[:iv_size]
    ciphertext_dec = ciphertext_dec[iv_size:]
    cipher = Cipher(algorithm, modes.CBC(iv), backend=backend)
    decryptor = cipher.decryptor()

    plaintext = decryptor.update(ciphertext_dec) + decryptor.finalize()
    return plaintext.strip(STRIP_CHARS)
