import importlib
import os
import pathlib
import sys
import typing
from pathlib import Path

from dotenv import load_dotenv
from kupala.config import Secrets
from pydantic import BaseModel, Field, Json, PostgresDsn
from pydantic.env_settings import BaseSettings

package_name = __name__.split(".")[0]
package_root = Path(str(importlib.import_module(package_name).__file__)).parent
project_root = package_root.parent

env_file = project_root / ".env"
if env_file.exists():
    load_dotenv(env_file)

IS_TESTING = "pytest" in sys.argv[0]
ENV = os.environ.get("APP_ENV", "test" if IS_TESTING else "production")
SECRETS_DIR = {"local": "_local/secrets"}.get(ENV, "/run/secrets")

secret = Secrets(SECRETS_DIR)


class AppSettings(BaseModel):
    secret_key: str = secret("secret_key.secret", "")
    debug: bool = False
    environment: str = ENV
    base_url: str = "http://localhost:8000"
    app_name: str = "{{cookiecutter.project_name}}"
    project_root: Path = project_root
    package_dir: Path = package_root
    package_name: str = package_name
    upload_dir: str | os.PathLike = project_root / "uploads"

    class Config:
        arbitrary_types_allowed = True


class ReleaseSettings(BaseModel):
    release_id: str = ""


class SessionSettings(BaseModel):
    lifetime: int = 3600 * 24


class RedisSettings(BaseModel):
    redis_url: str = secret("redis_url.secret", "redis://")


class DatabaseSettings(BaseModel):
    database_url: PostgresDsn = secret(
        "database_url.secret", "postgresql+asyncpg://postgres:postgres@localhost/{{cookiecutter.project_name}}"
    )
    echo: bool = False
    pool_size: int = 5
    pool_max_overflow: int = 10
    pool_timeout: int = 30

    @property
    def sync_database_url(self) -> str:
        return self.database_url.replace("+asyncpg", "")


class LocalizationSettings(BaseModel):
    language: str = "en"
    timezone: str = "UTC"
    languages: Json[list[str]] = Field(default_factory=lambda: ["en"])


class MailSettings(BaseModel):
    url: str = secret("email_url.secret", "smtp://localhost:1025")
    from_name: str = "Example"
    from_email: str = "info@example.com"


class SecuritySettings(BaseModel):
    post_login_redirect_path = "home-redirect"
    login_rate_limit = "10/minute"
    password_reset_rate_limit = "10/minute"
    password_reset_token_lifetime = 60 * 60  # 1h
    remember_me_duration = 3600 * 24 * 14  # 14 days
    trusted_hosts: Json[list[str]] = Field(default_factory=lambda: ["*"])

    registration_rate_limit = "3/minute"


class SentrySettings(BaseModel):
    dsn: str = secret("sentry_url.secret", "")
    traces_sample_rate: float = 0.1


class LocalStorageSettings(BaseModel):
    directory: str | pathlib.Path = project_root / "uploads"
    base_url: str = ""


class S3StorageSettings(BaseModel):
    bucket_name: str
    aws_access_key_id: str | None = None
    aws_secret_access_key: str | None = None
    region_name: str = "eu-central-1"
    endpoint_url: str | None = None
    signed_link_ttl: int = 300


class StorageSettings(BaseModel):
    default: typing.Literal["local", "s3"] = "local"
    local = LocalStorageSettings()
    s3 = S3StorageSettings(
        bucket_name="uploads.{{cookiecutter.project_name}}.io",
        region_name="eu-central-1",
        signed_link_ttl=300,
        aws_access_key_id=os.environ.get("APP_STORAGE_UPLOADS_AWS_ACCESS_KEY", ""),
        aws_secret_access_key=secret(
            "aws_secret_access_key.secret",
            os.environ.get("APP_STORAGE_UPLOADS_AWS_SECRET_KEY", ""),
        ),
    )

    class Config:
        arbitrary_types_allowed = True


class SocialSettings(BaseModel):
    google_client_id: str = "487962909894-j24dnl4t1i8rq7jfl3mdhj2qd1b8imvp.apps.googleusercontent.com"
    google_client_secret: str = secret("google_oauth_client_secret.secret", "")


class Settings(BaseSettings, AppSettings):
    database = DatabaseSettings()
    sentry = SentrySettings()
    release = ReleaseSettings()
    security = SecuritySettings()
    mail = MailSettings()
    localization = LocalizationSettings()
    session = SessionSettings()
    redis = RedisSettings()
    storages = StorageSettings()
    social = SocialSettings()

    class Config:
        frozen = True
        env_file = ".env"
        env_prefix = "APP_"
        env_nested_delimiter = "__"
        secrets_dir = SECRETS_DIR


def new_settings(**overrides: typing.Any) -> Settings:
    return Settings(**overrides)


def new_settings_for_test() -> Settings:
    test_database_url = "postgresql+asyncpg://postgres:postgres@localhost/{{cookiecutter.project_name}}_test"
    return new_settings(
        debug=True,
        environment="test",
        mail=MailSettings(url="memory://"),
        database=DatabaseSettings(database_url=test_database_url),
        security=SecuritySettings(
            registration_rate_limit="1000/second",
        ),
    )


settings = new_settings_for_test() if IS_TESTING else new_settings()


def get_settings() -> Settings:
    """Get current application settings."""
    return settings
