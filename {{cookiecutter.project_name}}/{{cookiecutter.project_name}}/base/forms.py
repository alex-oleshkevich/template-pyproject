import typing

import wtforms
from async_storages import FileStorage
from starlette.datastructures import FormData, UploadFile
from wtforms.utils import unset_value

from {{cookiecutter.project_name}}.base.storages import get_file_storage, upload_file


class AsyncFileField(wtforms.FileField):
    data: UploadFile | None

    def __init__(
        self,
        label: str | None = None,
        *,
        storage: FileStorage | None = None,
        upload_to: str = "uploads/{prefix}_{file_name}",
        **kwargs: typing.Any,
    ):
        self.storage = storage or get_file_storage()
        self.upload_to = upload_to
        self.should_delete = False
        super().__init__(label, **kwargs)

    def process(
        self,
        formdata: FormData | None,
        data: typing.Any = unset_value,
        extra_filters: list | None = None,
    ) -> None:
        if formdata:
            marker = "%s-delete" % self.name
            if marker in formdata:
                self.should_delete = True

        return super().process(formdata, data, extra_filters)  # noqa

    @property
    def file_uploaded(self) -> bool:
        return isinstance(self.data, UploadFile) and bool(self.data.filename)

    async def upload(self, extra_placeholders: dict[str, typing.Any] | None = None) -> str:
        if not self.data:
            raise ValueError("Field does not contain uploaded file.")
        extra_placeholders = extra_placeholders or {}
        return await upload_file(self.upload_to, self.data, self.storage, extra_placeholders)
