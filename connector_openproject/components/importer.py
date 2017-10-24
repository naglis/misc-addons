# -*- coding: utf-8 -*-
# Copyright 2017 Naglis Jonaitis
# License AGPL-3 or later (https://www.gnu.org/licenses/agpl).

import base64
import cStringIO
import logging

import PIL
import requests

from odoo import _, fields
from odoo.addons.component.core import AbstractComponent, Component
from odoo.addons.connector.exception import (
    IDMissingInBackend,
    NetworkRetryableError,
)

from ..utils import job_func, parse_openproject_link_relation
from ..const import (
    OP_ASSIGNEE_LINK,
    OP_PROJECT_LINK,
    OP_STATUS_LINK,
    OP_USER_LINK,
    OP_WORK_PACKAGE_LINK,
    USER_AGENT,
)

_logger = logging.getLogger(__name__)

try:
    import isodate
except ImportError:
    _logger.info('Missing dependency: isodate')


class OpenProjectImporter(Component):
    _name = 'base.openproject.importer'
    _inherit = [
        'base.importer',
        'base.openproject.connector',
    ]
    _apply_on = [
        'openproject.project.project',
        'openproject.project.task.type',
    ]
    _usage = 'record.importer'

    def _get_extra_context(self):
        '''Returns extra context to be used on create()/write().'''
        return {}

    def import_dependencies(self, record):
        pass

    @staticmethod
    def is_uptodate(record, binding):
        """
        Check if a record needs to be updated based on 'updatedAt' field
        from OpenProject and 'sync_date'.
        """
        last_update = record.get('updatedAt')
        if not (last_update and binding and binding.sync_date):
            return False

        sync_date = fields.Datetime.from_string(binding.sync_date)
        openproject_date = isodate.parse_datetime(last_update).replace(
            tzinfo=None)
        return sync_date > openproject_date

    def _after_import(self, binding, record, for_create=False):
        pass

    def _link_to_internal(self, record, link):
        links = record.get('_links', {})
        external_id = parse_openproject_link_relation(
            links.get(link.key, {}), link.endpoint)
        binder = self.binder_for(link.model)
        if external_id:
            return external_id, binder.to_internal(external_id)
        return None, binder.model.browse()

    def _import_link_dependency(self, record, link, force=False,
                                raise_null=True):
        _logger.debug(
            'Importing OpenProject link "%s" dependency for binding model: %s',
            link.key, link.model)
        external_id, binding = self._link_to_internal(record, link)
        if external_id:
            if not binding or force:
                self._import_dependency(external_id, link.model)
        elif raise_null:
            raise ValueError('Missing OpenProject link "%s" ID' % link.key)

    def _import_dependency(self, external_id, binding_model, force=False):
        record = self.component(
            usage='backend.adapter',
            model_name=binding_model).get_single(external_id)
        self.component(
            usage='record.importer', model_name=binding_model).run(record)

    def get_record(self, external_id):
        return self.backend_adapter.get_single(external_id)

    def run(self, data, force=False, **kwargs):
        if isinstance(data, basestring):
            external_id = data
            try:
                record = self.get_record(external_id)
            except IDMissingInBackend:
                return _('Record no longer exists on OpenProject')
        else:
            record, external_id = data, data['id']

        lock_name = 'import({}, {}, {}, {})'.format(
            self.backend_record._name,
            self.backend_record.id,
            self.work.model_name,
            external_id,
        )

        binding = self.binder.to_internal(external_id)
        exists = bool(binding)

        if not force and self.is_uptodate(record, binding):
            _logger.debug(
                'Skipping: %s with external ID: %s - up-to-date',
                self.work.model_name, external_id)
            return _('Record is already up-to-date.')

        self.advisory_lock_or_retry(lock_name)

        self.import_dependencies(record)
        values = self.mapper.map_record(record).values(for_create=not exists)
        context = self._get_extra_context()
        if exists:
            binding.with_context(**context).write(values)
        else:
            binding = self.model.with_context(**context).create(values)

        self.binder.bind(external_id, binding)

        self._after_import(binding, record, for_create=not exists)


class BatchImporter(AbstractComponent):
    _name = 'openproject.batch.importer'
    _inherit = [
        'base.importer',
        'base.openproject.connector',
    ]
    _usage = 'batch.importer'

    @property
    def page_size(self):
        return self.backend_record.page_size

    def get_records(self, filters, offset=None):
        return self.backend_adapter.get_collection(
            filters=filters, page_size=self.page_size, offset=offset)

    def run(self, filters=None, offset=None, job_options=None):
        records = self.get_records(filters=filters or [], offset=offset)
        for record in records:
            self._import_record(record, job_options=job_options)

    def _import_record(self, record, job_options=None):
        raise NotImplementedError()


class DelayedBatchImporter(Component):
    _name = 'openproject.delayed.batch.importer'
    _inherit = 'openproject.batch.importer'
    _apply_on = [
        'openproject.project.project',
        'openproject.project.task',
        'openproject.account.analytic.line',
    ]

    def _import_record(self, record, job_options=None):
        job_func(
            self.model,
            'import_record',
            **(job_options or {}))(self.backend_record, record)


class DelayedOpenProjectMailMessageBatchImporter(Component):
    _name = 'openproject.delayed.mail.message.batch.importer'
    _inherit = [
        'base.importer',
        'base.openproject.connector',
    ]
    _usage = 'batch.importer'
    _apply_on = 'openproject.mail.message'

    def run(self, wp_id, job_options=None):
        for record in self.get_records(wp_id):
            self._import_record(record, job_options=job_options)

    def get_records(self, wp_id, offset=None):
        return self.backend_adapter.get_work_package_activties(
            wp_id, offset=offset)

    def _import_record(self, record, job_options=None):
        job_func(
            self.model,
            'import_record',
            **(job_options or {}))(self.backend_record, record)


class OpenProjectUserImporter(Component):
    _name = 'openproject.user.importer'
    _inherit = 'base.openproject.importer'
    _apply_on = 'openproject.res.users'

    def _get_extra_context(self):
        # Don't send password reset emails during user creation.
        return {
            'no_reset_password': True,
        }

    def _after_import(self, binding, record, for_create=False):
        avatar_url = record.get('avatar')
        if for_create and avatar_url:
            job_func(
                self.model,
                'import_avatar',
                delay=True)(self.backend_record, avatar_url, binding.id)


class OpenProjectTaskImporter(Component):
    _name = 'openproject.task.importer'
    _inherit = 'base.openproject.importer'
    _apply_on = 'openproject.project.task'

    def _get_extra_context(self):
        # Disable mail sending, automatic author subscription, field tracking.
        return {
            'mail_auto_subscribe_no_notify': True,
            'mail_create_nosubscribe': True,
            'mail_create_nolog': True,
            'mail_track_log_only': True,
            'mail_notrack': True,
            'tracking_disable': True,
        }

    def import_dependencies(self, record):
        self._import_link_dependency(record, OP_PROJECT_LINK)
        self._import_link_dependency(
            record, OP_ASSIGNEE_LINK, raise_null=False)
        self._import_link_dependency(record, OP_STATUS_LINK)

    def _after_import(self, binding, record, for_create=False):
        project_id_, project = self._link_to_internal(record, OP_PROJECT_LINK)
        if project.sync_activities == 'all':
            # Import work package activities in bulk (don't split into separate
            # jobs).
            self.component(
                model_name='openproject.mail.message',
                usage='batch.importer').run(
                    binding.openproject_id, job_options={'delay': False})


class OpenProjectAccountAnalyticLineImporter(Component):
    _name = 'openproject.account.analytic.line.importer'
    _inherit = 'base.openproject.importer'
    _apply_on = 'openproject.account.analytic.line'

    def import_dependencies(self, record):
        self._import_link_dependency(
            record, OP_WORK_PACKAGE_LINK, raise_null=False)
        self._import_link_dependency(record, OP_USER_LINK)


class OpenProjectMailMessageImporter(Component):
    _name = 'openproject.mail.message.importer'
    _inherit = 'base.openproject.importer'
    _apply_on = 'openproject.mail.message'

    def import_dependencies(self, record):
        self._import_link_dependency(record, OP_WORK_PACKAGE_LINK)
        self._import_link_dependency(record, OP_USER_LINK)


class ImageImporter(AbstractComponent):
    _name = 'base.image.importer'
    _inherit = [
        'base.importer',
    ]
    _usage = 'image.importer'

    def _download_image(self, url, timeout=None):
        headers = {
            'User-Agent': USER_AGENT,
        }

        try:
            response = requests.get(url, headers=headers, timeout=timeout)
        except requests.exceptions.Timeout:
            raise NetworkRetryableError('Timeout while downloading image')
        return response.content if response.ok else None

    def run(self, url, binding_model, record_id, image_field, timeout=None):
        image = self._download_image(url, timeout=timeout)
        if not image:
            return _(u'No image could be downloaded')

        buf = cStringIO.StringIO(image)
        try:
            PIL.Image.open(buf).verify()
        except Exception:
            return _(u'Not a valid image: %s' % url)

        binding = self.env[binding_model].browse(record_id)
        binding.write({
            image_field: base64.b64encode(image),
        })
        return _('Image set on record: %s' % binding)


class OpenProjectImageImporter(Component):
    _name = 'openproject.image.importer'
    _inherit = [
        'base.image.importer',
        'base.openproject.connector',
    ]
    _apply_on = [
        'openproject.res.users',
    ]
