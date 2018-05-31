from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _
from django.utils.translation import ungettext

from . import api


class PwnedPasswordsValidator(object):
    """
    Password validator which checks the Pwned Passwords database.

    """
    DEFAULT_HELP_MESSAGE = _(
        "Your password can't be a commonly used password."
    )
    DEFAULT_PWNED_MESSAGE = (
        "This password is known to have appeared in a public data breach."
    )

    def __init__(self, error_message=None, help_message=None):
        self.help_message = help_message or self.DEFAULT_HELP_MESSAGE
        error_message = error_message or self.DEFAULT_PWNED_MESSAGE
        # If there is no plural, use the same message for both forms
        if not isinstance(error_message, (list, tuple)):
            self.error_message = (error_message, error_message)
        else:
            self.error_message = error_message

    def validate(self, password, user=None):
        amount = api.pwned_password(password)
        if amount:
            raise ValidationError(
                ungettext(
                    self.error_message[0],
                    self.error_message[1],
                    amount,
                ),
                params={'amount': amount},
                code='pwned_password',
            )

    def get_help_text(self):
        return self.help_message
