/* Copyright 2018-2019 Naglis Jonaitis
 * License LGPL-3 or later (https://www.gnu.org/licenses/lgpl). */
odoo.define('web_notify_action.action_notification', function (require) {
    'use strict';

    var Notification = require('web.Notification');
    var AbstractService = require('web.AbstractService');
    var core = require('web.core');

    var ActionNotification = Notification.extend({
        template: 'ActionNotification',

        /**
        * @override
        * @param {Notification} parent
        * @param {Object} params
        * @param {string} params.title notification title (plaintext)
        * @param {string} params.message notification main message (plaintext)
        * @param {string} params.type 'notification' or 'warning'
        * @param {boolean} [params.sticky=false] if true, the notification will stay
        *   visible until the user clicks on it (timeout will be ignored)
        * @param {integer} [params.timeout=2500] delay in miliseconds before
        *   the notification is closed
        * @param {string} [params.className] className to add on the dom
        * @param {string} [params.icon] font-awesome class
        * @param {string} [params.image_url] URL of an image to display alongside
        *   the message
        * @param {function} [params.onClose] callback when the user click on the x
        *   or when the notification is auto close (no sticky)
        * @param {Object[]} params.buttons
        * @param {function} params.buttons[0].click callback on click
        * @param {boolean} [params.buttons[0].primary] display the button as primary
        * @param {string} [params.buttons[0].text] button label
        * @param {string} [params.buttons[0].icon] font-awesome className or image src
        * @param {Object} [params.buttons[0].action] a hash of an action that can
        *   be executed by the action manager
        */
        init: function(parent, params) {
            var self = this;
            var buttons = params.buttons || [];
            for(var i = 0; i < buttons.length; i++) {
                if (buttons[i].action) {
                    buttons[i].click = function() {
                        self.do_action(this.action);
                    }
                }
            }
            this._super(parent, params);

            this.image_url = params.image_url;
            this._autoCloseDelay = params.timeout || this._autoCloseDelay;
            this.icon = params.icon || this.icon;
            this.sticky = params.sticky;
        }
    });

    var ActionNotificationManager =  AbstractService.extend({
        dependencies: ['bus_service'],
        start: function () {
            this._super.apply(this, arguments);
            this._listenOnBuses();
        },
        _listenOnBuses: function () {
            this.call('bus_service', 'onNotification', this, this._onNotification);
        },
        _onNotification: function (notifications) {
            var self = this;
            _.each(notifications, (function(notification) {
                if (notification[0][1] === 'web_notify_action.notify_action') {
                    debugger;
                    self.call('notification', 'notify', _.extend(notification[1] || {}, {
                        Notification: ActionNotification,
                    }));
                }
            }).bind(self));
        }
    });

    core.serviceRegistry.add('action_notification_manager_service', ActionNotificationManager);

    return {
        ActionNotification: ActionNotification,
        ActionNotificationManager: ActionNotificationManager
    };

});
