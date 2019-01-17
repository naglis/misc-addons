========================
Paysera Payment Acquirer
========================

A Paysera_ payment acquirer implementation for Odoo.

Requirements
~~~~~~~~~~~~

- cryptography_ (for private/public key based signature verification)

Changelog
~~~~~~~~~

v2.1.1 (2019-01-17)
-------------------
- Allows to change Paysera redirect URLs via `_get_paysera_redirect_urls()`.

v2.1.0 (2019-01-16)
-------------------
- Allows to validate actually paid amount/currency (#14)
- Adds validation of callback amount, currency and test mode parameters
- Added more test cases
- Various small fixes, improvements and refactorings

v2.0.3 (2019-01-15)
-------------------
- Small refactorings

v2.0.2 (2017-09-16)
-------------------
- Small refactorings
- Lithuanian translation update

v2.0.1 (2017-09-10)
-------------------
- Small refactorings

v2.0.0 (2017-06-18)
-------------------
- Made *ss2* signature check required.
- RSA signature check is now based on the *cryptography* library
- Added field level groups on *paysera_project_id* and *paysera_sign_password*
  fields on *payment.acquirer*.
- General clean-up.

v1.0.2 (2015-10-18)
-------------------

- Use new Odoo v8.0 API.

v1.0.1
------

- Initial working version.
- Private/public key signature verification.

.. _Paysera: https://www.paysera.com
.. _cryptography: https://pypi.python.org/pypi/cryptography
