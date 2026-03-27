from fastapi import Depends
from fastapi.routing import APIRouter

from julca_bakalarka.web.api.admin.auth import verify_admin
from julca_bakalarka.web.api.admin.views import router as admin_views_router

router = APIRouter(dependencies=[Depends(verify_admin)])
router.include_router(admin_views_router)
