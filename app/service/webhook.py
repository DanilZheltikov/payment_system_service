from hashlib import sha256
from secrets import compare_digest

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import (
    InvalidSignatureException,
    PaymentAlreadyProcessedException
)
from app.crud import account_crud, payment_crud, user_crud
from app.schemas import PaymentCreate, PaymentWebhook


async def process_payment(
    payment: PaymentWebhook,
    session: AsyncSession,
) -> dict[str, str]:
    """Сервис обработки и валидации webhook'a."""

    if not compare_digest(payment.signature, _calculate_signature(payment)):
        raise InvalidSignatureException()

    await user_crud.get(payment.user_id, session)

    try:
        await payment_crud.create(
            PaymentCreate(**payment.model_dump(exclude={'signature'})),
            session,
            commit=False,
            refresh=False
        )
        account = await account_crud.get_or_create_with_lock(
            account_id=payment.account_id,
            user_id=payment.user_id,
            session=session
        )
        await account_crud.update_balance_atomic(
            account_id=account.id,
            amount=payment.amount,
            session=session
        )

    except IntegrityError as e:
        if _is_unique_violation(e):
            raise PaymentAlreadyProcessedException()
        raise

    return {'status': 'success'}


def _calculate_signature(payment: PaymentWebhook) -> str:
    """Вычисление ожидаемой подписи."""

    return sha256(
        (
            f'{payment.account_id}'
            f'{payment.amount:.2f}'
            f'{payment.transaction_id}'
            f'{payment.user_id}'
            f'{settings.secret_key_to_webhook}'
        ).encode()
    ).hexdigest()


def _is_unique_violation(error: IntegrityError) -> bool:
    """Определяем UNIQUE constraint violation."""
    orig = getattr(error, "orig", None)

    if orig:
        if hasattr(orig, 'sqlstate') and orig.sqlstate == '23505':
            return True
        if hasattr(orig, 'pgcode') and orig.pgcode == '23505':
            return True

    return False
