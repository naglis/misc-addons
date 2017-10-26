# -*- coding: utf-8 -*-
# Copyright 2017 Naglis Jonaitis
# License AGPL-3 or later (https://www.gnu.org/licenses/agpl).

import contextlib
import datetime
import itertools
import re
import string

from odoo import fields

from .const import (
    ACTIVITY_SYNC_NONE,
    ACTIVITY_SYNC_COMMENTS,
    ACTIVITY_SYNC_ALL,
    DEFAULT_PRIORITY,
    IMPORT_DELTA_BUFFER,
    PRIORITY_ACTIVITY,
    PRIORITY_PROJECT,
    PRIORITY_STATUS,
    PRIORITY_TIME_ENTRY,
    PRIORITY_USER,
    PRIORITY_WORK_PACKAGE,
)


ALPHANUMERIC = frozenset(string.ascii_letters + string.digits)
PRIORITY_MAP = {
    'openproject.res.users': PRIORITY_USER,
    'openproject.project.project': PRIORITY_PROJECT,
    'openproject.project.task.type': PRIORITY_STATUS,
    'openproject.project.task': PRIORITY_WORK_PACKAGE,
    'openproject.mail.message': PRIORITY_ACTIVITY,
    'openproject.account.analytic.line': PRIORITY_TIME_ENTRY,
}


def parse_openproject_link_relation(link, endpoint):
    pattern = re.compile(r'^(?x)/api/v\d/%s/(?P<id>\d+)$' % endpoint)
    match = pattern.match(link.get('href') or '')
    return None if match is None else match.group('id')


def slugify(s, replacement='_'):
    r, prev = [], None
    for c in s:
        if c in ALPHANUMERIC:
            r.append(c)
            prev = c
        else:
            if prev == replacement:
                continue
            r.append(replacement)
            prev = replacement

    return ''.join(r).strip(replacement).lower()


def job_func(rec, func_name, delay=True, **kwargs):
    job_options = {
        'priority': PRIORITY_MAP.get(rec._name, DEFAULT_PRIORITY),
    }
    job_options.update(kwargs)
    if delay:
        return getattr(rec.with_delay(**job_options), func_name)
    return getattr(rec, func_name)


def paginate(page_size, total):
    return itertools.takewhile(
        lambda o: (o - 1) * page_size < total, itertools.count(start=1))


@contextlib.contextmanager
def last_update(record, field, delta=IMPORT_DELTA_BUFFER, force=False):
    now = datetime.datetime.now()
    last_update_date = record[field]
    if not last_update_date or force:
        yield None
    else:
        yield fields.Datetime.from_string(last_update_date)
    record.write({
        field: now - delta,
    })


def op_filter(name, operator, *values):
    return {
        name: {
            'operator': operator,
            'values': values,
        },
    }


def should_skip_activity(activity_type, enabled_for):
    if enabled_for == ACTIVITY_SYNC_NONE:
        return True
    elif enabled_for == ACTIVITY_SYNC_ALL:
        return False
    elif enabled_for == ACTIVITY_SYNC_COMMENTS:
        return not activity_type == 'Activity::Comment'
    else:
        return not activity_type == 'Activity'
