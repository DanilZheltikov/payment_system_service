from app.crud.base import UserRelatedBaseCRUD
from app.models import Payment
from app.schemas import PaymentCreate

payment_crud: UserRelatedBaseCRUD[Payment, PaymentCreate] = (
    UserRelatedBaseCRUD(Payment)
)
