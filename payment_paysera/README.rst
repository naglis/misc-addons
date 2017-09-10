===============
payment_paysera
===============

A Paysera payment acquirer implementation for Odoo.

Requirements
~~~~~~~~~~~~

- cryptography_ (for private/public key based signature verification)

Changelog
~~~~~~~~~

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

.. _cryptography: https://pypi.python.org/pypi/cryptography
