import datetime

from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf import empty_pb2 as _empty_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable, Mapping as _Mapping
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ProductIdRequest(_message.Message):
    __slots__ = ("product_id",)
    PRODUCT_ID_FIELD_NUMBER: _ClassVar[int]
    product_id: int
    def __init__(self, product_id: _Optional[int] = ...) -> None: ...

class CategoryIdRequest(_message.Message):
    __slots__ = ("category_id",)
    CATEGORY_ID_FIELD_NUMBER: _ClassVar[int]
    category_id: int
    def __init__(self, category_id: _Optional[int] = ...) -> None: ...

class Product(_message.Message):
    __slots__ = ("id", "category_id", "title", "description", "price", "stock", "is_active", "created_at", "updated_at")
    ID_FIELD_NUMBER: _ClassVar[int]
    CATEGORY_ID_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    PRICE_FIELD_NUMBER: _ClassVar[int]
    STOCK_FIELD_NUMBER: _ClassVar[int]
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: int
    category_id: int
    title: str
    description: str
    price: int
    stock: int
    is_active: bool
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[int] = ..., category_id: _Optional[int] = ..., title: _Optional[str] = ..., description: _Optional[str] = ..., price: _Optional[int] = ..., stock: _Optional[int] = ..., is_active: _Optional[bool] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class CreateProductRequest(_message.Message):
    __slots__ = ("category_id", "title", "description", "price", "stock")
    CATEGORY_ID_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    PRICE_FIELD_NUMBER: _ClassVar[int]
    STOCK_FIELD_NUMBER: _ClassVar[int]
    category_id: int
    title: str
    description: str
    price: int
    stock: int
    def __init__(self, category_id: _Optional[int] = ..., title: _Optional[str] = ..., description: _Optional[str] = ..., price: _Optional[int] = ..., stock: _Optional[int] = ...) -> None: ...

class ListProductsRequest(_message.Message):
    __slots__ = ("limit", "offset")
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    limit: int
    offset: int
    def __init__(self, limit: _Optional[int] = ..., offset: _Optional[int] = ...) -> None: ...

class ListProductsResponse(_message.Message):
    __slots__ = ("products", "count")
    PRODUCTS_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    products: _containers.RepeatedCompositeFieldContainer[Product]
    count: int
    def __init__(self, products: _Optional[_Iterable[_Union[Product, _Mapping]]] = ..., count: _Optional[int] = ...) -> None: ...

class UpdateProductRequest(_message.Message):
    __slots__ = ("product_id", "category_id", "title", "description", "price", "stock", "is_active")
    PRODUCT_ID_FIELD_NUMBER: _ClassVar[int]
    CATEGORY_ID_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    PRICE_FIELD_NUMBER: _ClassVar[int]
    STOCK_FIELD_NUMBER: _ClassVar[int]
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    product_id: int
    category_id: int
    title: str
    description: str
    price: int
    stock: int
    is_active: bool
    def __init__(self, product_id: _Optional[int] = ..., category_id: _Optional[int] = ..., title: _Optional[str] = ..., description: _Optional[str] = ..., price: _Optional[int] = ..., stock: _Optional[int] = ..., is_active: _Optional[bool] = ...) -> None: ...

class Category(_message.Message):
    __slots__ = ("id", "name", "path", "is_active", "created_at", "updated_at", "parent_id")
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    PATH_FIELD_NUMBER: _ClassVar[int]
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    PARENT_ID_FIELD_NUMBER: _ClassVar[int]
    id: int
    name: str
    path: str
    is_active: bool
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    parent_id: int
    def __init__(self, id: _Optional[int] = ..., name: _Optional[str] = ..., path: _Optional[str] = ..., is_active: _Optional[bool] = ..., created_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[datetime.datetime, _timestamp_pb2.Timestamp, _Mapping]] = ..., parent_id: _Optional[int] = ...) -> None: ...

class CreateCategoryRequest(_message.Message):
    __slots__ = ("name", "parent_id")
    NAME_FIELD_NUMBER: _ClassVar[int]
    PARENT_ID_FIELD_NUMBER: _ClassVar[int]
    name: str
    parent_id: int
    def __init__(self, name: _Optional[str] = ..., parent_id: _Optional[int] = ...) -> None: ...

class ListCategoriesRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ListCategoriesResponse(_message.Message):
    __slots__ = ("categories",)
    CATEGORIES_FIELD_NUMBER: _ClassVar[int]
    categories: _containers.RepeatedCompositeFieldContainer[Category]
    def __init__(self, categories: _Optional[_Iterable[_Union[Category, _Mapping]]] = ...) -> None: ...

class UpdateCategoryRequest(_message.Message):
    __slots__ = ("category_id", "name", "is_active")
    CATEGORY_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    category_id: int
    name: str
    is_active: bool
    def __init__(self, category_id: _Optional[int] = ..., name: _Optional[str] = ..., is_active: _Optional[bool] = ...) -> None: ...

class MoveCategoryRequest(_message.Message):
    __slots__ = ("category_id", "parent_id")
    CATEGORY_ID_FIELD_NUMBER: _ClassVar[int]
    PARENT_ID_FIELD_NUMBER: _ClassVar[int]
    category_id: int
    parent_id: int
    def __init__(self, category_id: _Optional[int] = ..., parent_id: _Optional[int] = ...) -> None: ...
