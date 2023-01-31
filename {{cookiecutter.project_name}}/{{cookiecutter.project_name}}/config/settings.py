import dataclasses
import importlib
import os
import pathlib
import sys
import typing
from pathlib import Path

from dotenv import load_dotenv
from kupala.config import Secrets
from starlette.config import Config

package_name = __name__.split(".")[0]
package_dir = Path(str(importlib.import_module(package_name).__file__)).parent
project_dir = package_dir.parent

env_file = project_dir / ".env"
if env_file.exists():
    load_dotenv(env_file)

config = Config()
secret = Secrets("/run/secrets")
IS_TESTING = "pytest" in sys.argv[0]
ENV = "test" if IS_TESTING else config('APP_ENV', default="production")


@dataclasses.dataclass(frozen=True)
class AppSettings:
    secret_key: str = secret("secret_key.secret", "")
    debug: bool = False
    environment: str = ENV
    base_url: str = "http://localhost:8000"
    app_name: str = "{{cookiecutter.project_name}}"
    project_dir: Path = project_dir
    package_dir: Path = package_dir
    package_name: str = package_name
    upload_dir: str | os.PathLike = project_dir / "uploads"


@dataclasses.dataclass(frozen=True)
class ReleaseSettings:
    release_id: str = config('APP_RELEASE_ID', default='')


@dataclasses.dataclass(frozen=True)
class SessionSettings:
    lifetime: int = 3600 * 24


@dataclasses.dataclass(frozen=True)
class RedisSettings:
    redis_url: str = secret("redis_url.secret", "redis://")


@dataclasses.dataclass(frozen=True)
class DatabaseSettings:
    database_url: str = secret("database_url.secret", "postgresql+asyncpg://postgres:postgres@localhost/{{cookiecutter.project_name}}")
    echo: bool = False
    pool_size: int = 5
    pool_max_overflow: int = 10
    pool_timeout: int = 30

    @property
    def sync_database_url(self) -> str:
        return self.database_url.replace("+asyncpg", "")


@dataclasses.dataclass(frozen=True)
class LocalizationSettings:
    language: str = "en"
    timezone: str = "UTC"
    languages: list[str] = dataclasses.field(default_factory=lambda: ["en"])


@dataclasses.dataclass(frozen=True)
class MailSettings:
    url: str = secret("email_url.secret", "smtp://localhost:1025")
    from_name: str = "Example"
    from_email: str = "info@example.com"


@dataclasses.dataclass(frozen=ENV != 'test')
class SecuritySettings:
    post_login_redirect_path: str = "home-redirect"
    login_rate_limit: str = "10/minute"
    password_reset_rate_limit: str = "10/minute"
    password_reset_token_lifetime: int = 60 * 60  # 1h
    remember_me_duration: int = 3600 * 24 * 14  # 14 days
    trusted_hosts: list[str] = dataclasses.field(default_factory=lambda: ["*"])
    registration_rate_limit: str = "3/minute"


@dataclasses.dataclass(frozen=True)
class SentrySettings:
    dsn: str = secret("sentry_url.secret", "")
    traces_sample_rate: float = 0.1


@dataclasses.dataclass(frozen=True)
class LocalStorageSettings:
    directory: str | pathlib.Path = project_dir / "uploads"
    base_url: str = ""


@dataclasses.dataclass(frozen=True)
class S3StorageSettings:
    bucket_name: str
    aws_access_key_id: str | None = None
    aws_secret_access_key: str | None = None
    region_name: str = "eu-central-1"
    endpoint_url: str | None = None
    signed_link_ttl: int = 300


@dataclasses.dataclass(frozen=True)
class StorageSettings:
    default: typing.Literal["local", "s3"] = "local"
    local: LocalizationSettings = LocalStorageSettings()
    s3: S3StorageSettings = S3StorageSettings(
        bucket_name="uploads.{{cookiecutter.project_name}}.io",
        region_name="eu-central-1",
        signed_link_ttl=300,
        aws_access_key_id=os.environ.get("APP_STORAGE_UPLOADS_AWS_ACCESS_KEY", ""),
        aws_secret_access_key=secret(
            "aws_secret_access_key.secret",
            os.environ.get("APP_STORAGE_UPLOADS_AWS_SECRET_KEY", ""),
        ),
    )


@dataclasses.dataclass(frozen=True)
class SocialSettings:
    google_client_id: str = ""
    google_client_secret: str = secret("google_oauth_client_secret.secret", "")


@dataclasses.dataclass(frozen=True)
class Settings(AppSettings):
    database: DatabaseSettings = DatabaseSettings()
    sentry: SentrySettings = SentrySettings()
    release: ReleaseSettings = ReleaseSettings()
    security: SecuritySettings = SecuritySettings()
    mail: MailSettings = MailSettings()
    localization: LocalizationSettings = LocalizationSettings()
    session: SessionSettings = SessionSettings()
    redis: RedisSettings = RedisSettings()
    storages: StorageSettings = StorageSettings()
    social: SocialSettings = SocialSettings()


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
