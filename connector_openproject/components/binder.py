# -*- coding: utf-8 -*-
# Copyright 2017-2018 Naglis Jonaitis
# License AGPL-3 or later (https://www.gnu.org/licenses/agpl).

import collections
import urlparse

from odoo.addons.component.core import AbstractComponent, Component


class OpenProjectBaseBinder(AbstractComponent):
    _name = 'base.openproject.binder'
    _inherit = [
        'base.binder',
        'base.openproject.connector',
    ]
    _external_field = 'openproject_id'
    _usage = 'binder'

    # Used for building the URL of record on the OpenProject instance.
    _external_url_fmt = None

    def get_external_url(self, external_id):
        if not self._external_url_fmt:
            return None
        if isinstance(external_id, collections.Mapping):
            external_id = external_id['id']
        path = self._external_url_fmt.format(id=external_id)
        return urlparse.urljoin(self.backend_record.instance_url, path)


class OpenProjectBinder(Component):
    _name = 'openproject.binder'
    _inherit = 'base.openproject.binder'
    _apply_on = [
        'openproject.mail.message',
        'openproject.project.task.type',
    ]


class OpenProjectResUsersBinder(Component):
    _name = 'openproject.res.users.binder'
    _inherit = 'base.openproject.binder'
    _apply_on = 'openproject.res.users'
    _external_url_fmt = '/users/{id}'


class OpenProjectProjectProjectBinder(Component):
    _name = 'openproject.project.project.binder'
    _inherit = 'base.openproject.binder'
    _apply_on = 'openproject.project.project'
    _external_url_fmt = '/projects/{id}'


class OpenProjectProjectTaskBinder(Component):
    _name = 'openproject.project.task.binder'
    _inherit = 'base.openproject.binder'
    _apply_on = 'openproject.project.task'
    _external_url_fmt = '/work_packages/{id}'


class OpenProjectAccountAnalyticLineBinder(Component):
    _name = 'openproject.account.analytic.line.binder'
    _inherit = 'base.openproject.binder'
    _apply_on = 'openproject.account.analytic.line'
    _external_url_fmt = '/time_entries/{id}/edit'
