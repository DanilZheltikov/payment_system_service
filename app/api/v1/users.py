from fastapi import APIRouter

from app.crud import account_crud, payment_crud
from app.dependencies import CurrentUserDep, SessionDep
from app.schemas import AccountRead, PaymentRead, UserRead


router = APIRouter()


@router.get('/', response_model=UserRead)
async def read_current_user(current_user: CurrentUserDep):
    """Запрос данных текущего пользователя."""

    return current_user


@router.get('/accounts', response_model=list[AccountRead])
async def get_my_accounts(
    current_user: CurrentUserDep,
    session: SessionDep,
    limit: int = 10,
    offset: int = 0
):
    """Запрос всех счетов текущего пользователя."""

    return await account_crud.get_multi_by_user(
        current_user.id,
        session,
        limit,
        offset
    )


@router.get('/payments', response_model=list[PaymentRead])
async def get_my_payments(
    current_user: CurrentUserDep,
    session: SessionDep,
    limit: int = 10,
    offset: int = 0
):
    """Запрос всех платежей текущего пользователя."""

    return await payment_crud.get_multi_by_user(
        current_user.id,
        session,
        limit,
        offset
    )
