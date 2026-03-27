from pathlib import Path

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from julca_bakalarka.db.dao.question_dao import QuestionDAO
from julca_bakalarka.web.api.admin.auth import verify_admin

APP_ROOT = Path(__file__).parent.parent.parent

router = APIRouter(dependencies=[Depends(verify_admin)])
templates = Jinja2Templates(directory=str(APP_ROOT / "templates"))


@router.get("/admin", response_class=HTMLResponse)
async def admin_dashboard(request: Request) -> HTMLResponse:
    """Render the admin dashboard."""
    dao = QuestionDAO()
    questions = await dao.get_all_ordered()
    return templates.TemplateResponse(
        request=request,
        name="admin/dashboard.html",
        context={"questions": questions},
    )


@router.get("/admin/questions/new", response_class=HTMLResponse)
async def admin_question_new(request: Request) -> HTMLResponse:
    """Render the new question form."""
    return templates.TemplateResponse(
        request=request,
        name="admin/question_form.html",
        context={"question": None},
    )


@router.get("/admin/questions/{question_id}/edit", response_class=HTMLResponse)
async def admin_question_edit(
    request: Request,
    question_id: int,
) -> HTMLResponse:
    """Render the edit question form."""
    dao = QuestionDAO()
    question = await dao.get_by_id(question_id)
    return templates.TemplateResponse(
        request=request,
        name="admin/question_form.html",
        context={"question": question},
    )
