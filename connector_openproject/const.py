# -*- coding: utf-8 -*-
# Copyright 2017-2018 Naglis Jonaitis
# License AGPL-3 or later (https://www.gnu.org/licenses/agpl).

import collections
import datetime

from odoo import release

OpenProjectLink = collections.namedtuple(
    'OpenProjectLink', ['key', 'endpoint', 'model'])

OP_ASSIGNEE_LINK = OpenProjectLink(
    key='assignee', endpoint='users', model='openproject.res.users')
OP_PROJECT_LINK = OpenProjectLink(
    key='project', endpoint='projects', model='openproject.project.project')
OP_STATUS_LINK = OpenProjectLink(
    key='status', endpoint='statuses', model='openproject.project.task.type')
OP_USER_LINK = OpenProjectLink(
    key='user', endpoint='users', model='openproject.res.users')
OP_WORK_PACKAGE_LINK = OpenProjectLink(
    key='workPackage', endpoint='work_packages',
    model='openproject.project.task')

IMPORT_DELTA_BUFFER = datetime.timedelta(seconds=30)

USER_AGENT = '{r.product_name}/{r.series}'.format(r=release)

(
    PRIORITY_USER,
    PRIORITY_PROJECT,
    PRIORITY_STATUS,
    PRIORITY_WORK_PACKAGE,
    PRIORITY_ACTIVITY,
    PRIORITY_TIME_ENTRY,
) = (p * 50 for p in range(1, 7))
DEFAULT_PRIORITY = 100

DEFAULT_PAGE_SIZE = 100

DEFAULT_TIMEOUT = 30

ACTIVITY_SYNC_NONE = 'none'
ACTIVITY_SYNC_COMMENTS = 'comments'
ACTIVITY_SYNC_UPDATES = 'updates'
ACTIVITY_SYNC_ALL = 'all'

OP_USER_STATUS_ACTIVE = 'active'
OP_USER_STATUS_REGISTERED = 'registered'
OP_USER_STATUS_LOCKED = 'locked'
OP_USER_STATUS_INVITED = 'invited'
