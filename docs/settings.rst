.. module:: django.conf.settings

.. _settings:

Configuration via Django settings
=================================

Some of ``pwned-passwords-django``'s behavior is configurable via Django
settings. To do so, add the following new setting to your Django settings
module:

.. data:: PWNED_PASSWORDS

   A :class:`dict` containing configuration specific to
   ``pwned-passwords-django``.

   The default values, if not set, are equivalent to:

   .. code-block:: python

      PWNED_PASSWORDS = {
         "ADD_PADDING": True,
         "API_TIMEOUT": 1.0,
         "PASSWORD_REGEX": r"PASS",
      }

   The keys in ``PWNED_PASSWORDS`` have the following semantics:

   **ADD_PADDING**
      A :class:`bool` indicating whether to send the custom ``Add-Padding:
      true`` HTTP header on requests to Pwned Passwords. This header enables `a
      feature in the Pwned Passwords API which "pads" responses with additional
      irrelevant results
      <https://haveibeenpwned.com/API/v3#PwnedPasswordsPadding>`_.

      This trades off some performance for security; without the "padding", it
      is potentially possible for an attacker who can observe your
      request/response traffic to extract information about the requests being
      made by observing variations in the sizes of the response bodies (which
      is something that even encryption/HTTPS cannot hide). Having Pwned
      Passwords "pad" all responses with random irrelevant results defeats this
      style of traffic analysis, at the cost of increasing the average size of
      the responses and thus the amount of data which must be transferred.

      Default value, if not provided, is ``True``.

   **API_TIMEOUT**
      A :class:`float` indicating the desired connection timeout threshold for
      contacting Pwned Passwords, in seconds.

      Default value, if not provided, is ``1.0`` (one second).

   **PASSWORD_REGEX**
      A :class:`str` -- *not* a compiled regex object -- to be used as a regex
      by :ref:`the middleware <middleware>` when scanning request payloads for
      possible passwords. Any key in the request's
      :attr:`~django.http.HttpRequest.POST` which matches (via
      :func:`re.search`) this regex will be checked against Pwned Passwords.

      The supplied string will be compiled to a regex with :func:`re.compile`
      using the :data:`re.IGNORECASE` flag.

      Default value, if not provided, is ``r"PASS"``.
