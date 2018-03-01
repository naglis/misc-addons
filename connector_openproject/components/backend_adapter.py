# -*- coding: utf-8 -*-
# Copyright 2017 Naglis Jonaitis
# License AGPL-3 or later (https://www.gnu.org/licenses/agpl).

import collections
import json
import logging
import urlparse

import requests

from odoo.addons.component.core import AbstractComponent, Component
from odoo.addons.connector.exception import NetworkRetryableError

from ..const import USER_AGENT
from ..exceptions import (
    OpenProjectAPIError,
    OpenProjectAPIPermissionError,
)

_logger = logging.getLogger(__name__)


def pretty_print_request(req):
    return '{req.method} {req.url}\n{headers}\n\n{body}'.format(
        req=req,
        headers='\n'.join(
            '{}: {}'.format(k, v) for k, v in req.headers.iteritems()),
        body=req.body or '',
    )


def pretty_print_response(response):
    body = json.dumps(json.loads(response.content), indent=2)
    return '{resp.url}\n{headers}\n\n{body}'.format(
        resp=response,
        headers='\n'.join(
            '{}: {}'.format(k, v) for k, v in response.headers.iteritems()),
        body=body,
    )


def unwrap_elements(data):
    return data.get('_embedded', {}).get('elements', [])


class BaseOpenProjectAdapter(AbstractComponent):
    _name = 'base.openproject.adapter'
    _inherit = [
        'base.backend.adapter',
        'base.openproject.connector',
    ]
    _usage = 'backend.adapter'
    _single_endpoint = None
    _collection_endpoint = None
    _paginated_collection = True

    # Used for building the URL of record on the OpenProject instance.
    _external_url_fmt = None

    # Version of OpenProject API.
    API_VERSION = 'v3'

    def __init__(self, *a, **kw):
        super(BaseOpenProjectAdapter, self).__init__(*a, **kw)
        self.session = requests.Session()

    def get_external_url(self, external_id):
        if self._external_url_fmt is None:
            return None
        if isinstance(external_id, collections.Mapping):
            external_id = external_id['id']
        path = self._external_url_fmt.format(id=external_id)
        return urlparse.urljoin(self.backend_record.instance_url, path)

    @property
    def paginated(self):
        return self._paginated_collection

    @property
    def api_url(self):
        instance_url = self.collection.instance_url
        if instance_url.endswith('/'):
            instance_url = instance_url.rstrip('/')
        return instance_url + '/api/%s' % self.API_VERSION

    @property
    def api_key(self):
        return self.collection.api_key

    @property
    def timeout(self):
        return self.collection.timeout or None

    @property
    def page_size(self):
        return self.collection.page_size

    @property
    def debug(self):
        return self.collection.debug

    def _raise_for_error(self, response):
        error_map = {
            'urn:openproject-org:api:v3:errors:MissingPermission': (
                OpenProjectAPIPermissionError
            ),
        }
        data = response.json()
        if data.get('_type') == 'Error':
            raise error_map.get(
                data.get('errorIdentifier'),
                OpenProjectAPIError,
            )(data.get('message') or 'Unknown OpenProject API error')

    def get_total(self, filters=None):
        data = self._request(
            'GET', self._collection_endpoint, filters=filters, page_size=1)
        return data['total']

    def _request(self, method, url, headers=None, filters=None, page_size=None,
                 offset=None):
        endpoint_url = '%s%s' % (self.api_url, url)
        request_headers = {
            'User-Agent': USER_AGENT,
        }
        if headers:
            request_headers.update(headers)

        request_params = collections.OrderedDict()
        if page_size:
            request_params.update(pageSize=page_size)
        if offset:
            request_params.update(offset=offset)
        if filters:
            request_params.update(filters=json.dumps(filters))

        request = requests.Request(
            method,
            endpoint_url,
            params=request_params,
            headers=request_headers,
            auth=requests.auth.HTTPBasicAuth('apikey', self.api_key),
        )
        prepared_request = self.session.prepare_request(request)
        if self.debug:
            _logger.info(pretty_print_request(prepared_request))

        try:
            response = self.session.send(
                prepared_request, timeout=self.timeout)
        except requests.exceptions.Timeout:
            raise NetworkRetryableError(
                'Timeout during request to OpenProject')

        if self.debug:
            _logger.info(pretty_print_response(response))
        self._raise_for_error(response)
        return response.json()

    def get_single(self, element_id, **kw):
        return self._request(
            'GET', self._single_endpoint.format(id=element_id), **kw)

    def get_collection(self, filters=None, page_size=None, offset=None):
        return unwrap_elements(self._request(
            'GET', self._collection_endpoint, filters=filters,
            page_size=page_size, offset=offset))


class OpenProjectResUsersAdapter(Component):
    _name = 'openproject.res.users.adapter'
    _inherit = 'base.openproject.adapter'
    _apply_on = 'openproject.res.users'
    _single_endpoint = '/users/{id}'
    _collection_endpoint = '/users'
    _external_url_fmt = _single_endpoint


class OpenProjectProjectProjectAdapter(Component):
    _name = 'openproject.project.project.adapter'
    _inherit = 'base.openproject.adapter'
    _apply_on = 'openproject.project.project'
    _single_endpoint = '/projects/{id}'
    _collection_endpoint = '/projects'
    _external_url_fmt = _single_endpoint



class OpenProjectProjectTaskTypeAdapter(Component):
    _name = 'openproject.project.task.type.adapter'
    _inherit = 'base.openproject.adapter'
    _apply_on = 'openproject.project.task.type'
    _single_endpoint = '/statuses/{id}'
    _collection_endpoint = '/statuses'


class OpenProjectProjectTaskAdapter(Component):
    _name = 'openproject.project.task.adapter'
    _inherit = 'base.openproject.adapter'
    _apply_on = 'openproject.project.task'
    _single_endpoint = '/work_packages/{id}'
    _collection_endpoint = '/work_packages'
    _external_url_fmt = _single_endpoint


class OpenProjectMailMessageAdapter(Component):
    _name = 'openproject.mail.message.adapter'
    _inherit = 'base.openproject.adapter'
    _apply_on = 'openproject.mail.message'
    _single_endpoint = '/activities/{id}'
    _wp_collection_endpoint = '/work_packages/{wp_id}/activities'

    def get_work_package_activties(self, work_package_id, offset=None):
        return unwrap_elements(self._request(
            'GET', self._wp_collection_endpoint.format(wp_id=work_package_id),
            offset=offset))


class OpenProjectAccountAnalyticLineAdapter(Component):
    _name = 'openproject.account.analytic.line.adapter'
    _inherit = 'base.openproject.adapter'
    _apply_on = 'openproject.account.analytic.line'
    _single_endpoint = '/time_entries/{id}'
    _collection_endpoint = '/time_entries'
