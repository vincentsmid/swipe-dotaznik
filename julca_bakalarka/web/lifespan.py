from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from julca_bakalarka.settings import settings


@asynccontextmanager
async def lifespan_setup(
    app: FastAPI,
) -> AsyncGenerator[None]:  # pragma: no cover
    """
    Actions to run on application startup.

    This function uses fastAPI app to store data
    in the state, such as db_engine.

    :param app: the fastAPI application.
    :return: function that actually performs actions.
    """
    # Ensure media directory exists.
    settings.media_dir.mkdir(parents=True, exist_ok=True)

    app.middleware_stack = None
    app.middleware_stack = app.build_middleware_stack()

    yield
