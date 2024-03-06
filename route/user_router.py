import json
from fastapi import (
    APIRouter, 
    Request,
    Response, 
    Depends, 
    Body, 
    Path,
    status,
    HTTPException,
)
from fastapi.encoders import jsonable_encoder
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from typing import Annotated
from model.user import User, UserSignup, UserResponse, TokenResponse
from auth.jwt_handler import JWTHandler
from auth.authenticate import basic_authenticate, oauth2_authenticate
from auth.hash_password import HashPassword
from config.engine_config import EngineConfig
from config.redis_driver import RedisDriver
from uuid import uuid4


router = APIRouter()


@router.post(path = "/signup", status_code = status.HTTP_201_CREATED)
async def signup(
    session: Annotated[Session, Depends(EngineConfig.get_session)],
    user_signup: Annotated[UserSignup, Body()],
    hash_password: Annotated[HashPassword, Depends()]
) -> UserResponse:
    user = user_signup.to_user()
    stat = select(User).where(User.email == user.email)
    exist = session.exec(stat).first() != None

    if not exist:
        user.password = hash_password.create_hash(user.password)
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
    jwt_handler: Annotated[JWTHandler, Depends()],
    redis_driver: Annotated[RedisDriver, Depends()]
) -> bool:
    # session id, token 생성
    session_id = str(uuid4())
    access_token = await jwt_handler.create_access_token(user.email)
    refresh_token = await jwt_handler.create_refresh_token(user.email)
    
    # http 응답 헤더 세팅   
    response.headers["Authorization-session"] = session_id
    response.headers["Authorization"] = access_token
    response.headers["Authorization-refresh"] = refresh_token
    user.refresh_token = refresh_token
    
    # 유저 정보 업데이트
    await redis_driver.set_key(session_id, json.dumps(jsonable_encoder(user)))
    session.add(user)
    session.commit()
    return True


@router.post(path = "/signin/oauth2", status_code = status.HTTP_200_OK)
async def signinOAuth2(
    user_form: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[Session, Depends(EngineConfig.get_session)],
    hash_password: Annotated[HashPassword, Depends()],
    jwt_handler: Annotated[JWTHandler, Depends()]
) -> TokenResponse:
    stat = select(User).where(User.email == user_form.username)
    user = session.exec(stat).first()

    if not user:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "CAN'T FIND USER EMAIL {username}"
        )
    
    if not hash_password.verify_hash(user_form.password, user.password):
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "UNMATCHED PASSWORD"
        )
    
    access_token = await jwt_handler.create_access_token(user_form.username)
    refresh_token = await jwt_handler.create_refresh_token(user_form.username)
    user.refresh_token = refresh_token

    session.add(user)
    session.commit()

    return TokenResponse(
        access_token = access_token,
        refresh_token = refresh_token,
        token_type = "Bearer"
    )


@router.get("/refresh")
async def refresh_all_token(
    request: Request,
    response: Response,
    session: Annotated[Session, Depends(EngineConfig.get_session)],
    jwt_handler: Annotated[JWTHandler, Depends()]
) -> int:
    try:
        refresh_token = request.headers['Authorization-Refresh']
        username = await jwt_handler.verify_refresh_token(refresh_token)
        stat = select(User).where(User.email == username)
        user = session.exec(stat).first()

        access_token = await jwt_handler.create_access_token(username)
        refresh_token = await jwt_handler.create_refresh_token(username)
        response.headers['Token-Type'] = "Bearer"
        response.headers['Authorization'] = access_token
        response.headers['Authorization-Refresh'] = refresh_token
        user.refresh_token = refresh_token
        session.add(user)

        return 1

    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=e)


@router.get("/valid/{session_id}")
async def is_valid_session_id(
    user_email: Annotated[str, Depends(oauth2_authenticate)],
    session_id: Annotated[str, Path()],
    redis_driver: Annotated[RedisDriver, Depends()]
) -> bool:
    user = await redis_driver.get_key(session_id)
    return user != None


@router.get("/info/{session_id}")
async def get_user_by_session_id(
    user_email: Annotated[str, Depends(oauth2_authenticate)],
    session_id: Annotated[str, Path()],
    redis_driver: Annotated[RedisDriver, Depends()]
) -> UserResponse:
    user = await redis_driver.get_key(session_id)

    if not user:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "Invalid Session ID"
        )
    
    try:
        user = json.loads(user)
        return UserResponse(id = user['id'], email = user['email'], role = user['role'])
    
    except Exception as e:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = e
        )


@router.get("/signout/{session_id}")
async def signout(
    session_id: Annotated[str, Path()],
    redis_driver: Annotated[RedisDriver, Depends()]
) -> None:
    await redis_driver.del_key(session_id)