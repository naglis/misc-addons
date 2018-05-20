==============
Defuse XML-RPC
==============

Installation
------------

Before installing the addon, make sure the *defusedxml* Python package is
installed in your system. You can install it by running:

.. code-block:: bash

    pip install defusedxml

You can read more about installing Python packages `here`_.

After that, this addon can be installed as any other regular Odoo addon:

- Unzip the addon in one of Odoo's addons paths.
- Login to Odoo as a user with administrative privileges, go into debug mode.
- Go to *Apps -> Update Apps List*, click *Update* in the dialog window.
- Go to *Apps -> Apps*, remove the *Apps* filter in the search bar and search
  for *Defuse XML-RPC*. Click *Install* button on the addon.

Configuration
-------------

If you run into problems with large XML-RPC request/response bodies, you may
increase the maximum size of the request/response body via Odoo configuration
file. Simply set the *defused_xml_max_data* configuration option to something
larger than 47185920, which is the default (equal to 45 MB). Odoo server
process must be restarted after changing the value in order for the new
configuration to take effect.

Uninstallation
--------------

- Login to Odoo as a user with administrative privileges, go into debug mode.
- Go to *Apps -> Apps*, remove the *Apps* filter in the search bar and search
  for *Defuse XML-RPC*.
- Click on the addon, then click the *Uninstall* button.

.. note:: After uninstalling the addon the Odoo server process needs to be
  restarted in order for the module to be completely uninstalled.

.. _here: https://packaging.python.org/tutorials/installing-packages/
