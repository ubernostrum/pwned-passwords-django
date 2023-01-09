"""
A Django password validator using the Pwned Passwords API to check for
compromised passwords.

"""
import logging
import typing

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.password_validation import CommonPasswordValidator
from django.core.exceptions import ValidationError
from django.utils.functional import Promise
from django.utils.translation import gettext_lazy as _
from django.utils.translation import ngettext
from django.views.decorators.debug import sensitive_variables

from . import api, exceptions

logger = logging.getLogger(__name__)

# A value that is either a string, or a lazy Promise object that will resolve to a
# string.
Message = typing.Union[str, Promise]

# A value that is either a Message, or a 2-tuple of Message providing singular and
# plural forms.
PluralMessage = typing.Union[Message, typing.Tuple[Message, Message]]


class PwnedPasswordsValidator:
    """
    Password validator which checks the Pwned Passwords database.

    """

    default_error_message = _("This password is too common.")

    def __init__(
        self,
        error_message: typing.Optional[PluralMessage] = None,
        help_message: typing.Optional[Message] = None,
        api_client: api.PwnedPasswords = api.client,
    ):
        self.fallback_validator = CommonPasswordValidator()
        self.help_message = help_message or self.fallback_validator.get_help_text()
        error_message = error_message or self.default_error_message
        self.api_client = api_client

        # If there is no plural, use the same message for both forms.
        if isinstance(error_message, (str, Promise)):
            singular, plural = error_message, error_message
        else:
            singular, plural = error_message
        self.error_message = {"singular": singular, "plural": plural}

    @sensitive_variables()
    def validate(self, password: str, user: typing.Optional[AbstractBaseUser] = None):
        """
        Check a proposed password against Pwned Passwords and reject the password if
        it has been compromised.

        This method is called by most high-level account-creation and account-editing
        operations in Django.

        :raises django.core.exceptions.ValidationError: when the proposed password is
          compromised.

        """
        # pylint: disable=unused-argument
        try:
            amount = self.api_client.check_password(password)
        except exceptions.PwnedPasswordsError:
            # HIBP API failure. Instead of allowing a potentially compromised
            # password, check Django's list of common passwords generated from
            # the same database.
            logger.error(
                "Falling back to Django CommonPasswordValidator due "
                "to error contacting Pwned Passwords."
            )
            self.fallback_validator.validate(password)
        else:
            if amount:
                raise ValidationError(
                    ngettext(
                        self.error_message["singular"],
                        self.error_message["plural"],
                        amount,
                    ),
                    params={"amount": amount},
                    code="password_compromised",
                )

    def get_help_text(self) -> Message:
        """
        Return help text for this validator.

        """
        return self.help_message

    def deconstruct(self) -> typing.Tuple[str, tuple, dict]:
        """
        Deconstruct this validator instance for serialization by the Django ORM
        migration framework.

        Note that only :attr:`error_message` and :attr:`help_message` are serialized and
        stored in migrations when this validator is attached to a model field;
        :attr:`api_client`, if present, will not be serialized or stored in migrations,
        and so in migrations will always be the default
        :data:`~pwned_passwords_django.api.client` instance.

        """
        return (
            "pwned_passwords_django.validators.PwnedPasswordsValidator",
            (),
            {"help_message": self.help_message, "error_message": self.error_message},
        )

    def __eq__(self, other: object) -> bool:
        """
        Equality check for this validator; this method is required to allow this
        validator to be serializable by the Django ORM migration framework.

        Note that only :attr:`error_message` and :attr:`help_message` are considered
        here; two validator instances which differ only in their :attr:`api_client` will
        compare equal.

        """
        if not isinstance(other, PwnedPasswordsValidator):
            return NotImplemented
        return (
            self.error_message == other.error_message
            and self.help_message == other.help_message
        )
