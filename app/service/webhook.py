from hashlib import sha256

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import (
    InvalidSignatureException,
    PaymentAlreadyProcessedException
)
from app.crud import account_crud, payment_crud, user_crud
from app.schemas import AccountCreate, PaymentWebhook


async def process_payment(
    payment: PaymentWebhook,
    session: AsyncSession,
) -> dict[str, str]:
    expected_sign = sha256(
        (
            f'{payment.account_id}'
            f'{payment.amount.normalize():f}'
            f'{payment.transaction_id}'
            f'{payment.user_id}'
            f'{settings.secret_key_to_webhook}'
        ).encode()
    ).hexdigest()
    if payment.signature != expected_sign:
        raise InvalidSignatureException()

    user = await user_crud.get_user_with_accounts(payment.user_id, session)
    account = {acc.id: acc for acc in user.accounts}.get(payment.account_id)

    if not account:
        account = await account_crud.create(
            obj_in=AccountCreate(
                id=payment.account_id,
                user_id=payment.user_id,
            ),
            session=session,
            commit=False,
            refresh=False
        )
    try:
        account.balance += payment.amount

        await payment_crud.create(
            payment,
            session,
            commit=False,
            refresh=False
        )
        await session.commit()

    except IntegrityError:
        await session.rollback()
        raise PaymentAlreadyProcessedException()

    return {'status': 'success'}
