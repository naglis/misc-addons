/* Copyright 2018 Naglis Jonaitis
 * License LGPL-3 or later (https://www.gnu.org/licenses/lgpl). */
odoo.define('web_bsod.exception_handler', function (require) {
    'use strict';

    var core = require('web.core');
    var BSODWidget = require('web_bsod.BSOD');

    var BSODHandler = core.Class.extend({
        init: function(parent, error) {
            this.error = error;
        },
        display: function() {
            var bsod = new BSODWidget(this, this.error);
            bsod.appendTo($('body'));
            $(document).one('keyup', function(e) {
                e.preventDefault();
                e.stopPropagation();
                if (e.keyCode === 27) {
                    window.location.reload();
                }
                bsod.destroy();
            });
        }
    });

    core.crash_registry.add('odoo.addons.web_bsod.exceptions.BSOD', BSODHandler);

    return BSODHandler;
});
