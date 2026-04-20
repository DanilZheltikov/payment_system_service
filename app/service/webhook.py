from hashlib import sha256

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import (
    InvalidSignatureException,
    PaymentAlreadyProcessedException
)
from app.crud import account_crud, payment_crud, user_crud
from app.schemas import PaymentWebhook


async def process_payment(
    payment: PaymentWebhook,
    session: AsyncSession,
) -> dict[str, str]:
    secret_key = settings.secret_key_to_webhook
    amount_str = f'{payment.amount.normalize():f}'
    expected_sign = sha256(
        (
            f'{payment.account_id}'
            f'{amount_str}'
            f'{payment.transaction_id}'
            f'{payment.user_id}'
            f'{secret_key}'
        ).encode()
    ).hexdigest()
    if payment.signature != expected_sign:
        raise InvalidSignatureException()

    async with session.begin():
        user = await user_crud.get(payment.user_id, session)
        if await payment_crud.is_exists(payment.transaction_id, session):
            raise PaymentAlreadyProcessedException()

        account = await account_crud.get_or_create(
            user.id,
            payment.account_id,
            session
        )
        account.balance += payment.amount
        await payment_crud.create(payment, session)

    return {'status': 'success'}
