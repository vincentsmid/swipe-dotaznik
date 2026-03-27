from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import UJSONResponse
from fastapi.staticfiles import StaticFiles

from julca_bakalarka.settings import settings
from julca_bakalarka.web.api.router import api_router
from julca_bakalarka.web.lifespan import lifespan_setup
from julca_bakalarka.web.pages.admin_pages import router as admin_pages_router
from julca_bakalarka.web.pages.survey_pages import router as survey_pages_router

APP_ROOT = Path(__file__).parent.parent


def get_app() -> FastAPI:
    """
    Get FastAPI application.

    This is the main constructor of an application.

    :return: application.
    """
    app = FastAPI(
        title="julca_bakalarka",
        lifespan=lifespan_setup,
        docs_url=None,
        redoc_url=None,
        openapi_url="/api/openapi.json",
        default_response_class=UJSONResponse,
    )

    # Main router for the API.
    app.include_router(router=api_router, prefix="/api")

    # HTML page routers.
    app.include_router(router=survey_pages_router)
    app.include_router(router=admin_pages_router)

    # Static files for docs, CSS, JS.
    app.mount("/static", StaticFiles(directory=APP_ROOT / "static"), name="static")
    # Media files (uploaded GIFs/videos).
    settings.media_dir.mkdir(parents=True, exist_ok=True)
    app.mount(
        "/media",
        StaticFiles(directory=settings.media_dir),
        name="media",
    )

    return app
