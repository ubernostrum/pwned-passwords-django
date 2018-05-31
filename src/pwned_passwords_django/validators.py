from django.core.exceptions import ValidationError
from django.utils.six import string_types
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

        # If there is no plural, use the same message for both forms.
        if isinstance(error_message, string_types):
            singular, plural = error_message, error_message
        else:
            singular, plural = error_message
        self.error_message = {
            'singular': singular,
            'plural': plural
        }

    def validate(self, password, user=None):
        amount = api.pwned_password(password)
        if amount:
            raise ValidationError(
                ungettext(
                    self.error_message['singular'],
                    self.error_message['plural'],
                    amount,
                ),
                params={'amount': amount},
                code='pwned_password',
            )

    def get_help_text(self):
        return self.help_message
