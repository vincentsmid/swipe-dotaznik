from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

APP_ROOT = Path(__file__).parent.parent.parent

router = APIRouter()
templates = Jinja2Templates(directory=str(APP_ROOT / "templates"))


@router.get("/", response_class=RedirectResponse)
async def root() -> str:
    """Redirect root to survey start."""
    return "/survey"


@router.get("/survey", response_class=HTMLResponse)
async def survey_start(request: Request) -> HTMLResponse:
    """Render the participant ID entry page."""
    return templates.TemplateResponse(request=request, name="survey/start.html")


@router.get("/survey/instructions", response_class=HTMLResponse)
async def survey_instructions(request: Request) -> HTMLResponse:
    """Render the instructions page."""
    return templates.TemplateResponse(request=request, name="survey/instructions.html")


@router.get("/survey/questions", response_class=HTMLResponse)
async def survey_questions(request: Request) -> HTMLResponse:
    """Render the question page (SPA shell)."""
    return templates.TemplateResponse(request=request, name="survey/question.html")


@router.get("/survey/done", response_class=HTMLResponse)
async def survey_done(request: Request) -> HTMLResponse:
    """Render the completion page."""
    return templates.TemplateResponse(request=request, name="survey/done.html")
