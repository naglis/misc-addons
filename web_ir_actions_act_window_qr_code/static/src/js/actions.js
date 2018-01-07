/* Copyright 2018 Naglis Jonaitis
 * License LGPL-3 or later (https://www.gnu.org/licenses/lgpl). */
odoo.define('web.web_ir_actions_act_window_qr_code', function(require) {
    'use strict';

    var ActionManager = require('web.ActionManager');
    var Dialog = require('web.Dialog');
    var core = require('web.core');

    var QWeb = core.qweb;
    var _t = core._t;

    ActionManager.include({
        ir_actions_act_window_qr_code: function(action, options) {
            var self = this;
            var dialog = new Dialog(
                this,
                _.extend({
                    $content: QWeb.render('QRCode', {
                        data: action.data,
                        help_text: action.help_text,
                        flags: action.flags,
                    }),
                    size: action.size || 'medium',
                    title: action.title || _t('QR Code'),
                    buttons: [
                        {
                            text: _t('Close'),
                            close: true
                        }
                    ],
                }, options)
            );

            dialog.opened().then(function () {
                var $spinner = dialog.$el.find('.o_spinner');
                var $img = dialog.$el.find('img');
                self._rpc({
                    route: '/web/qrcode',
                    params: {
                        data: action.data
                    }
                }).then(function (result) {
                    $img.attr('src', 'data:image/png;base64,' + btoa(result.image)).show();
                }).fail(function (error, event) {
                    event.preventDefault();
                    $img.after(QWeb.render('QRCodeError', {
                        error: error.data.arguments[0] || _t('Unknown error'),
                    }));
                }).always(function () {
                    $spinner.hide();
                });
            });
            return dialog.open();
        },
    });

});
