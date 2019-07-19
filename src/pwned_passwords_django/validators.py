"""
A Django password validator using the Pwned Passwords API to check for
compromised passwords.

"""

from django.contrib.auth.password_validation import CommonPasswordValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from django.utils.translation import ngettext

from . import api


class PwnedPasswordsValidator:
    """
    Password validator which checks the Pwned Passwords database.

    """
    DEFAULT_HELP_MESSAGE = _(
        "Your password can't be a commonly used password."
    )
    DEFAULT_PWNED_MESSAGE = _(
        "This password is too common."
    )

    def __init__(self, error_message=None, help_message=None):
        self.help_message = help_message or self.DEFAULT_HELP_MESSAGE
        error_message = error_message or self.DEFAULT_PWNED_MESSAGE

        # If there is no plural, use the same message for both forms.
        if isinstance(error_message, str):
            singular, plural = error_message, error_message
        else:
            singular, plural = error_message
        self.error_message = {
            'singular': singular,
            'plural': plural
        }

    def validate(self, password, user=None):
        amount = api.pwned_password(password)
        if amount is None:
            # HIBP API failure. Instead of allowing a potentially compromised
            # password, check Django's list of common passwords generated from
            # the same database.
            CommonPasswordValidator().validate(password, user)
        elif amount:
            raise ValidationError(
                ngettext(
                    self.error_message['singular'],
                    self.error_message['plural'],
                    amount,
                ),
                params={'amount': amount},
                code='pwned_password',
            )

    def get_help_text(self):
        return self.help_message
