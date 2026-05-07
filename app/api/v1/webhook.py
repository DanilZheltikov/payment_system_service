from fastapi import APIRouter

from app.dependencies import SessionDep
from app.schemas import PaymentWebhook
from app.service.webhook import process_payment

router = APIRouter()


@router.post('/payment')
async def webhook_handle(
    payment: PaymentWebhook,
    session: SessionDep
) -> dict[str, str]:
    """Прием платежей."""
    return await process_payment(payment, session)
