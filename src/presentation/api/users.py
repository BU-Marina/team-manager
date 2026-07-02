from fastapi import APIRouter, Depends, HTTPException, status
from src.domain.users.entities import User
from src.domain.users.usecases import UserUseCases
from src.infra.auth.jwt import create_access_token, create_refresh_token, decode_token
from src.presentation.schemas.users import (
    UserRegisterRequest,
    UserLoginRequest,
    TokenResponse,
    RefreshRequest,
    UserResponse,
)
from src.presentation.api.dependencies import get_user_usecases, get_current_user

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def register(
    data: UserRegisterRequest,
    usecases: UserUseCases = Depends(get_user_usecases),
):
    try:
        user = await usecases.register(email=data.email, password=data.password)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    return _user_to_response(user)


@router.post("/login", response_model=TokenResponse)
async def login(
    data: UserLoginRequest,
    usecases: UserUseCases = Depends(get_user_usecases),
):
    try:
        user = await usecases.authenticate(email=data.email, password=data.password)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    data: RefreshRequest,
    usecases: UserUseCases = Depends(get_user_usecases),
):
    payload = decode_token(data.refresh_token)
    if payload is None or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Невалидный refresh токен"
        )

    user_id = payload.get("sub")
    user = await usecases.get_by_id(int(user_id))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Пользователь не найден"
        )

    access_token = create_access_token({"sub": str(user.id)})
    refresh_token = create_refresh_token({"sub": str(user.id)})
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return _user_to_response(current_user)


def _user_to_response(user: User) -> UserResponse:
    return UserResponse(
        id=user.id,
        email=user.email,
        role=str(user.role),
        display_name=user.display_name,
    )
