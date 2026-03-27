from collections.abc import AsyncGenerator
from typing import Any

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from piccolo.conf.apps import Finder
from piccolo.table import create_tables, drop_tables

from julca_bakalarka.web.application import get_app


@pytest.fixture(scope="session")
def anyio_backend() -> str:
    """
    Backend for anyio pytest plugin.

    :return: backend name.
    """
    return "asyncio"


@pytest.fixture(autouse=True)
async def setup_db() -> AsyncGenerator[None]:
    """
    Fixture to create all tables before test and drop them after.

    :yield: nothing.
    """
    tables = Finder().get_table_classes()
    create_tables(*tables, if_not_exists=True)

    yield

    drop_tables(*tables)


@pytest.fixture
def fastapi_app() -> FastAPI:
    """
    Fixture for creating FastAPI app.

    :return: fastapi app with mocked dependencies.
    """
    application = get_app()
    return application  # noqa: RET504


@pytest.fixture
async def client(
    fastapi_app: FastAPI, anyio_backend: Any
) -> AsyncGenerator[AsyncClient]:
    """
    Fixture that creates client for requesting server.

    :param fastapi_app: the application.
    :yield: client for the app.
    """
    async with AsyncClient(
        transport=ASGITransport(fastapi_app), base_url="http://test", timeout=2.0
    ) as ac:
        yield ac
