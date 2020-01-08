# Copyright 2019 Naglis Jonaitis
# License AGPL-3 or later (https://www.gnu.org/licenses/agpl).

import base64
import urllib.parse


def make_full_url_getter(env):
    base_url = env['ir.config_parameter'].sudo().get_param('web.base.url')

    def getter(path):
        return urllib.parse.urljoin(base_url, path)

    return getter


def decode_form_data(encoded_data):
    '''
    Decodes base64 encoded string, parses it and returns a dict of parameters

    :param encoded_data: base64 encoded URL parameters list
    :type encoded_data: str
    :rtype: dict
    '''
    decoded = base64.urlsafe_b64decode(encoded_data)
    return dict(urllib.parse.parse_qsl(decoded.decode('utf-8'), keep_blank_values=True))
