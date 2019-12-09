"""
A Django password validator using the Pwned Passwords API to check for
compromised passwords.

"""

from typing import Optional, Union

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.password_validation import CommonPasswordValidator
from django.core.exceptions import ValidationError
from django.utils.functional import Promise
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import ungettext

from . import api


StrOrTranslation = Union[str, Promise]


common_password_validator = CommonPasswordValidator()


class PwnedPasswordsValidator:
    """
    Password validator which checks the Pwned Passwords database.

    """

    DEFAULT_HELP_MESSAGE = common_password_validator.get_help_text()
    DEFAULT_PWNED_MESSAGE = _("This password is too common.")

    def __init__(
        self,
        error_message: Optional[StrOrTranslation] = None,
        help_message: Optional[StrOrTranslation] = None,
    ):
        self.help_message = help_message or self.DEFAULT_HELP_MESSAGE
        error_message = error_message or self.DEFAULT_PWNED_MESSAGE

        # If there is no plural, use the same message for both forms.
        if isinstance(error_message, (str, Promise)):
            singular, plural = error_message, error_message
        else:
            singular, plural = error_message
        self.error_message = {"singular": singular, "plural": plural}

    def validate(self, password: str, user: Optional[AbstractBaseUser] = None):
        amount = api.pwned_password(password)
        if amount is None:
            # HIBP API failure. Instead of allowing a potentially compromised
            # password, check Django's list of common passwords generated from
            # the same database.
            common_password_validator.validate(password, user)
        elif amount:
            raise ValidationError(
                ungettext(
                    self.error_message["singular"], self.error_message["plural"], amount
                ),
                params={"amount": amount},
                code="pwned_password",
            )

    def get_help_text(self) -> str:
        return self.help_message
