from fastapi import APIRouter

from app.dependencies import CurrentUserDep
from app.schemas.user import UserRead

router = APIRouter()


@router.get('/me', response_model=UserRead)
async def read_current_user(
    current_user: CurrentUserDep
):
    return current_user
