/* Copyright 2018 Naglis Jonaitis
 * License LGPL-3 or later (https://www.gnu.org/licenses/lgpl). */
odoo.define('web_bsod.BSOD', function (require) {
    'use strict';

    var Widget = require('web.Widget');

    var BSODWidget = Widget.extend({
        template: 'BSOD',
        init: function(parent, error) {
            this._super(parent);
            this.error = error;
        }
    });
    return BSODWidget;
});
