from typing import ClassVar as _ClassVar, Optional as _Optional

from google.protobuf import descriptor as _descriptor, message as _message

DESCRIPTOR: _descriptor.FileDescriptor

class SignUpRequest(_message.Message):
    __slots__ = ("email", "phone", "password")
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    PHONE_FIELD_NUMBER: _ClassVar[int]
    PASSWORD_FIELD_NUMBER: _ClassVar[int]
    email: str
    phone: str
    password: str
    def __init__(
        self,
        email: _Optional[str] = ...,
        phone: _Optional[str] = ...,
        password: _Optional[str] = ...,
    ) -> None: ...

class SignUpResponse(_message.Message):
    __slots__ = ("access_token", "refresh_token")
    ACCESS_TOKEN_FIELD_NUMBER: _ClassVar[int]
    REFRESH_TOKEN_FIELD_NUMBER: _ClassVar[int]
    access_token: str
    refresh_token: str
    def __init__(
        self, access_token: _Optional[str] = ..., refresh_token: _Optional[str] = ...
    ) -> None: ...

class LoginRequest(_message.Message):
    __slots__ = ("email", "password")
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    PASSWORD_FIELD_NUMBER: _ClassVar[int]
    email: str
    password: str
    def __init__(
        self, email: _Optional[str] = ..., password: _Optional[str] = ...
    ) -> None: ...

class LoginResponse(_message.Message):
    __slots__ = ("access_token", "refresh_token")
    ACCESS_TOKEN_FIELD_NUMBER: _ClassVar[int]
    REFRESH_TOKEN_FIELD_NUMBER: _ClassVar[int]
    access_token: str
    refresh_token: str
    def __init__(
        self, access_token: _Optional[str] = ..., refresh_token: _Optional[str] = ...
    ) -> None: ...

class LogoutRequest(_message.Message):
    __slots__ = ("session_id",)
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    def __init__(self, session_id: _Optional[str] = ...) -> None: ...

class LogoutResponse(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class RefreshRequest(_message.Message):
    __slots__ = ("refresh_token",)
    REFRESH_TOKEN_FIELD_NUMBER: _ClassVar[int]
    refresh_token: str
    def __init__(self, refresh_token: _Optional[str] = ...) -> None: ...

class RefreshResponse(_message.Message):
    __slots__ = ("access_token",)
    ACCESS_TOKEN_FIELD_NUMBER: _ClassVar[int]
    access_token: str
    def __init__(self, access_token: _Optional[str] = ...) -> None: ...

class ValidateTokenRequest(_message.Message):
    __slots__ = ("access_token",)
    ACCESS_TOKEN_FIELD_NUMBER: _ClassVar[int]
    access_token: str
    def __init__(self, access_token: _Optional[str] = ...) -> None: ...

class ValidateTokenResponse(_message.Message):
    __slots__ = ("valid", "user_id", "error_message")
    VALID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    ERROR_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    valid: bool
    user_id: str
    error_message: str
    def __init__(
        self,
        valid: _Optional[bool] = ...,
        user_id: _Optional[str] = ...,
        error_message: _Optional[str] = ...,
    ) -> None: ...
