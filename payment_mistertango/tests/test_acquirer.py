# Copyright 2018 Naglis Jonaitis
# License AGPL-3 or later (https://www.gnu.org/licenses/agpl).

from lxml import etree

from .common import (
    TEST_AMOUNT,
    TestMistertangoCommon,
)


class TestPaymentAcquirer(TestMistertangoCommon):

    def get_rendered_data(self, reference, amount=TEST_AMOUNT,
                          currency_id=None, partner_id=False, values=None):
        form_html = self.acquirer.render(
            reference, amount, currency_id or self.ref('base.EUR'),
            values=values or self.buyer_values)
        root = etree.HTML(form_html).getroottree()
        input_el = root.find('//input[@name="mistertango_data"]')
        return {
            k[len('data-'):]: v
            for k, v in input_el.attrib.items()
            if k.startswith('data-')
        } if input_el is not None else {}

    def test_form_render_has_values(self):
        attrs = self.get_rendered_data(self.tx_1.reference)
        self.assertEqual(attrs['amount'], str(TEST_AMOUNT))
        self.assertEqual(attrs['currency'], 'EUR')
        self.assertEqual(attrs['payer'], self.buyer_values['partner_email'])
        self.assertEqual(
            attrs['recipient'], self.acquirer.mistertango_username)
        self.assertEqual(attrs['reference'], self.tx_1.reference)
        self.assertFalse(attrs['error-msg'])

    def test_market_is_rendered(self):
        market = 'EE'
        self.acquirer.mistertango_market = market
        attrs = self.get_rendered_data(self.tx_1.reference)
        self.assertEqual(attrs['market'], market)

    def test_unsupported_currency_error_msg_is_rendered(self):
        attrs = self.get_rendered_data(
            self.tx_1.reference, currency_id=self.ref('base.USD'))
        self.assertNotEqual(attrs['currency'], '')
        self.assertTrue(attrs['error-msg'])

    def test_default_lang_is_rendered(self):
        default_lang = 'fi'
        self.acquirer.mistertango_default_lang = default_lang
        attrs = self.get_rendered_data(self.tx_1.reference)
        self.assertEqual(attrs['lang'], default_lang)

    def test_payment_type_is_rendered(self):
        payment_type = 'bitcoin'
        self.acquirer.mistertango_payment_type = payment_type
        attrs = self.get_rendered_data(self.tx_1.reference)
        self.assertEqual(attrs['payment-type'], payment_type)
