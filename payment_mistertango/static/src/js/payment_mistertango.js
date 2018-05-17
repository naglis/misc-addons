/* Copyright 2018 Naglis Jonaitis
 * License AGPL-3 or later (https://www.gnu.org/licenses/agpl). */
odoo.define('payment_mistertango.MistertangoWrapper', function (require) {
    'use strict';

    var ajax = require('web.ajax');
    var core = require('web.core');
    var Class = require('web.Class');
    var _t = core._t;

    var MistertangoWrapper = Class.extend({
        init: function ($target, $btn) {
            this.$target = $target;
            this.$btn = $btn;
            this.redirect = false;
            this.acquirer_id = this.$btn.parents('div.oe_sale_acquirer_button').first().data('id');
            if (!this.acquirer_id) {
                this.show_error(_t('Mistertango acquirer is configured incorrectly.'), 'danger');
                return;
            }
            var self = this;
            if (self.$btn.data('error-msg')) {
                // Show unsupported currency message.
                self.$btn.replaceWith(
                    $('<div/>', {
                        'class': 'alert alert-info',
                        'text': self.$btn.data('error-msg'),
                    })
                );
            } else {
                self.$btn.on('click', _.bind(self.on_click, self));
            }
        },
        show_error: function (message, level) {
            if (!this.$target.prev().hasClass('o_payment_mistertango_alerts')) {
                $('<div/>', {
                    'class': 'o_payment_mistertango_alerts'
                }).insertBefore(this.$target);
            }
            $('<div/>', {
                'class': 'alert alert-dismissible' + (level
                    ? ' alert-' + level
                    : ''),
                'role': 'alert',
                'html': $('<a/>', {
                    'href': '#',
                    'class': 'close',
                    'data-dismiss': 'alert',
                    'aria-label': 'Close',
                    'html': '&times;'
                }).add($('<p/>', {'text': message}))
            }).appendTo(this.$target.prev());
        },
        clear_errors: function () {
            if (this.$target.prev().hasClass('o_payment_mistertango_alerts')) {
                this.$target.prev().remove();
            }
        },
        // Called when the Mistertango pop-up is opened.
        on_opened: function () { // eslint-disable-line no-empty-function
        },
        // Called when the Mistertango pop-up is closed.
        on_closed: function () {
            if (this.redirect === true) {
                window.location.href = '/shop/payment/validate';
            }
        },
        // Called if Mistertango payment was successful.
        on_success: function () {
            this.redirect = true;
            this.$btn
                .text(_t('Paid!'))
                .prop('disabled', true);
        },
        on_error: function () {
            this.redirect = false;
            this.show_error(_t('An error occurred during your payment via Mistertango. Please try again.'), 'danger');
        },
        // Called if customer decides to pay via bank transfer.
        on_offline_payment: function () {
            this.redirect = true;
        },
        on_click: function(event) {
            event.preventDefault();
            event.stopPropagation();
            this.clear_errors();

            var self = this;
            var params = {
                'tx_type': 'form'
            };

            // Mistertango script was not loaded. It's likely due to some ad/JS
            // blocking plugin blocking third party scripts.
            if (typeof mrTangoCollect === 'undefined') {
                this.show_error(_t('There was a problem while contacting Mistertango. Please make sure that you disable any ad blocking plugins in your browser and then try again after refreshing this page.'), 'warning');
                return;
            }

            /* eslint-disable no-undef */
            mrTangoCollect.load();
            mrTangoCollect.onOpened = _.bind(this.on_opened, this);
            mrTangoCollect.onClosed = _.bind(this.on_closed, this);
            mrTangoCollect.onSuccess = _.bind(this.on_success, this);
            mrTangoCollect.onError = _.bind(this.on_error, this);
            mrTangoCollect.onOffLinePayment = _.bind(this.on_offline_payment, this);
            ajax.jsonRpc('/shop/payment/transaction/' + this.acquirer_id, 'call', params).then(function (response) {
                var new_reference = $('<html/>').html(response).find('button.mistertango-submit').data('reference');
                mrTangoCollect.set.recipient(self.$btn.data('recipient'));
                mrTangoCollect.set.payer(self.$btn.data('payer'));
                mrTangoCollect.set.lang(self.$btn.data('lang'));
                mrTangoCollect.set.amount(self.$btn.data('amount'));
                mrTangoCollect.set.currency(self.$btn.data('currency'));
                mrTangoCollect.set.description(new_reference);
                mrTangoCollect.set.payment_type_forced(self.$btn.data('payment-type'));
                if (self.$btn.data('market')) {
                    mrTangoCollect.set.custom({
                        'market': self.$btn.data('market'),
                    });
                }
                mrTangoCollect.submit();
            });
            /* eslint-enable no-undef */
        },
    });
    return MistertangoWrapper;
});

odoo.define('payment_mistertango.payment', function (require) {
    'use strict';

    require('website.website');
    var MistertangoWrapper = require('payment_mistertango.MistertangoWrapper');

    var $target = $('#payment_method');
    if (!$target.length) {
        return $.Deferred().reject('DOM does not contain "#payment_method"');
    }

    // We support multiple Mistertango acquirer buttons on the same page,
    // however, the Mistertango widget itself seems not to support it :(
    $target.find('button.mistertango-submit').each(function () {
        new MistertangoWrapper($target, $(this)); // eslint-disable-line no-new
    });
});
