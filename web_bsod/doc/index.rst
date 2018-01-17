====================
Blue Screen of Death
====================

Installation
------------

This module can be installed as any other regular Odoo addon.

Usage
-----

#. Add this module to your module's dependencies (*depends* key in module's
   manifest).
#. Raise the *BSOD* exception in your Python code:

    .. code-block:: python

        from odoo import _, api, models
        from odoo.addons.web_bsod import exceptions


        class ResUsers(models.Model):
            _inherit = 'res.users'

            @api.multi
            def unlink(self):
                if self.env.user.id in self.ids:
                    raise exceptions.BSOD(_('Does not compute'))
                return super().unlink()
