"""
Test the Pwned Passwwords validator.

"""

# SPDX-License-Identifier: BSD-3-Clause

import httpx
from django.contrib.auth.password_validation import CommonPasswordValidator
from django.core.exceptions import ValidationError
from django.test import override_settings

from pwned_passwords_django import api
from pwned_passwords_django.validators import PwnedPasswordsValidator

from .base import PwnedPasswordsTests


class PwnedPasswordsValidatorsTests(PwnedPasswordsTests):
    """
    Test the Pwned Passwords validator.

    """

    def test_compromised(self):
        """
        Compromised passwords raise ValidationError.

        """
        validator = PwnedPasswordsValidator(
            api_client=api.PwnedPasswords(client=self.http_client())
        )
        with self.assertRaisesMessage(
            ValidationError, str(validator.error_message["singular"])
        ):
            validator.validate(self.sample_password)

    def test_not_compromised(self):
        """
        Non-compromised passwords don't raise ValidationError.

        """
        suffix = self.sample_password_suffix.replace("A", "3")
        validator = PwnedPasswordsValidator(
            api_client=api.PwnedPasswords(client=self.http_client(suffix=suffix))
        )
        validator.validate(self.sample_password)

    @override_settings(
        AUTH_PASSWORD_VALIDATORS=[
            {
                "NAME": "pwned_passwords_django.validators.PwnedPasswordsValidator",
                "OPTIONS": {"error_message": "Pwned"},
            }
        ]
    )
    def test_message_override(self):
        """
        Custom messages are honored.

        """
        error_message = "Pwned"
        validator = PwnedPasswordsValidator(
            error_message=error_message,
            api_client=api.PwnedPasswords(client=self.http_client()),
        )
        with self.assertRaisesMessage(ValidationError, "Pwned"):
            validator.validate(self.sample_password)

    @override_settings(
        AUTH_PASSWORD_VALIDATORS=[
            {
                "NAME": "pwned_passwords_django.validators.PwnedPasswordsValidator",
                "OPTIONS": {
                    "error_message": ("Pwned %(amount)d time", "Pwned %(amount)d times")
                },
            }
        ]
    )
    def test_message_number(self):
        """
        Custom messages can include the count of breaches.

        """
        for count in range(1, 10):
            error_message = ("Pwned %(amount)d time", "Pwned %(amount)d times")
            expected_message = (
                f"Pwned {count} times" if count > 1 else f"Pwned {count} time"
            )
            validator = PwnedPasswordsValidator(
                error_message=error_message,
                api_client=api.PwnedPasswords(client=self.http_client(count=count)),
            )
            with self.assertRaisesMessage(ValidationError, expected_message):
                validator.validate(self.sample_password)

    def test_http_error_fallback_common_password_validator(self):
        """
        In the event of a Pwned Passwords API failure,
        PwnedPasswordsValidator falls back to CommonPasswordValidator.

        """
        validator = PwnedPasswordsValidator(
            error_message="Pwned",
            api_client=api.PwnedPasswords(
                client=self.exception_client(
                    exception_class=httpx.ConnectTimeout, message="Timed out"
                )
            ),
        )
        try:
            validator.validate("password")
        except ValidationError as exc:
            error = exc.error_list[0]
            # The raised error should have the message and code of the
            # CommonPasswordValidator, not the message (overridden) and code of the
            # PwnedPasswordsValidator.
            self.assertEqual(error.message, "This password is too common.")
            assert error.code == "password_too_common"
        else:
            # If no validation error was raised, that's a failure.
            assert False  # noqa: B011

    def test_get_help_text_matches_django(self):
        """
        The validator's help text is identical to the help text of Django's
        CommonPasswordValidator.

        """
        assert (
            PwnedPasswordsValidator().get_help_text()
            == CommonPasswordValidator().get_help_text()
        )

    def test_deconstruct(self):
        """
        The validator correctly deconstructs itself for serialization in migrations.

        """
        error_message = "Pwned"
        help_message = "Help text"
        validator = PwnedPasswordsValidator(
            error_message=error_message, help_message=help_message
        )
        assert validator.deconstruct() == (
            "pwned_passwords_django.validators.PwnedPasswordsValidator",
            (),
            {
                "help_message": help_message,
                "error_message": {"singular": error_message, "plural": error_message},
            },
        )

    def test_serializable(self):
        """
        The equality checking implemented for serializing the validator in
        migrations is correct.

        """
        validator_1 = PwnedPasswordsValidator()
        validator_2 = PwnedPasswordsValidator(error_message="Oops!")
        validator_3 = PwnedPasswordsValidator(help_message="Help")
        validator_4 = PwnedPasswordsValidator(
            error_message="Oops!", help_message="Help"
        )
        validator_5 = PwnedPasswordsValidator(
            error_message="Oops!", help_message="Help"
        )

        for first, second in (
            (validator_1, validator_1),
            (validator_2, validator_2),
            (validator_3, validator_3),
            (validator_4, validator_4),
            (validator_5, validator_5),
            (validator_4, validator_5),
        ):
            assert first == second

        for first, second in (
            (validator_1, validator_2),
            (validator_1, validator_3),
            (validator_1, validator_4),
            (validator_1, validator_5),
            (validator_1, object()),
            (validator_2, validator_3),
            (validator_2, validator_4),
            (validator_2, validator_5),
            (validator_3, validator_4),
            (validator_3, validator_5),
        ):
            assert first != second
