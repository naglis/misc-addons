==================
Update Module List
==================

Update module list from the command line.

Installation
============

This module does not have to be installed in a database in order to use it.
Simply putting it inside one of your Odoo addon paths is enough.

Usage
=====

In your server, logged in as the Odoo user, run::

    <path_to_odoo>/odoo-bin --addons-path=/foo/path1,/bar/path2 uml <db_name>

This will update the module list in database `<db_name>`.

.. note:: The equality sign (=) after the *--addons-path* is important
  (required). Also, no other Odoo command line arguments should be passed.
