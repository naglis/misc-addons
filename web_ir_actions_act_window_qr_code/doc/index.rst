=====================
QR Code Window Action
=====================

Installation
------------

This module can be installed as any other regular Odoo addon.

Usage
-----

#. Add this module to your module's dependencies (*depends* key in module's
   manifest).
#. Return the QR code action from your Python code:

    .. code-block:: python

        return {
            # This is the name of the pop-up dialog window.
            'name': _('QR Code'),
            'type': 'ir.actions.act_window.qr_code',
            # A help text displayed above the QR code.
            'help_text': 'Scan the below QR code using your mobile phone.',
            # Data to be encoded in the QR code
            'data': 'https://naglis.me/',
            'flags': {
                # If true, an additional 'Open Link' button is displayed to open
                # the link in a new window.
                'is_url': False,
                # If true, hide the collapsible text area with the value of the QR
                # code.
                'hide_value': False,
            },
        }
