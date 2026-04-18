from fastapi import APIRouter, Depends

from app.api.v1.endpoints import admin_router, auth_router, users_router
from app.dependencies import get_current_superuser

main_router = APIRouter()

main_router.include_router(
    auth_router,
    prefix='/auth',
    tags=['Authentication']
)

main_router.include_router(
    users_router,
    prefix='/me',
    tags=['Users']
)

main_router.include_router(
    admin_router,
    prefix='/admin/users',
    dependencies=[Depends(get_current_superuser)],
    tags=['Admin']
)
