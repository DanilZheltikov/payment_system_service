from app.crud.base import UserRelatedBaseCRUD
from app.models import Payment

payment_crud = UserRelatedBaseCRUD(Payment)
