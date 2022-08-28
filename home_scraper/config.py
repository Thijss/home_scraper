# pylint: disable=no-self-argument,too-few-public-methods
from enum import IntEnum
from pathlib import Path

from pydantic import BaseModel, BaseSettings, root_validator, validator

from home_scraper.storage.enums import StorageMode

_BASE_DIR = Path(__file__).parent.parent
_RESULTS_DIR = _BASE_DIR / "results"


class AwsConfig(BaseModel):
    iam_access_key_id: str
    iam_secret_access_key: str
    bucket_name: str = "home-scraper"


class DataSource(IntEnum):
    LOCAL = 1
    WEB = 2


class StorageConfig(BaseModel):
    mode: StorageMode = StorageMode.LOCAL
    aws: AwsConfig | None = None

    @validator("mode", pre=True)
    def validate_mode(cls, value):
        if isinstance(value, str):
            return StorageMode[value.upper()]
        return value

    @property
    def storage_dir(self):
        if self.mode == StorageMode.AWS:
            return _RESULTS_DIR / "aws"
        return _RESULTS_DIR / "local"


class SlackConfig(BaseModel):
    bot_token: str
    channel: str = "eigenhaard"


class Settings(BaseSettings):
    slack: SlackConfig | None = None
    storage: StorageConfig
    data_source: DataSource

    class Config:
        env_file = _BASE_DIR / ".env"
        env_file_encoding = "utf-8"
        env_nested_delimiter = "__"
        allow_population_by_field_name = True

    @property
    def base_dir(self):
        return _BASE_DIR

    @validator("data_source", pre=True)
    def validate_data_source(cls, value):
        if isinstance(value, str):
            return DataSource[value.upper()]
        return value

    @root_validator
    def check_congruent_storage_mode(cls, values):
        storage = values.get("storage")
        if storage and storage.mode == StorageMode.AWS and storage.aws is None:
            raise ValueError(
                f"{storage.mode.repr()} requires configured {AwsConfig.__name__}"
            )
        return values


settings = Settings()
