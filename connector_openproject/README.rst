=====================
OpenProject Connector
=====================

OpenProject Connector is a unidirectional (OpenProject -> Odoo) connector,
compatible with Odoo 10.0 and OpenProject_ 7.3+.

What can be synchronized?
=========================

- Users -> Users (`res.users`);
- Projects -> Projects (`project.project`);
- Work Packages -> Tasks (`project.task`);
- Time Entries -> Timesheet Lines (`account.analytic.line`);
- Work Package Activities (comments, updates) -> Messages (`mail.message` under
  `project.task`);
- Work Package Statuses -> Stages (`project.task.type`).

Installation
============

To install this module, you need to:

#. Install `Odoo Connector`_ module.
#. Install pip dependencies for this module (check the *requirements.txt* file
   at the top level in module repository).

Configuration
=============

OpenProject side
----------------

#. Create a limited role for Odoo synchronization, eg. *Odoo* with the following permissions:

   #. *Time tracking / View spent time*.
   #. *Work package tracking / View work packages*.

#. Create an Odoo synchronization user (eg. *Odoo Bot*) and assign it with the *Odoo* role to all projects you will be syncing with Odoo.
#. Generate an API key for the *Odoo Bot* user.

Odoo side
---------

#. Configure the OpenProject Connector queue job channel in your Odoo
   configuration file, eg.:

    .. code-block:: ini

        [queue_job]
        channels = root:2,root.openproject:1

#. Login to your Odoo instance with a user with *Connector Manager* access
   rights.
#. In debug mode (*Settings -> Activate the developer mode*) go to *Connectors
   -> OpenProject -> Backends* and create a new backend for your OpenProject
   instance, fill in the name, OpenProject instance URL and API key of the
   OpenProject synchronization user. Once finished, save the record.

Usage
=====

#. Login to your Odoo instance with a user with *Connector Manager* access
   rights.
#. In debug mode go to *Settings -> Technical  -> Automation -> Scheduled
   Actions*, select *OpenProject Sync*) and click the *Run Manually* button or
   click the *Run Import* button on the OpenProject backend record.
#. On the OpenProject backend record, click on the *Projects* button at the
   top - the projects from your OpenProject instance will appear here after
   synchronization finishes.
#. Once all projects are created (no more pending jobs in *Job Queue -> Queue
   -> Jobs*), configure the projects and things you want to synchronize for
   each project (whether to sync work packages descriptions, and which types of
   activites to sync).
#. Once done with the configuration, run the *OpenProject Sync* cron job again.

Known issues / Roadmap
======================

* OpenProject time entry API endpoint currently does not support *updatedAt* filtering. See also: https://goo.gl/Kst39h.

FAQ
===

Are you planning on making it bidirectional?
--------------------------------------------

Personally, no, as currently I do not have a need for it. If you want to give a
try yourself, please note that the current version of the OpenProject API (at
the time of writing: API v3 on OpenProject 7.4) `does not support
<http://docs.openproject.org/apiv3-doc/#projects>`_ creating projects via API,
same goes for time entries, but at least for time entries `create support is
planned <https://community.openproject.com/projects/openproject/work_packages/26108/activity>`_.

Credits
=======

Images
------

* Module icon by `OpenProject Foundation`_.

.. _OpenProject: https://www.openproject.org/
.. _Odoo Connector: https://github.com/oca/connector
.. _OpenProject Foundation: https://www.openproject.org/contact-us/
