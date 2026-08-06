"""Business-rule validation helpers for auth input payloads.

Validation is deliberately implemented with the standard library plus pydantic's
``EmailStr`` so no third-party validation dependencies (zxcvbn, libphonenumber)
are required. The rules live here so they can be reused by usecases and tested
in isolation.
"""

from __future__ import annotations

import re

from src.core.settings import settings
from src.domain.exceptions import ValidationError

_PHONE_RE = re.compile(r"^\+[1-9][0-9]{6,14}$")


def validate_email(email: str | None) -> None:
    """Ensure the email is a syntactically valid address.

    A missing email or a clearly malformed one (e.g. ``test@``) is rejected.
    """
    if not email or "@" not in email:
        raise ValidationError("email is required and must be a valid address")
    from pydantic import EmailStr

    try:
        EmailStr._validate(email)
    except Exception as exc:
        raise ValidationError("email is not a valid address") from exc


def validate_password(password: str | None) -> None:
    """Enforce length and complexity rules for passwords."""
    if not password:
        raise ValidationError("password is required")

    if len(password) < settings.PASSWORD_MIN_LENGTH:
        raise ValidationError(
            f"password must be at least {settings.PASSWORD_MIN_LENGTH} characters"
        )

    if len(password) > settings.PASSWORD_MAX_LENGTH:
        raise ValidationError(
            f"password must be at most {settings.PASSWORD_MAX_LENGTH} characters"
        )

    if not re.search(r"[A-Za-z]", password) or not re.search(r"[0-9]", password):
        raise ValidationError("password must contain both letters and digits")


def validate_phone(phone: str | None) -> None:
    """Validate an optional phone number (``+`` followed by 7-15 digits)."""
    if not phone:
        return
    if not _PHONE_RE.fullmatch(phone):
        raise ValidationError(
            "phone must be in international format, e.g. +79990000000"
        )


def validate_signup_input(
    email: str | None, phone: str | None, password: str | None
) -> None:
    """Run all signup validations."""
    validate_email(email)
    validate_password(password)
    validate_phone(phone)
