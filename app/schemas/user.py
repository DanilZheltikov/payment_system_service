from pydantic import BaseModel, ConfigDict, EmailStr


class UserCreate(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    first_name: str
    last_name: str
    is_active: bool
    is_admin: bool


class UserRead(UserUpdate):
    id: int
    email: EmailStr
    full_name: str

    model_config = ConfigDict(from_attributes=True)
