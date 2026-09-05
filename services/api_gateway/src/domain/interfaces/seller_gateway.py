from abc import ABC, abstractmethod

from src.domain.dtos.seller import (
    MerchantCreateInput,
    MerchantResult,
    VerifyAccessInput,
    VerifyAccessResult,
)


class AbstractSellerGateway(ABC):
    """Port for every seller operation the gateway performs."""

    @abstractmethod
    async def create_merchant(self, data: MerchantCreateInput) -> MerchantResult: ...

    @abstractmethod
    async def list_user_merchants(self, user_id: str) -> list[MerchantResult]: ...

    @abstractmethod
    async def verify_access(self, data: VerifyAccessInput) -> VerifyAccessResult: ...
