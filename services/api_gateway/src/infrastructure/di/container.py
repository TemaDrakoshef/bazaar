from collections.abc import AsyncIterable

from dishka import Provider, Scope, provide

from src.application.use_cases.auth.login import LoginUseCase
from src.application.use_cases.auth.logout import LogoutUseCase
from src.application.use_cases.auth.refresh import RefreshUseCase
from src.application.use_cases.auth.signup import SignUpUseCase
from src.application.use_cases.auth.validate_token import ValidateTokenUseCase
from src.application.use_cases.catalog.create_category import CreateCategoryUseCase
from src.domain.interfaces.auth_gateway import AbstractAuthGateway
from src.domain.interfaces.catalog_gateway import AbstractCatalogGateway
from src.infrastructure.config.settings import Settings
from src.infrastructure.grpc.auth_client import AuthClient
from src.infrastructure.grpc.catalog_client import CatalogClient
from src.infrastructure.grpc.channels import Channels


class ApiGatewayProvider(Provider):
    @provide(scope=Scope.APP)
    def provide_settings(self) -> Settings:
        return Settings()

    @provide(scope=Scope.APP)
    async def provide_channels(self, settings: Settings) -> AsyncIterable[Channels]:
        channels = Channels(settings)
        try:
            yield channels
        finally:
            await channels.close()

    @provide(scope=Scope.APP)
    def provide_auth_gateway(self, channels: Channels) -> AbstractAuthGateway:
        return AuthClient(channels.auth)

    @provide(scope=Scope.APP)
    def provide_catalog_gateway(self, channels: Channels) -> AbstractCatalogGateway:
        return CatalogClient(channels.catalog)

    @provide(scope=Scope.REQUEST)
    def provide_signup_use_case(self, auth: AbstractAuthGateway) -> SignUpUseCase:
        return SignUpUseCase(auth)

    @provide(scope=Scope.REQUEST)
    def provide_login_use_case(self, auth: AbstractAuthGateway) -> LoginUseCase:
        return LoginUseCase(auth)

    @provide(scope=Scope.REQUEST)
    def provide_logout_use_case(self, auth: AbstractAuthGateway) -> LogoutUseCase:
        return LogoutUseCase(auth)

    @provide(scope=Scope.REQUEST)
    def provide_refresh_use_case(self, auth: AbstractAuthGateway) -> RefreshUseCase:
        return RefreshUseCase(auth)

    @provide(scope=Scope.REQUEST)
    def provide_validate_token_use_case(
        self, auth: AbstractAuthGateway
    ) -> ValidateTokenUseCase:
        return ValidateTokenUseCase(auth)

    @provide(scope=Scope.REQUEST)
    def provide_create_category_use_case(
        self, catalog: AbstractCatalogGateway
    ) -> CreateCategoryUseCase:
        return CreateCategoryUseCase(catalog)
