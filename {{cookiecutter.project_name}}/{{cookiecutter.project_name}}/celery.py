import functools
import typing

import anyio
from celery import Celery
from kombu import Queue

from {{cookiecutter.project_name}}.config.settings import settings

task_packages = [
    settings.package_name,
]

scheduled_tasks: dict[str, typing.Any] = {}

task_routes: dict[str | typing.Pattern, typing.Any] = {}

task_queues: list[Queue] = []

app = Celery(
    set_as_current=True,
    broker=settings.redis.redis_url,
    task_routes=task_routes,
    task_queues=task_queues,
    timezone=settings.localization.timezone,
    result_backend=settings.redis.redis_url,
    result_expires=3600,  # 1h
    task_always_eager=settings.environment == "test",
    task_store_eager_result=False,
    task_ignore_result=False,
    task_time_limit=60 * 30,  # hard limit
    task_soft_time_limit=60 * 20,  # soft limit
    beat_schedule=scheduled_tasks,
    worker_max_tasks_per_child=1000,
)
app.autodiscover_tasks(packages=task_packages)

_PS = typing.ParamSpec("_PS")
_RT = typing.TypeVar("_RT")


def async_task(fn: typing.Callable[_PS, typing.Awaitable[_RT]]) -> typing.Callable[_PS, _RT]:
    @functools.wraps(fn)
    def decorator(*args: _PS.args, **kwargs: _PS.kwargs) -> _RT:
        async def main() -> _RT:
            return await fn(*args, **kwargs)

        return anyio.run(main)

    return decorator
