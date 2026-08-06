"""Unit tests for the domain validation helpers."""

import pytest

from src.domain.exceptions import ValidationError
from src.domain.validation import (
    validate_email,
    validate_password,
    validate_phone,
    validate_signup_input,
)


@pytest.mark.parametrize(
    "email",
    [
        None,
        "",
        "test@",
        "plainaddress",
        "a b@example.com",
        "@example.com",
    ],
)
def test_validate_email_rejects_invalid(email):
    with pytest.raises(ValidationError):
        validate_email(email)


@pytest.mark.parametrize("email", ["user@example.com", "a+b@sub.domain.co"])
def test_validate_email_accepts_valid(email):
    validate_email(email)


@pytest.mark.parametrize(
    "password",
    [
        None,
        "",
        "short",
        "lettersonly",
        "12345678",
        "A" * 101,
    ],
)
def test_validate_password_rejects_invalid(password):
    with pytest.raises(ValidationError):
        validate_password(password)


@pytest.mark.parametrize(
    "password",
    ["S3cr3t-pass!", "abc12345", "LONGpass123", "alllowercase123", "mixed C4s3! 1"],
)
def test_validate_password_accepts_valid(password):
    validate_password(password)


@pytest.mark.parametrize(
    "phone",
    ["12", "12345", "phone-number", "abc", "+123456"],
)
def test_validate_phone_rejects_invalid(phone):
    with pytest.raises(ValidationError):
        validate_phone(phone)


@pytest.mark.parametrize("phone", [None, "", "+79990000000", "+15551234567"])
def test_validate_phone_accepts_valid(phone):
    validate_phone(phone)


def test_validate_signup_input_runs_all_rules():
    with pytest.raises(ValidationError):
        validate_signup_input("bad", "+79990000000", "S3cr3t-pass!")
    validate_signup_input("user@example.com", "+79990000000", "S3cr3t-pass!")
