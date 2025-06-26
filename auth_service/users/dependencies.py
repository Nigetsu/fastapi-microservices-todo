from fastapi import (
    HTTPException,
    status,
    Form,
    Depends,
)
from jwt import InvalidTokenError
from auth.utils import (
    validate_password,
    decode_jwt,
)
from users.crud import UserDAO
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/auth/login/",
)


def get_current_token_payload(
        token: str = Depends(oauth2_scheme),
) -> dict:
    try:
        payload = decode_jwt(
            token=token,
        )
    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"invalid token error: {e}",
        )
    return payload


async def get_current_auth_user(
        payload: dict = Depends(get_current_token_payload),
):
    username: str | None = payload.get("sub")
    user = await UserDAO.find_one_or_none(username=username)
    if user:
        return user
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="token invalid (user not found)",
    )


async def authenticate_user(
        username: str = Form(),
        password: str = Form(),
):
    user = await UserDAO.find_one_or_none(username=username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid email",
        )

    if not validate_password(password=password, hashed_password=user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid password",
        )

    return user
