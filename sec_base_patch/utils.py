# Copyright 2018 Naglis Jonaitis
# License AGPL-3 or later (https://www.gnu.org/licenses/agpl).

import logging
import threading

_logger = logging.getLogger(__name__)
_patch_lock = threading.RLock()


def is_patched(func, func_name):
    return getattr(func, '%s_patched' % func_name, False)


def patch_func(module, func_name, new_func):
    _logger.debug('Patching function: %s', func_name)
    with _patch_lock:
        original_func = getattr(module, func_name)

        # Don't patch the function repeatedly, eg. on module update.
        if is_patched(original_func, func_name):
            _logger.debug('Function "%s" already patched', func_name)
            return False

        # Store the original function in case we want to restore it later.
        new_func.original_func = original_func

        setattr(module, func_name, new_func)

        # Mark the function as patched.
        setattr(new_func, '%s_patched' % func_name, True)

        return True


def unpatch_func(module, func_name):
    _logger.debug('Unpatching function: %s', func_name)
    with _patch_lock:
        func = getattr(module, func_name)
        original_func = getattr(func, 'original_func', None)

        # Bail out if the function was not patched.
        if not is_patched(func, func_name) or original_func is None:
            return False

        # Restore the original function.
        setattr(module, func_name, original_func)

        return True
