from fastapi import (
    APIRouter, 
    Request,
    Response, 
    Depends, 
    Body, 
    Path,
    status,
    HTTPException
)
from dataclasses import dataclass
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from typing import Annotated
from datetime import timezone, datetime, timedelta
from model.user import User, UserSignup, UserResponse, TokenResponse
from auth.jwt_handler import JWTHandler
from auth.authenticate import basic_authenticate
from auth.hash_password import HashPassword
from config.transaction_route import TransactionRoute
from config.engine_config import EngineConfig
from config.redis_driver import RedisDriver
from uuid import uuid4


router = APIRouter(route_class = TransactionRoute)


@router.post(path = "/signup", status_code = status.HTTP_201_CREATED)
async def signup(
    userSignup: Annotated[UserSignup, Body()],
    session: Annotated[Session, Depends(EngineConfig.get_session)],
    hashPassword: Annotated[HashPassword, Depends()]
) -> UserResponse:
    user = userSignup.toUser()
    stat = select(User).where(User.email == user.email)
    exist = session.exec(stat).first() != None

    if not exist:
        user.password = hashPassword.create_hash(user.password)
        session.add(user)
        session.commit()
        return UserResponse(id = user.id, email = user.email, role = user.role)
    
    raise HTTPException(
        status_code = status.HTTP_409_CONFLICT,
        detail = f"DUPLICATED EMAIL ADDRESS {user.email}"
    )


# HttpBasicAuth 
@router.post(path = "/signin/basic", status_code = status.HTTP_200_OK)
async def signinBasic(
    response: Response,
    session: Annotated[Session, Depends(EngineConfig.get_session)],
    user: Annotated[User, Depends(basic_authenticate)],
    jwtHandler: Annotated[JWTHandler, Depends()],
    redisDriver: Annotated[RedisDriver, Depends()]
) -> User:
    # session id, token 생성
    session_id = str(uuid4())
    access_token = await jwtHandler.create_access_token(user.email)
    refresh_token = await jwtHandler.create_refresh_token(user.email)
    
    # http 응답 헤더 세팅   
    response.set_cookie("JSESSIONID", session_id)
    response.headers["Authorization"] = access_token
    response.headers["Authorization-refresh"] = refresh_token
    user.refresh_token = refresh_token
    
    # 유저 정보 업데이트
    session.add(user)
    session.commit()
    await redisDriver.set_key(session_id, "test")

    return user


@dataclass
class SessionTest:
    session_id: str

@router.post(path = "/", status_code = status.HTTP_200_OK)
async def get_my_info(
    session_test: Annotated[SessionTest, Body()],
    redis_driver: Annotated[RedisDriver, Depends()]
) -> str:
    user = await redis_driver.get_key(session_test.session_id)
    print(user)
    return user


@router.post(path = "/signin/oauth2", status_code = status.HTTP_200_OK)
async def signinOAuth2(
    userForm: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[Session, Depends(EngineConfig.get_session)],
    hashPassword: Annotated[HashPassword, Depends()],
    jwtHandler: Annotated[JWTHandler, Depends()]
) -> TokenResponse:
    stat = select(User).where(User.email == userForm.username)
    user = session.exec(stat).first()

    if not user:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "CAN'T FIND USER EMAIL {username}"
        )
    
    if not hashPassword.verify_hash(userForm.password, user.password):
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "UNMATCHED PASSWORD"
        )
    
    access_token = await jwtHandler.create_access_token(userForm.username)
    refresh_token = await jwtHandler.create_refresh_token(userForm.username)
    user.refresh_token = refresh_token

    session.add(user)
    session.commit()

    return TokenResponse(
        access_token = access_token,
        refresh_token = refresh_token,
        token_type = "Bearer"
    )