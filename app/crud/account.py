from app.crud.base import UserRelatedBaseCRUD
from app.models import Account

account_crud = UserRelatedBaseCRUD(Account)
