# -*- coding: utf-8 -*-
# Copyright 2017 Naglis Jonaitis
# License AGPL-3 or later (https://www.gnu.org/licenses/agpl).


class OpenProjectAPIError(Exception):
    """Base exception for errors received from the OpenProject API."""


class OpenProjectAPIPermissionError(OpenProjectAPIError):
    """
    Exception which is raised in case of insufficient permissions for the
    OpenProject sync user.
    """
