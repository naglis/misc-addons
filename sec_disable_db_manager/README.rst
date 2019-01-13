========================
Disable Database Manager
========================

Installation
============

It is recommended to restart Odoo after the module is installed.

Configuration
=============

Start Odoo with the ``--no-database-list`` CLI parameter or the ``list_db``
configuration parameter set to ``False`` to disable the database management
functions.

.. note:: When running Odoo with multiple databases, users will not be able to
   select the database to login to, because the database selector window will be
   disabled. You can set the default database name with the `-d`, `--database`
   CLI parameter or `db_name` configuration parameter, or specify the database
   name to login to in the URL, e.g.: `/web/login?db=mydatabase`.
