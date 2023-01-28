import typing

from async_storages import FileStorage, LocalStorage, S3Storage

from {{cookiecutter.project_name}}.config.settings import LocalStorageSettings, S3StorageSettings, settings

_storages: dict[str, FileStorage] = {}


def new_local_file_storage(config: LocalStorageSettings) -> FileStorage:
    return FileStorage(LocalStorage(config.directory, base_url=config.base_url, mkdirs=True))


def new_s3_file_storage(config: S3StorageSettings) -> FileStorage:
    assert config.aws_access_key_id
    assert config.aws_secret_access_key

    return FileStorage(
        S3Storage(
            bucket=config.bucket_name,
            aws_access_key_id=config.aws_access_key_id,
            aws_secret_access_key=config.aws_secret_access_key,
            region_name=config.region_name,
            endpoint_url=config.endpoint_url,
            signed_link_ttl=config.signed_link_ttl,
        )
    )


_factories: dict[type[LocalStorageSettings | S3StorageSettings], typing.Callable] = {
    LocalStorageSettings: new_local_file_storage,
    S3StorageSettings: new_s3_file_storage,
}


def get_file_storage(name: str = "__default__") -> FileStorage:
    if name not in _storages:
        name = settings.storages.default if name == "__default__" else name
        storage_config = getattr(settings.storages, name)
        factory = _factories[type(storage_config)]
        _storages[name] = factory(storage_config)
    return _storages[name]
