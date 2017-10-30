# -*- coding: utf-8 -*-
# Copyright 2017 Naglis Jonaitis
# License AGPL-3 or later (https://www.gnu.org/licenses/agpl).

import logging

from odoo import _
from odoo.addons.component.core import AbstractComponent, Component
from odoo.addons.connector.components.mapper import (
    mapping,
    only_create,
)

from ..const import (
    OP_ASSIGNEE_LINK,
    OP_PROJECT_LINK,
    OP_STATUS_LINK,
    OP_USER_LINK,
    OP_WORK_PACKAGE_LINK,
)
from ..utils import parse_openproject_link_relation, slugify

_logger = logging.getLogger(__name__)

try:
    import isodate
except ImportError:
    _logger.info('Missing dependency: isodate')


def openproject_text(field, fmt='html'):
    if fmt not in ('html', 'raw'):
        raise ValueError('Unknown OpenProject text format: "%s"' % fmt)

    def modifier(self, record, to_attr):
        text_field = record[field]
        if fmt not in text_field:
            raise KeyError(
                'Expected format: "%s" not present for field: "%s"' % (
                    fmt, field))
        return text_field[fmt]
    return modifier


def openproject_duration(field, raise_err=False, allow_none=True):

    def modifier(self, record, to_attr):
        value = record[field]
        if value is None:
            if allow_none:
                return 0.0
            else:
                raise ValueError(
                    'Missing OpenProject duration value for mapping '
                    '"%s" -> "%s"' % (field, to_attr))
        try:
            hours = isodate.parse_duration(value).total_seconds() / 3600.0
        except isodate.ISO8601Error:
            if raise_err:
                raise
            _logger.exception(
                u'Could not parse OpenProject duration: %s '
                u'(mapping: "%s" -> "%s")', value, field, to_attr)
            hours = 0.0
        return hours
    return modifier


def openproject_date(field, raise_err=False, allow_none=True):

    def modifier(self, record, to_attr):
        value = record.get(field)
        if value is None:
            if allow_none:
                return False
            else:
                raise ValueError(
                    'Missing OpenProject date value for mapping '
                    '"%s" -> "%s"' % (field, to_attr))
        try:
            date = isodate.parse_date(value)
        except isodate.ISO8601Error:
            if raise_err:
                raise
            _logger.exception(
                u'Could not parse OpenProject date: %s '
                u'(mapping: "%s" -> "%s")', value, field, to_attr)
            date = False
        return date
    return modifier


class BaseOpenProjectMapper(AbstractComponent):
    _name = 'base.openproject.mapper'
    _inherit = [
        'base.import.mapper',
        'base.openproject.connector',
    ]
    _usage = 'import.mapper'

    @mapping
    def openproject_id(self, record):
        return {
            'openproject_id': record['id'],
        }

    @mapping
    def backend_id(self, record):
        return {
            'backend_id': self.backend_record.id,
        }

    def _map_op_link(self, record, link, raise_missing=True, raise_null=True,
                     unwrap=True):
        links = record.get('_links', {})
        external_id = parse_openproject_link_relation(
            links.get(link.key, {}), link.endpoint)
        binder = self.component(usage='binder', model_name=link.model)
        if external_id:
            binding = binder.to_internal(external_id, unwrap=unwrap)
            if not binding and raise_missing:
                raise ValueError(
                    'Missing binding for OpenProject link "%s" with ID: %s' % (
                        link.key, external_id))
            else:
                return binding
        elif raise_null:
            raise ValueError('Missing OpenProject link "%s" ID' % link.key)
        else:
            return binder.model.odoo_id if unwrap else binder.model


class OpenProjectAgeMapper(AbstractComponent):
    _name = 'base.openproject.age.mapper'
    _inherit = [
        'base.import.mapper',
    ]
    _usage = 'import.mapper'

    @mapping
    @only_create
    def create_date(self, record):
        created_at = record.get('createdAt')
        if created_at:
            return {
                'op_create_date': isodate.parse_datetime(created_at),
            }

    @mapping
    def write_date(self, record):
        updated_at = record.get('updatedAt')
        if updated_at:
            return {
                'op_write_date': isodate.parse_datetime(updated_at),
            }


class OpenProjectUserMapper(Component):
    _name = 'openproject.user.mapper'
    _inherit = [
        'base.openproject.mapper',
        'base.openproject.age.mapper',
    ]
    _apply_on = [
        'openproject.res.users',
    ]

    @mapping
    def main(self, record):
        is_deleted = record.get('subtype') == 'DeletedUser'
        firstname, lastname = map(record.get, ('firstName', 'lastName'))
        if firstname and lastname:
            name = u' '.join((firstname, lastname))
        else:
            name = record.get('name')
        active = False if is_deleted else record.get('status') != 'locked'
        # The 'login' of a deleted user is empty.
        login = ('__op_deleted_user_%(id)s' % record
                 if is_deleted else record.get('login') or slugify(name))
        return {
            'active': active,
            'name': name,
            'login': login,
            'email': False if is_deleted else (
                record.get('email') or record.get('login')),
        }

    @mapping
    @only_create
    def defaults(self, record):
        categ = self.env.ref(
            'connector_openproject.res_partner_category_1',
            raise_if_not_found=False)
        return {
            'customer': False,
            'supplier': False,
            'notify_email': 'none',
            'opt_out': True,
            'category_id': [(4, categ.id)] if categ else False,
            'groups_id': [],
        }


class OpenProjectProjectMapper(Component):
    _name = 'openproject.project.mapper'
    _inherit = [
        'base.openproject.mapper',
        'base.openproject.age.mapper',
    ]
    _apply_on = [
        'openproject.project.project',
    ]
    direct = [
        ('name', 'name'),
    ]

    @mapping
    @only_create
    def defaults(self, record):
        return {
            'label_tasks': _('Work Packages'),
        }


class OpenProjectTaskMapper(Component):
    _name = 'openproject.task.mapper'
    _inherit = [
        'base.openproject.mapper',
        'base.openproject.age.mapper',
    ]
    _apply_on = [
        'openproject.project.task',
    ]
    direct = [
        ('subject', 'name'),
        (openproject_duration('estimatedTime'), 'planned_hours'),
        (openproject_date('startDate'), 'date_start'),
        (openproject_date('dueDate'), 'date_deadline'),
        # TODO(naglis): type -> tag_ids, priority?
    ]

    @mapping
    def description(self, record):
        project = self._map_op_link(record, OP_PROJECT_LINK, unwrap=False)
        return {
            'description': openproject_text('description')(
                self, record, 'description'),
        } if project.sync_wp_description else {}

    @mapping
    def links(self, record):
        return {
            'project_id': self._map_op_link(record, OP_PROJECT_LINK).id,
            'user_id': self._map_op_link(
                record, OP_ASSIGNEE_LINK, raise_null=False).id,
            'stage_id': self._map_op_link(record, OP_STATUS_LINK).id,
        }


class OpenProjectTaskTypeMapper(Component):
    _name = 'openproject.task.type.mapper'
    _inherit = 'base.openproject.mapper'
    _apply_on = [
        'openproject.project.task.type',
    ]
    direct = [
        ('name', 'name'),
        ('isClosed', 'fold'),
        ('position', 'sequence'),
    ]


class OpenProjectAccountAnalyticLineMapper(Component):
    _name = 'openproject.account.analytic.line.mapper'
    _inherit = [
        'base.openproject.mapper',
        'base.openproject.age.mapper',
    ]
    _apply_on = 'openproject.account.analytic.line'
    direct = [
        (
            openproject_date('spentOn', raise_err=True, allow_none=False),
            'date',
        ),
        (openproject_duration('hours'), 'unit_amount'),
    ]

    @mapping
    def comment(self, record):
        return {
            'name': record.get('comment') or u'/',
        }

    @mapping
    def links(self, record):
        return {
            'user_id': self._map_op_link(record, OP_USER_LINK).id,
            'project_id': self._map_op_link(record, OP_PROJECT_LINK).id,
            'task_id': self._map_op_link(
                record, OP_WORK_PACKAGE_LINK, raise_null=False).id,
        }


class OpenProjectMailMessageMapper(Component):
    _name = 'openproject.mail.message.mapper'
    _inherit = [
        'base.openproject.mapper',
        'base.openproject.age.mapper',
    ]
    _apply_on = 'openproject.mail.message'

    @mapping
    @only_create
    def main(self, record):
        activity_type = record['_type']
        if activity_type == 'Activity':
            body = '<br/>'.join(d['raw'] for d in record.get('details', []))
            subtype_xml_id = 'mail_message_subtype_wp_update'
        else:
            body = openproject_text('comment')(self, record, 'body')
            subtype_xml_id = 'mail_message_subtype_wp_comment'
        subtype = self.env.ref(
            'connector_openproject.%s' % subtype_xml_id,
            raise_if_not_found=False)
        return {
            'body': body,
            'message_type': 'comment',
            'model': 'project.task',
            'author_id': self._map_op_link(record, OP_USER_LINK).partner_id.id,
            'res_id': self._map_op_link(record, OP_WORK_PACKAGE_LINK).id,
            'subtype_id': subtype.id if subtype else False,
        }
