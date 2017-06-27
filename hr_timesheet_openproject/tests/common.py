# -*- coding: utf-8 -*-
# Copyright 2017 Naglis Jonaitis
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import io

from .. import utils

HEADER_LINE = u','.join(utils.TIME_ENTRY_KEYS)


def line_from_dict(d):
    return u','.join(d.get(k, u'') for k in utils.TIME_ENTRY_KEYS)


def build_csv(lines):
    return u'\n'.join([HEADER_LINE] + map(line_from_dict, lines))


def build_csv_io(lines, encoding='utf-8'):
    return io.BytesIO(build_csv(lines).encode(encoding))
