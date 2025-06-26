from uuid import UUID

from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    field_validator,
)
import re


class UserRegister(BaseModel):
    email: EmailStr | None = None
    username: str
    password: str = Field(..., min_length=5, max_length=50, description="Пароль, от 5 до 50 знаков")
    phone_number: str = Field(..., description="Номер телефона в международном формате, начинающийся с '+'")

    @field_validator("phone_number")
    def validate_phone_number(cls, value: str) -> str:
        if not re.match(r'^\+\d{5,15}$', value):
            raise ValueError('Номер телефона должен начинаться с "+" и содержать от 5 до 15 цифр')
        return value


class UserAuth(BaseModel):
    id: UUID
    email: EmailStr | None = None
    username: str
    password: str = Field(..., min_length=5, max_length=50, description="Пароль, от 5 до 50 знаков")


class TokenInfo(BaseModel):
    access_token: str
    token_type: str
