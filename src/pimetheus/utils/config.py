import os
import tomllib

import structlog
from pydantic import BaseModel, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

from pimetheus.infrastructure.storage.paths import ProjectPaths

logger = structlog.getLogger(__name__)

CONFIG_DIR = ProjectPaths.CONFIG
ENV_MODE: str = os.getenv("APP_ENV", "dev").lower()


class PimetheusSettings(BaseModel):
    """
    Runtime feature flags for the Pimetheus application.

    Attributes:
        offline (bool): If true, disables external API calls.
        emulation (bool): Enables simulated execution mode.
        twitter (bool): Enables posting to Twitter/X.
        bluesky (bool): Enables posting to Bluesky.
    """

    offline: bool = Field(default=False)
    emulation: bool = Field(default=False)
    twitter: bool = Field(default=False)
    bluesky: bool = Field(default=False)


class BlueskySettings(BaseSettings):
    """
    Configuration for Bluesky engagement behavior.

    Attributes:
        esa_handles (list[str]): ESA-related accounts used for engagement.
        space_handles (list[str]): Space-related accounts used for engagement.
    """

    esa_handles: list[str] = Field(default=[])
    space_handles: list[str] = Field(default=[])


class Settings(BaseSettings):
    """
    Application configuration loaded from environment variables and TOML files.

    Handles:
    - Secret credentials
    - Feature flags
    - External API configuration

    Methods:
        load(): Load configuration from TOML and environment variables.
    """

    model_config = SettingsConfigDict(
        env_file=str(CONFIG_DIR / f".env.{ENV_MODE}"), env_file_encoding="utf-8", extra="ignore"
    )

    # ENVIRONMENT SECRETS
    google_api_key: SecretStr = Field(default=SecretStr("default_google_api_key"))
    google_search_engine_id: SecretStr = Field(default=SecretStr("default_google_search_engine_id"))

    x_bearer_token: SecretStr = Field(default=SecretStr("default_x_bearer_token"))
    x_consumer_key: SecretStr = Field(default=SecretStr("default_x_api_key"))
    x_consumer_key_secret: SecretStr = Field(default=SecretStr("default_x_api_key_secret"))

    x_access_token: SecretStr = Field(default=SecretStr("default_x_access_token"))
    x_access_token_secret: SecretStr = Field(default=SecretStr("default_x_access_token_secret"))

    x_client_id: SecretStr = Field(default=SecretStr("default_x_client_id"))
    x_client_secret: SecretStr = Field(default=SecretStr("default_x_client_secret"))

    x_user_id: SecretStr = Field(default=SecretStr("default_x_user_id"))
    x_user_name: SecretStr = Field(default=SecretStr("default_x_user_name"))

    bluesky_consumer_key: SecretStr = Field(default=SecretStr("default_bluesky_api_key"))
    bluesky_consumer_key_secret: SecretStr = Field(default=SecretStr("default_bluesky_api_key_secret"))

    nasa_api_key: SecretStr = Field(default=SecretStr("default_nasa_api_key"))

    # APP Settings
    app_name: str = Field(default="package_name")

    # Nested APP Settings
    pimetheus: PimetheusSettings = Field(default_factory=PimetheusSettings)
    bluesky: BlueskySettings = Field(default_factory=BlueskySettings)

    @classmethod
    def load(cls) -> "Settings":
        """
        Load configuration from TOML file and environment variables.

        Returns:
            Settings: Application configuration instance.

        Notes:
            Falls back to defaults if TOML is missing or invalid.
        """

        config_path = CONFIG_DIR / f"config.{ENV_MODE}.toml"
        toml_data = {}

        if config_path.exists():
            try:
                with open(config_path, "rb") as f:
                    toml_data = tomllib.load(f)
            except (tomllib.TOMLDecodeError, PermissionError) as e:
                logger.warning("Failed to load TOML data, fallback to defaults", exc_info=e)
            except Exception as e:
                logger.warning("Unexpected error reading TOML, fallback to defaults", exc_info=e)
        else:
            logger.warning("Missing config file, fallback to defaults", path=config_path)

        try:
            return cls(**toml_data)
        except Exception as e:
            logger.warning("Failed to validate TOML data, fallback to defaults", error=str(e))
            return cls()
