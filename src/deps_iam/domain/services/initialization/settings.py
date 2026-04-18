from pydantic_settings import BaseSettings, SettingsConfigDict

__all__ = ["Settings"]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="SETUP_")

    tenant: str
    users_invites_path: str  # Path to the json file with list of users. User fields: firstName, lastName, email.
