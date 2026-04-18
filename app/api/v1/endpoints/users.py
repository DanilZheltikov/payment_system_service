from typing import List

from fastapi import APIRouter

from app.crud import account_crud, payment_crud
from app.dependencies import CurrentUserDep, SessionDep
from app.schemas import AccountSchema, PaymentRead, UserRead


router = APIRouter()


@router.get('/', response_model=UserRead)
async def read_current_user(current_user: CurrentUserDep):
    return current_user


@router.get('/accounts', response_model=List[AccountSchema])
async def get_my_accounts(current_user: CurrentUserDep, session: SessionDep):
    return await account_crud.get_accounts_by_user(current_user, session)


@router.get('/payments', response_model=PaymentRead)
async def get_my_payments(current_user: CurrentUserDep, session: SessionDep):
    return await payment_crud.get_payments_by_user(current_user, session)
