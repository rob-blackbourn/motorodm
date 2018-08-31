import asyncio
import unittest
from unittest import mock
from functools import wraps


def AsyncMock(*args, **kwargs):
    """Create an async function mock."""
    m = mock.MagicMock(*args, **kwargs)

    async def mock_coro(*args, **kwargs):
        return m(*args, **kwargs)

    mock_coro.mock = m
    return mock_coro


def run_async(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        async def go():
            await func(*args, **kwargs)
        self = args[0]
        self.io_loop.run_until_complete(go())
    return wrapper
