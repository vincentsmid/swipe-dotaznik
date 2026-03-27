from fastapi.routing import APIRouter

from julca_bakalarka.web.api import admin, docs, monitoring, survey

api_router = APIRouter()
api_router.include_router(monitoring.router)
api_router.include_router(docs.router)
api_router.include_router(survey.router, prefix="/survey", tags=["survey"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
