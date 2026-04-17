from typing import List

from fastapi import APIRouter

from app.crud.user import user_crud
from app.dependencies import SessionDep
from app.schemas.user import (
    UserRead,
    UserCreate,
    UserUpdate,
    UserWithAccountsRead
)
from app.service.user import user_create_service

router = APIRouter()


@router.patch('/{user_id}', response_model=UserRead)
async def update(
    user_id: int,
    obj_in: UserUpdate,
    session: SessionDep
):
    user = await user_crud.get(user_id, session)
    updated_user = await user_crud.update(user, obj_in, session)
    return updated_user


@router.delete('/{user_id}', response_model=UserRead)
async def remove_user(
    user_id: int,
    session: SessionDep
):
    user = await user_crud.get(user_id, session)
    user = await user_crud.remove(user, session)
    return user


@router.post('/create', response_model=UserRead)
async def create_user(user: UserCreate, session: SessionDep):
    return await user_create_service(user_in=user, session=session)


@router.get('/', response_model=List[UserWithAccountsRead])
async def get_users_with_accounts(
    session: SessionDep,
    limit: int = 10,
    offset: int = 0
):
    return await user_crud.get_all_users_with_accounts(limit, offset, session)


@router.get('/{user_id}', response_model=UserWithAccountsRead)
async def get_user_with_accounts(user_id: int, session: SessionDep):
    return await user_crud.get_user_with_accounts(user_id, session)
