from typing import Any

from deps_asb import ASBSettings
from deps_kafka import KafkaSettings
from deps_message_flow import MessagingDriverEnum
from deps_rabbitmq import RabbitMQTLSSettings
from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from deps_iam import constants
from deps_iam.extras.settings import (
    AuthenticationSettings as BaseAuthenticationSettings,
)
from deps_iam.extras.settings import DatabaseSettings, ServiceInfoSettings
from deps_iam.infrastructure.access_management.constants import AccessModeEnum
from deps_iam.infrastructure.constants import MessagingModeEnum


class AuthenticationSettings(BaseAuthenticationSettings):
    default_organisation: str = Field("deps-users")
    enable_personal_org: bool = Field(False, validation_alias="FEATURE_PERSONAL_ORG")  # noqa: WPS425
    api_key_auth_enabled: bool = Field(False, validation_alias="API_KEY_AUTH")  # noqa: WPS425
    access_mode: AccessModeEnum = AccessModeEnum.ORGANISATION
    userinfo_endpoint: str | None = Field(None)

    @field_validator("access_mode")
    @classmethod
    def validate_access_mode(cls, v, info):  # noqa: WPS110, N805
        if v != AccessModeEnum.ORGANISATION or not info.data.get("enabled"):
            raise ValueError("IAM service works only with organisation access mode and enabled authentication.")

        return v

    @field_validator("userinfo_endpoint")
    @classmethod
    def validate_userinfo_endpoint_and_key(cls, v, info):  # noqa: WPS110
        if info.data.get("api_key") is None and v is None:
            raise ValueError(
                "Please provide userinfo endpoint via `USERINFO_ENDPOINT` or provide auth key via `API_KEY`"
            )
        return v


class MessagingSettings(BaseSettings):
    messaging_mode: MessagingModeEnum = Field(MessagingModeEnum.broker)


class FeatureSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="FEATURE_")


class SMTPSettings(BaseSettings):
    host: str | None = Field(default=None, validation_alias="SMTP_HOST")
    port: int | None = Field(default=None, validation_alias="SMTP_PORT")
    login: str | None = Field(default=None, validation_alias="SMTP_LOGIN")
    password: str | None = Field(default=None, validation_alias="SMTP_PASSWORD")
    from_address: str = Field(default=constants.SMTP_DEFAULT_FROM, validation_alias="SMTP_FROM_ADDRESS")
    email_invitations_enabled: bool = Field(default=False, validation_alias="EMAIL_INVITATIONS_ENABLED")
    event_type: str = Field(default="generic_smtp_inbound", validation_alias="EMAIL_EVENT_TYPE")

    @model_validator(mode="after")
    def validate_vars_passed_if_invitations_enabled(self) -> "SMTPSettings":
        if not self.email_invitations_enabled:
            return self

        unset_vars = []
        for field_name, field_info in self.model_fields.items():
            if field_name not in {"from_address", "email_invitations_enabled"} and getattr(self, field_name) is None:
                env_name = str(field_info.validation_alias) if field_info.validation_alias else field_name.upper()
                unset_vars.append(env_name)

        if unset_vars:
            verb = "has" if len(unset_vars) == 1 else "have"
            message = f"Email invitations feature is enabled, but {', '.join(unset_vars)} {verb} not been provided"
            raise ValueError(message)

        return self


class CacheSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="CACHE_")

    ttl: int = Field(7200)  # noqa: WPS432
    maxsize: int = Field(100)
    enabled: bool = Field(default=False)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(use_enum_values=True)

    env: str
    version: str = "1.0"

    info: ServiceInfoSettings = ServiceInfoSettings()
    database: DatabaseSettings = DatabaseSettings()
    authentication: AuthenticationSettings = AuthenticationSettings()
    messaging: MessagingSettings = MessagingSettings()

    messaging_driver: MessagingDriverEnum = Field(MessagingDriverEnum.RABBITMQ)
    messaging_driver_settings: Any = Field(None)
    message_broker_connection_string: str
    rabbitmq_dlx_per_queue: bool = Field(False)  # noqa: WPS425

    documentation_enabled: bool = True
    instrumentation_enabled: bool = False
    default_customization_url: str | None = Field(None)

    features: FeatureSettings = FeatureSettings()

    smtp: SMTPSettings = SMTPSettings()
    external_url: str
    user_guide_link: str | None = None
    vpn_disclaimer: str | None = None

    cache_settings: CacheSettings = CacheSettings()

    logger_level: str = Field("INFO", validation_alias="LOG_LEVEL")

    @field_validator("messaging_driver_settings")
    @classmethod
    def validate_messaging_driver_settings(cls, v, info):  # noqa: N805, WPS110
        messaging_driver = info.data.get("messaging_driver")
        if not messaging_driver:
            raise ValueError("Invalid messaging driver")

        driver = MessagingDriverEnum(messaging_driver)
        if driver == MessagingDriverEnum.ASB:
            return ASBSettings()
        elif driver == MessagingDriverEnum.KAFKA:
            return KafkaSettings()
        elif driver == MessagingDriverEnum.RABBITMQ:
            return RabbitMQTLSSettings().model_dump()  # TODO: use BaseSettings

        raise ValueError(f"Driver {driver} is not implemented")
