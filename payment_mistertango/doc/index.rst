============================
Mistertango Payment Acquirer
============================

Installation
------------

Before installing the addon, make sure the `cryptography`_ Python package is
installed in your system. You can install it by running:

.. code-block:: bash

    pip install 'cryptography>=2.0.0,<3.0.0'

You can read more about installing Python packages `here`_.

.. note:: For best compatibility *cryptography* version >=2.0.0 and <3.0.0 is
    recommended.

After that, this addon can be installed as any other regular Odoo addon:

- Unzip the addon in one of Odoo's addons paths.
- Login to Odoo as a user with administrative privileges, go into debug mode.
- Go to *Apps -> Update Apps List*, click *Update* in the dialog window.
- Go to *Apps -> Apps*, remove the *Apps* filter in the search bar and search
  for *Mistertango Payment Acquirer*. Click *Install* button on the addon.

.. note:: You you would like to use the payment acquirer in the eCommerce shop,
    make sure the *eCommerce* module (*website_sale*) is installed as well.

Configuration
-------------

Before configuring the Mistertango payment acquirer, register an account on
`Mistertango`_ and login.

Once you have logged in, click on the settings menu icon at the top right
corner of the page and select *Payment Collection Settings*.

.. image:: screenshot_2.png
    :alt: Payment collection settings page.
    :class: img-responsive img-thumbnail

In this window:

- Set *Enable/disable payment collection service* to *Enabled*.
- Specify your shop's address in the *Shop website address (URL)* field.
- In the *Choose module or service* field select *Self integration*.
- In the *Callback address (URL)* field, specify the acquirer callback URL. It
  should be in the following format: *https://<your shop url>/payment/mistertango/callback*.
- Set the *Enable test mode* field to *Enabled* or *Disabled* depending if you
  want to test the addon yourself before going into production.
- Click *Save*.

.. note:: For best results when testing make sure your Odoo instance is
    publicly available on the Internet - if you are running it only locally,
    you will not be able to receive callback requests from Mistertango.

Also, take note of the *Integration credentials* in the same window.

Now, let's configure the payment acquirer:

- Login to Odoo as a user with administrative privileges, go into debug mode.
- Go to *Website Admin -> Configuration -> eCommerce -> Payment Acquirers* or
  *Invoicing -> Configuration -> Payments -> Payment Acquirers* and click
  *Configure* on the *Mistertango* acquirer:

.. image:: screenshot_3.png
   :alt: Payment Acquirers view in Odoo.
   :class: img-responsive img-thumbnail

- In the *Credentials* tab, enter the username and secret key from Mistertango
  *Integration credentials* section noted earlier:

.. image:: screenshot_4.png
   :alt: Mistertango payment acquirers credentials configuration.
   :class: img-responsive img-thumbnail

- If necessary, you maye change the forced payment type (eg. *Bank Link*, *Bank
  Transfer*, *Bitcoin* or *Credit Card*), default Mistertango widget language
  and the market country for your eCommerce shop:

.. image:: screenshot_5.png
   :alt: Mistertango payment acquirers configuration.
   :class: img-responsive img-thumbnail

- Click on the *Save* button.
- Click on the *Publish* button to make the acquirer available for you in the
  eCommerce shop.

.. note:: The *Test* / *Production* acquirer environments in Odoo do not apply
    to Mistertango acquirer, because test mode is configuration on the
    `Mistertango`_ website.

.. _cryptography: https://pypi.org/project/cryptography/
.. _here: https://packaging.python.org/tutorials/installing-packages/
.. _Mistertango: https://mistertango.com/
