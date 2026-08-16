from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    project_name: str = "Bazaar API Gateway"
    project_version: str = "1.0.0"

    auth_service_host: str = "auth_service"
    auth_service_port: int = 50051

    catalog_service_host: str = "catalog_service"
    catalog_service_port: int = 50052

    LOG_LEVEL: str = "INFO"
    ENVIRONMENT: str = "dev"

    otel_exporter_otlp_endpoint: str = "otel-collector:4317"

    @property
    def auth_address(self) -> str:
        return f"{self.auth_service_host}:{self.auth_service_port}"

    @property
    def catalog_address(self) -> str:
        return f"{self.catalog_service_host}:{self.catalog_service_port}"


settings = Settings()
