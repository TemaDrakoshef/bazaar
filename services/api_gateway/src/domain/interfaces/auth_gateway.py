from abc import ABC, abstractmethod

from src.domain.dtos.auth import (
    AuthTokens,
    LoginInput,
    LogoutInput,
    RefreshInput,
    SignUpInput,
    TokenStatus,
    ValidateTokenInput,
)


class AbstractAuthGateway(ABC):
    """Port for every auth operation the gateway performs."""

    @abstractmethod
    async def sign_up(self, data: SignUpInput) -> AuthTokens: ...

    @abstractmethod
    async def login(self, data: LoginInput) -> AuthTokens: ...

    @abstractmethod
    async def logout(self, data: LogoutInput) -> None: ...

    @abstractmethod
    async def refresh(self, data: RefreshInput) -> AuthTokens: ...

    @abstractmethod
    async def validate_token(self, data: ValidateTokenInput) -> TokenStatus: ...
