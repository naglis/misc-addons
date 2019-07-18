/* Copyright 2018 Naglis Jonaitis
 * License LGPL-3 or later (https://www.gnu.org/licenses/lgpl). */
odoo.define('web_notify_action.action_notification', function (require) {
    'use strict';

    var bus = require('bus.bus').bus;
    var WebClient = require('web.WebClient');
    var Widget = require('web.Widget');

    /**
    * params:
    * - title: title of the notification.
    * - text: text of the notification.
    * - allow_dismiss: boolean if the notification has a close button. Default:
    *   true.
    * - animate: boolean if the notification show/hide should be animated.
    *   Default: true.
    * - timeout: duration in miliseconds after which the notification is
    *   closed. Default: 2500. Set to 0 if you want to disable the timeout.
    * - type: one of ('notification', 'error'). Default: 'notification'.
    * - icon: notification icon CSS classes. Could be Font-Awesome icons or
    *   other (if available). Default: 'fa fa-3x fa-lightbulb-o'.
    * - image_url: URL of an image to be displayed on the side of the text.
    * - buttons: an array of action buttons. See below for options available
    *   for a button.
    *
    * button:
    * - tag: a slug-like tag for the action (required). If not set, the button
    *   will not be displayed.
    * - class: CSS classes for the button element. Default: 'btn btn-default'.
    * - icon: button icon CSS classes. Could be Font-Awesome icons or
    *   other (if available). By default no icon is added.
    * - label: the button label text.
    * - action: a hash of any action that can be executed by the action
    *   manager.
    */
    var ActionNotification = Widget.extend({
        template: 'ActionNotification',
        events: {
            'click .o_close': 'on_close_click',
            'click .notify_action_button': 'on_action_click'
        },
        init: function(parent, params) {
            this._super.apply(this, arguments);
            this.title = params.title;
            this.text = params.text;
            this.params = _.defaults(params || {}, {
                'buttons': [],
                'allow_dismiss': true,
                'animate': true,
                'timeout': 2500,
                'type': 'notification',
                'icon': 'fa fa-3x fa-lightbulb-o'
            });

            this.tag_actions = {};
            for(var i = 0; i < this.params.buttons.length; i++) {
                var button = this.params.buttons[i];
                var tag = button.tag;
                if(tag) {
                    this.tag_actions[tag] = button.action;
                }
            }
        },
        start: function() {
            this._super.apply(this, arguments);
            if(this.params.type === 'error') {
                this.$el.addClass('o_error');
            }

            var self = this,
                timeout = this.params.timeout;
            if(this.params.animate) {
                this.$el.animate({opacity: 1.0}, {
                    duration: 'normal',
                    easing: 'swing',
                    complete: function() {
                        if(timeout) {
                            setTimeout(self.destroy.bind(self), timeout);
                        }
                    }
                });
            } else {
                this.$el.css('opacity', 1.0);
                if(timeout) {
                    setTimeout(this.destroy.bind(this), timeout);
                }
            }

        },
        destroy: function() {
            if(!this.params.animate) {
                return this._super.apply(this, arguments);
            }
            this.$el.animate({opacity: 0.0}, {
                'duration': 'normal',
                'easing': 'swing',
                'complete': this._super.bind(this)
            });
        },
        on_action_click: function(event) {
            event.preventDefault();
            var action = this.tag_actions[$(event.target).data('action-tag')] || false;
            if(action) {
                this.do_action(action).then(this.destroy.bind(this));
            } else {
                this.destroy();
            }
        },
        on_close_click: function(event) {
            event.preventDefault();
            this.destroy();
        }
    });

    WebClient.include({
        show_application: function() {
            var self = this;
            bus.on('notification', this, function(notifications) {
                _.each(notifications, (function(notification) {
                    if (notification[0][1] === 'web_notify_action.notify_action') {
                        this.notification_manager.display(new ActionNotification(this.notification_manager, notification[1]));
                    }
                }).bind(self));
            });
            return this._super.apply(this, arguments);
        }
    });

    return {
        ActionNotification: ActionNotification
    };

});
