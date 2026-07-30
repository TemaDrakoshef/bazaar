from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    project_name: str = "Bazaar API Gateway"
    project_version: str = "1.0.0"

    auth_service_host: str = "auth_service"
    auth_service_port: int = 50051

    user_service_host: str = "user_service"
    user_service_port: int = 50051

    @property
    def auth_address(self) -> str:
        return f"{self.auth_service_host}:{self.auth_service_port}"

    @property
    def user_address(self) -> str:
        return f"{self.user_service_host}:{self.user_service_port}"


settings = Settings()
