# -*- coding: utf-8 -*-
# Copyright 2019 Naglis Jonaitis
# License AGPL-3 or later (https://www.gnu.org/licenses/agpl).

import base64
import urlparse


def make_full_url_getter(env):
    base_url = env['ir.config_parameter'].sudo().get_param('web.base.url')

    def getter(path):
        return urlparse.urljoin(base_url, path)

    return getter


def decode_form_data(encoded_data):
    '''
    Decodes base64 encoded string, parses it and returns a dict of parameters

    :param encoded_data: base64 encoded URL parameters list
    :type encoded_data: str
    :rtype: dict
    '''
    decoded = base64.urlsafe_b64decode(encoded_data.encode('ascii'))
    parsed = urlparse.parse_qsl(decoded, keep_blank_values=True)
    return {k: v.decode('utf-8') for k, v in parsed}
