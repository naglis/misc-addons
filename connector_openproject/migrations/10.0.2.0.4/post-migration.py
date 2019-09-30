# -*- coding: utf-8 -*-
# Copyright 2019 Naglis Jonaitis
# License AGPL-3 or later (https://www.gnu.org/licenses/agpl).

import json
import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)
KEYS = [u'format', u'html', u'raw']


def mark_analytic_entries_as_not_synced(env):
    model = env['openproject.account.analytic.line']
    to_update = model.browse()
    for line in model.search([
        ('name', '=like', '{%}'),
    ]):
        try:
            desc = json.loads(line.name)
        except ValueError:
            pass
        else:
            if sorted(desc) == KEYS:
                to_update |= line

    if to_update:
        _logger.info(
            'Clearing `sync_date` for %d "%s" model records with IDs: %s',
            len(to_update),
            model._name,
            to_update.ids,
        )
        to_update.write({
            'sync_date': False,
        })


def migrate(cr, version):
    if not version:
        return
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        mark_analytic_entries_as_not_synced(env)
