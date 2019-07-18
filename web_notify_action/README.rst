========================
User Action Notfications
========================

Server-initiated action notifications on steroids!

.. code-block:: python

   self.env.user._notify_action({
       "title": "Hello World",
       "message": "This is a notification with custom actions.",
       "type": "notification",  # Possible values: ['notification', 'warning'].  Default: 'notification'
       "icon": "fa-check",  # Font Awesome class
       "image_url": "https://odoocdn.com/openerp_website/static/src/img/assets/png/odoo_logo.png",
       "timeout": 2500, # In miliseconds. Ignored if sticky = True. Default: 2500
       "sticky": True,  # If true, do not close notification automatically.  Default: False
       "buttons": [{
           "primary": True, # If true, display button as primary.
           "text": "Open", # Button label text.
           "icon": "fa-users", # Font Awesome class or image URL.
           "action": { # Any action dict that can be executed by the action manager.
               "type": "ir.actions.act_window",
               "view_mode": "tree",
               "res_model": "res.users",
               "views": [[False, 'list'], [False,'form']],
               "name": "Users",
               "target": "new",
           },
       }, {
           "primary": False,
           "text": "Open URL",
           "icon": "fa-link",
           "action": {
               "type": "ir.actions.act_url",
               "url": "https://naglis.me/",
               "target": "new",
           }
       }],
   })

.. note:: HTML in `title` or `message` is not supported due to safety concerns.

TODO
====

* JavaScript tests.
* Documentation and demos.
* Multi-action via drop-down button.
* Model method call actions?
* Progress bar?
