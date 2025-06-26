from fastapi import (
    APIRouter,
    HTTPException,
    status,
)
from fastapi.params import Depends
from auth.utils import (
    hash_password,
    encode_jwt,
)
from users.crud import UserDAO
from users.dependencies import (
    authenticate_user,
    get_current_auth_user,
    get_current_token_payload,
)
from users.rabbitmq import (
    get_task_stats,
    publish_user_registered_event
)
from users.schemas import (
    UserRegister,
    UserAuth,
    TokenInfo,
)

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register/")
async def register_user(
        user_data: UserRegister
) -> dict:
    user = await UserDAO.find_one_or_none(username=user_data.username)
    if user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="Пользователь уже существует")
    user_dict = user_data.model_dump()
    user_dict["password"] = hash_password(user_data.password)
    new_user = await UserDAO.add(**user_dict)

    if user_dict.get("email"):
        await publish_user_registered_event(
            user_id=str(new_user.id),
            email=user_dict["email"],
        )

    return {
        "message": "Вы успешно зарегистрированы!",
        "user_id": str(new_user.id)
    }


@router.post("/login/", response_model=TokenInfo)
async def auth_user(
        user: UserAuth = Depends(authenticate_user)
):
    jwt_payload = {
        "sub": user.username,
        "username": user.username,
        "email": user.email,
    }
    token = encode_jwt(jwt_payload)
    return TokenInfo(
        access_token=token,
        token_type="Bearer",
    )


@router.get("/users/me/")
async def auth_user_check_self_info(
        payload: dict = Depends(get_current_token_payload),
        user: UserAuth = Depends(get_current_auth_user),
):
    user_id = user.id
    print(user_id)
    task_stats = await get_task_stats(user_id)

    iat = payload.get("iat")
    return {
        "username": user.username,
        "email": user.email,
        "logged_in_at": iat,
        "executor_tasks": task_stats["executor_tasks"],
        "observer_tasks": task_stats["observer_tasks"]
    }
