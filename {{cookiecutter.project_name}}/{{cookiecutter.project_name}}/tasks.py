import sys

from celery import shared_task

from {{cookiecutter.project_name}}.celery import async_task


@shared_task
@async_task
async def debug_task(message: str = "") -> None:
    sys.stdout.write(f"If you see this message in worker they it works. Message: {message}.")
