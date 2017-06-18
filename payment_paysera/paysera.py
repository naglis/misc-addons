# -*- coding: utf-8 -*-

import base64
import hashlib
import urllib

from cryptography import exceptions, x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric.padding import PKCS1v15
from cryptography.hazmat.primitives import hashes

PAYSERA_API_VERSION = '1.6'
PAYSERA_API_URL = 'https://www.paysera.com/pay/'

# Paysera's Public Key certificate.
# Refer to: https://www.webtopay.com/download/public.key
PAYSERA_CERT_PEM = '''
-----BEGIN CERTIFICATE-----
MIIECTCCA3KgAwIBAgIBADANBgkqhkiG9w0BAQUFADCBujELMAkGA1UEBhMCTFQx
EDAOBgNVBAgTB1ZpbG5pdXMxEDAOBgNVBAcTB1ZpbG5pdXMxHjAcBgNVBAoTFVVB
QiBFVlAgSW50ZXJuYXRpb25hbDEtMCsGA1UECxMkaHR0cDovL3d3dy5tb2tlamlt
YWkubHQvYmFua2xpbmsucGhwMRkwFwYDVQQDExB3d3cubW9rZWppbWFpLmx0MR0w
GwYJKoZIhvcNAQkBFg5wYWdhbGJhQGV2cC5sdDAeFw0wOTA3MjQxMjMxMTVaFw0x
NzEwMTAxMjMxMTVaMIG6MQswCQYDVQQGEwJMVDEQMA4GA1UECBMHVmlsbml1czEQ
MA4GA1UEBxMHVmlsbml1czEeMBwGA1UEChMVVUFCIEVWUCBJbnRlcm5hdGlvbmFs
MS0wKwYDVQQLEyRodHRwOi8vd3d3Lm1va2VqaW1haS5sdC9iYW5rbGluay5waHAx
GTAXBgNVBAMTEHd3dy5tb2tlamltYWkubHQxHTAbBgkqhkiG9w0BCQEWDnBhZ2Fs
YmFAZXZwLmx0MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDeT23V/kNtf/hr
Nae/ZsLfRZd8E+os6HZ9CbgvB+X659kBDBq5vjMDCVkY6sicn1fcFfuotEcbhKSK
DrDAQ+DmCMm96C7A4gqCC5OqmINauxYDdbie7V9GJWnbRXDs/5Mu722f5TuOUG3H
hN/vTg8uCxIrGIYv9idhvTbDyieVCwIDAQABo4IBGzCCARcwHQYDVR0OBBYEFI1V
hRQeacLkR4OekokkQq0dFDAHMIHnBgNVHSMEgd8wgdyAFI1VhRQeacLkR4Oekokk
Qq0dFDAHoYHApIG9MIG6MQswCQYDVQQGEwJMVDEQMA4GA1UECBMHVmlsbml1czEQ
MA4GA1UEBxMHVmlsbml1czEeMBwGA1UEChMVVUFCIEVWUCBJbnRlcm5hdGlvbmFs
MS0wKwYDVQQLEyRodHRwOi8vd3d3Lm1va2VqaW1haS5sdC9iYW5rbGluay5waHAx
GTAXBgNVBAMTEHd3dy5tb2tlamltYWkubHQxHTAbBgkqhkiG9w0BCQEWDnBhZ2Fs
YmFAZXZwLmx0ggEAMAwGA1UdEwQFMAMBAf8wDQYJKoZIhvcNAQEFBQADgYEAwIZw
Rb2E//fmXrcO2hnUYaG9spg1xCvRVrlfasLRURzcwwyUpJian7+HTdTNhrMa0rHp
NlS0iC8hx1Xfltql//lc7EoyyIRXrom4mijCFUHmAMvR5AmnBvEYAUYkLnd/QFm5
/utEm5JsVM8LidCtXUppCehy1bqp/uwtD4b4F3c=
-----END CERTIFICATE-----
-----BEGIN CERTIFICATE REQUEST-----
MIIB+zCCAWQCAQAwgboxCzAJBgNVBAYTAkxUMRAwDgYDVQQIEwdWaWxuaXVzMRAw
DgYDVQQHEwdWaWxuaXVzMR4wHAYDVQQKExVVQUIgRVZQIEludGVybmF0aW9uYWwx
LTArBgNVBAsTJGh0dHA6Ly93d3cubW9rZWppbWFpLmx0L2JhbmtsaW5rLnBocDEZ
MBcGA1UEAxMQd3d3Lm1va2VqaW1haS5sdDEdMBsGCSqGSIb3DQEJARYOcGFnYWxi
YUBldnAubHQwgZ8wDQYJKoZIhvcNAQEBBQADgY0AMIGJAoGBAN5PbdX+Q21/+Gs1
p79mwt9Fl3wT6izodn0JuC8H5frn2QEMGrm+MwMJWRjqyJyfV9wV+6i0RxuEpIoO
sMBD4OYIyb3oLsDiCoILk6qYg1q7FgN1uJ7tX0YladtFcOz/ky7vbZ/lO45QbceE
3+9ODy4LEisYhi/2J2G9NsPKJ5ULAgMBAAGgADANBgkqhkiG9w0BAQUFAAOBgQAr
GZJzT9Tzvo6t6/mOHr4NsdyVopQm0Ym0mwcrs+4qC4yfz0kj7STjcUnPlz1OP+Vp
aPoe4aREKf58SAZGfZqeiYhl2IL7i3PoeN/DThSwcFcb3YFpMG9EkRDfC/c2H0x7
GFYXlI9ODyfBPa02o44sQdqmdhCQCqvS5/5vhflJ9A==
-----END CERTIFICATE REQUEST-----
'''

PAYSERA_CERT = x509.load_pem_x509_certificate(
    PAYSERA_CERT_PEM,
    default_backend(),
)
PAYSERA_PUBLIC_KEY = PAYSERA_CERT.public_key()

# Payment has not been executed.
# According to Paysera, this status means that the order can be dismissed.
PAYSERA_STATUS_NOT_EXECUTED = '0'

# Payment was successful.
PAYSERA_STATUS_PAYMENT_SUCCESSFULL = '1'

# Payment order accepted, but not yet executed.
PAYSERA_STATUS_PAYMENT_ACCEPTED = '2'

# Additional payment information,
# This is typically additional information about the bank account
# number or about personal code, if such request was made.
# We do not store this information, so we ignore this type of request.
PAYSERA_STATUS_ADDITIONAL_INFO = '3'

def _maybe_encode(value, encoding='ascii'):
    if isinstance(value, unicode):
        return value.encode(encoding)
    return value


def _encode_dict_vals(old_dict):
    '''Encodes Unicode values in the dict using UTF-8.'''
    return {
        _maybe_encode(k, 'utf-8'): _maybe_encode(v, 'utf-8')
        for k, v in old_dict.items()
    }


def md5_sign(data, sign_password):
    '''Returns the MD5 hash of (data + paysera_sign_password).'''
    value = ''.join(map(_maybe_encode, (data, sign_password)))
    return hashlib.md5(value).hexdigest()


def verify_rsa_signature(signature, data):
    '''
    Verify the data's RSA signature (ss2).

    :param signature: base64 encoded signature
    :param data: data of which the signature is verified
    :rtype: bool
    '''
    signature = base64.b64decode(_maybe_encode(signature), altchars='-_')
    valid = True
    try:
        PAYSERA_PUBLIC_KEY.verify(
            signature,
            _maybe_encode(data),
            PKCS1v15(),
            hashes.SHA1(),
        )
    except exceptions.InvalidSignature:
        valid = False
    return valid


def get_form_values(value_dict, sign_password):
    # urlencode needs bytes
    encoded_params = _encode_dict_vals(value_dict)

    # Concatenate the parameters into a single line and b64encode it.
    data = base64.b64encode(urllib.urlencode(encoded_params), altchars='-_')
    signature = md5_sign(data, sign_password)
    return {
        'data': data,
        'signature': signature,
    }
