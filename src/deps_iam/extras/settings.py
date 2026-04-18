from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from .datasource import DBDialect, DBDriver

__all__ = ["AuthenticationSettings", "Settings", "ServiceInfoSettings", "DatabaseSettings"]


class AuthenticationSettings(BaseSettings):
    enabled: bool = Field(default=False, validation_alias="AUTH_ENABLED")
    verify_ssl: bool = Field(default=True, validation_alias="AUTH_VERIFY_SSL")
    certs_endpoint: str | None = Field(default=None, validation_alias="AUTH_CERTS_ENDPOINT")
    encryption_algorithm: str = Field(default="RS256", validation_alias="AUTH_ENCRYPTION_ALGORITHM")
    api_key: str | None = Field(default=None, validation_alias="API_KEY")

    @model_validator(mode="after")
    def validate_certs_endpoint_and_key(self) -> "AuthenticationSettings":
        inner_condition = self.certs_endpoint is None and self.api_key is None
        if self.enabled and inner_condition:
            raise ValueError(
                "Please provide OAUTH certificates endpoint via AUTH_CERTS_ENDPOINT or provide auth key via API_KEY"
            )

        return self


class ServiceInfoSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="SERVICE_INFO")

    tag: str = ""
    date: str = ""
    hash: str = ""


class Settings(BaseSettings):
    info: ServiceInfoSettings = ServiceInfoSettings()
    auth: AuthenticationSettings = AuthenticationSettings()
    ocr_api_url: str | None = Field(default=None)
    file_storage_url: str | None = Field(default=None)
    tables_api_url: str | None = Field(default=None)
    omr_service_url: str | None = Field(default=None)
    debug_mode: bool = Field(default=False)


class SSLSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="DATABASE_SSL")

    key: str = ""
    cert: str = ""
    rootcert: str = ""
    mode: str = "verify-full"


class DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="DATABASE_")

    user: str
    password: str
    host: str
    port: str
    db: str
    ssl: SSLSettings = SSLSettings()
    dialect: DBDialect = DBDialect.POSTGRES
    driver: DBDriver = DBDriver.PSYCOPG2
    require_secure_transport: bool = False
