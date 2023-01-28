import contextlib
import typing

from limits import parse
from limits.aio.storage import MemoryStorage, Storage
from limits.aio.strategies import MovingWindowRateLimiter


class RateLimitError(Exception):
    ...


class RateLimited(RateLimitError):
    error_code = "rate_limited"


class RateLimiter:
    def __init__(self, namespace: str, limit: str, storage: Storage | None = None) -> None:
        self.limit = parse(limit)
        self.namespace = namespace

        self._storage = storage or MemoryStorage()
        self.limiter = MovingWindowRateLimiter(self._storage)

    async def hit(self, key: str) -> None:
        await self.limiter.hit(self.limit, self.namespace, key)

    async def reset(self, key: str) -> None:
        await self.limiter.clear(self.limit, self.namespace, key)

    async def is_rate_limited(self, key: str) -> bool:
        return not await self.limiter.test(self.limit, self.namespace, key)


memory_storage = MemoryStorage()


@contextlib.asynccontextmanager
async def with_rate_limit(
    key: str,
    message: str,
    namespace: str,
    limit: str,
) -> typing.AsyncGenerator[RateLimiter, None]:
    """
    Enforce rate limit check for a code block.

    :param key: Unique identity or resource to protect.
    :param message: Message to use as exception text
    :param namespace: Context where rate limiter is used. E.g. login, password recovery.
    :param limit: Rate limit spec. Example: 10/minute
    :raise RateLimited:
    :return: RateLimiter
    """
    limiter = RateLimiter(namespace, limit, storage=memory_storage)
    if await limiter.is_rate_limited(key):
        raise RateLimited(message)

    await limiter.hit(key)
    yield limiter
