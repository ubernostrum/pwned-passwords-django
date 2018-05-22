from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _

from . import api


class PwnedPasswordsValidator(object):
    """
    Password validator which checks the Pwned Passwords database.

    """
    HELP_MESSAGE = _("Your password can't be a commonly used password.")
    PWNED_MESSAGE = _(
        "This password is known to have appeared in a public data breach."
    )

    def validate(self, password, user=None):
        if api.pwned_password(password):
            raise ValidationError(self.PWNED_MESSAGE)

    def get_help_text(self):
        return self.HELP_MESSAGE  # pragma: no cover
