import datetime

from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class MerchantStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    MERCHANT_STATUS_UNSPECIFIED: _ClassVar[MerchantStatus]
    MERCHANT_STATUS_ACTIVE: _ClassVar[MerchantStatus]
    MERCHANT_STATUS_PENDING_VERIFICATION: _ClassVar[MerchantStatus]

class MerchantRole(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    MERCHANT_ROLE_UNSPECIFIED: _ClassVar[MerchantRole]
    MERCHANT_ROLE_OWNER: _ClassVar[MerchantRole]
    MERCHANT_ROLE_MANAGER: _ClassVar[MerchantRole]
    MERCHANT_ROLE_VIEWER: _ClassVar[MerchantRole]
MERCHANT_STATUS_UNSPECIFIED: MerchantStatus
MERCHANT_STATUS_ACTIVE: MerchantStatus
MERCHANT_STATUS_PENDING_VERIFICATION: MerchantStatus
MERCHANT_ROLE_UNSPECIFIED: MerchantRole
MERCHANT_ROLE_OWNER: MerchantRole
MERCHANT_ROLE_MANAGER: MerchantRole
MERCHANT_ROLE_VIEWER: MerchantRole

class Merchant(_message.Message):
    __slots__ = ("id", "name", "inn", "owner_user_id", "status", "created_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    INN_FIELD_NUMBER: _ClassVar[int]
    OWNER_USER_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: int
    name: str
    inn: str
    owner_user_id: str
    status: MerchantStatus
    created_at: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[int] = ..., name: _Optional[str] = ..., inn: _Optional[str] = ..., owner_user_id: _Optional[str] = ..., status: _Optional[_Union[MerchantStatus, str]] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class MerchantMember(_message.Message):
    __slots__ = ("id", "merchant_id", "user_id", "role", "is_active")
    ID_FIELD_NUMBER: _ClassVar[int]
    MERCHANT_ID_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    id: int
    merchant_id: int
    user_id: str
    role: MerchantRole
    is_active: bool
    def __init__(self, id: _Optional[int] = ..., merchant_id: _Optional[int] = ..., user_id: _Optional[str] = ..., role: _Optional[_Union[MerchantRole, str]] = ..., is_active: _Optional[bool] = ...) -> None: ...

class CreateMerchantRequest(_message.Message):
    __slots__ = ("name", "inn", "user_id")
    NAME_FIELD_NUMBER: _ClassVar[int]
    INN_FIELD_NUMBER: _ClassVar[int]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    name: str
    inn: str
    user_id: str
    def __init__(self, name: _Optional[str] = ..., inn: _Optional[str] = ..., user_id: _Optional[str] = ...) -> None: ...

class GetMerchantRequest(_message.Message):
    __slots__ = ("merchant_id",)
    MERCHANT_ID_FIELD_NUMBER: _ClassVar[int]
    merchant_id: int
    def __init__(self, merchant_id: _Optional[int] = ...) -> None: ...

class ListUserMerchantsRequest(_message.Message):
    __slots__ = ("user_id",)
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    def __init__(self, user_id: _Optional[str] = ...) -> None: ...

class ListUserMerchantsResponse(_message.Message):
    __slots__ = ("merchants",)
    MERCHANTS_FIELD_NUMBER: _ClassVar[int]
    merchants: _containers.RepeatedCompositeFieldContainer[Merchant]
    def __init__(self, merchants: _Optional[_Iterable[_Union[Merchant, _Mapping]]] = ...) -> None: ...

class VerifyAccessRequest(_message.Message):
    __slots__ = ("user_id", "merchant_id")
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    MERCHANT_ID_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    merchant_id: int
    def __init__(self, user_id: _Optional[str] = ..., merchant_id: _Optional[int] = ...) -> None: ...

class VerifyAccessResponse(_message.Message):
    __slots__ = ("allowed", "role")
    ALLOWED_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    allowed: bool
    role: MerchantRole
    def __init__(self, allowed: _Optional[bool] = ..., role: _Optional[_Union[MerchantRole, str]] = ...) -> None: ...
