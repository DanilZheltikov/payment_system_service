from fastapi import APIRouter, Depends

from app.dependencies import CurrentUserDep, get_current_superuser, SessionDep
from app.crud.user import user_crud
from app.schemas.user import UserRead, UserCreate, UserUpdate
from app.service.user import user_create_service

router = APIRouter()


@router.patch(
    '/{user_id}',
    response_model=UserRead,
    dependencies=[Depends(get_current_superuser)]
)
async def update(
    user_id: int,
    obj_in: UserUpdate,
    session: SessionDep
):
    user = await user_crud.get(user_id, session)
    updated_user = await user_crud.update(user, obj_in, session)
    return updated_user


@router.delete(
    '/{user_id}',
    response_model=UserRead,
    dependencies=[Depends(get_current_superuser)]
)
async def remove_user(
    user_id: int,
    session: SessionDep
):
    user = await user_crud.get(user_id, session)
    user = await user_crud.remove(user, session)
    return user


@router.get('/me', response_model=UserRead)
async def read_current_user(
    current_user: CurrentUserDep
):
    return current_user


@router.post(
    '/create',
    response_model=UserRead,
    dependencies=[Depends(get_current_superuser)]
)
async def create_user(user: UserCreate, session: SessionDep):
    return await user_create_service(user_in=user, session=session)
