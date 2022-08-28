# pylint: disable=no-self-argument,too-few-public-methods
from pathlib import Path

from pydantic import BaseModel, BaseSettings, root_validator, validator

from home_scraper.config.enums import DataSource
from home_scraper.config._helpers import convert_enum
from home_scraper.storage.enums import StorageLocation

_BASE_DIR = Path(__file__).parent.parent.parent
_RESULTS_DIR = _BASE_DIR / "results"


class AwsConfig(BaseModel):
    iam_access_key_id: str
    iam_secret_access_key: str
    bucket_name: str = "home-scraper"


class StorageConfig(BaseModel):
    mode: StorageLocation = StorageLocation.LOCAL
    aws: AwsConfig | None = None

    @validator("mode", pre=True)
    def validate_mode(cls, value):
        return convert_enum(value, StorageLocation)

    @property
    def results_dir(self):
        return _BASE_DIR / "results"


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
        return convert_enum(value, DataSource)

    @root_validator
    def check_congruent_storage_mode(cls, values):
        storage = values.get("storage")
        if storage and storage.mode == StorageLocation.S3 and storage.aws is None:
            raise ValueError(
                f"{storage.mode.repr()} requires configured {AwsConfig.__name__}"
            )
        return values


settings = Settings()
