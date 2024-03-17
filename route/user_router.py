import json
from typing import Optional
from datetime import datetime
from fastapi import (
    APIRouter, 
    Request,
    Response, 
    Depends, 
    Body, 
    File,
    Path,
    Form,
    status,
    HTTPException,
)
from pathlib import Path as Pathlib
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from typing import Annotated
from auth.jwt_handler import JWTHandler
from auth.authenticate import basic_authenticate, oauth2_authenticate
from auth.hash_password import HashPassword
from config.engine_config import EngineConfig
from config.redis_driver import RedisDriver
from model.user import (
    User, 
    UserSigninRes,
    TokenResponse
)


router = APIRouter()


@router.post(path = "/signup", status_code = status.HTTP_201_CREATED)
async def signup(
    session: Annotated[Session, Depends(EngineConfig.get_session)],
    email: Annotated[str, Form()],
    password: Annotated[str, Form()],
    hash_password: Annotated[HashPassword, Depends()],
) -> None:
    stat = select(User).where(User.email == email)
    exist = session.exec(stat).first() != None

    if exist:
        raise HTTPException(status.HTTP_409_CONFLICT)
    
    user = User(
        email = email, 
        password = hash_password.create_hash(password),
    )

    session.add(user)
    session.commit()


@router.post("/file")
async def userProfileImage(
    session: Annotated[Session, Depends(EngineConfig.get_session)],
    email: Annotated[str, Form()],
    filename: Annotated[str, Form()],
    image: Annotated[bytes, Form()]
) -> None:
    stat = select(User).where(User.email == email)
    user = session.exec(stat).first()

    if not user:
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST)

    upload_path = Pathlib.cwd() / "storage" / "user"
    
    if not upload_path.exists():
        upload_path.mkdir(parents = True)

    with open(upload_path / filename, "wb") as f:
        f.write(image)

    user.profile_image = upload_path / filename
    session.add(user)
    session.commit()
    

# HttpBasicAuth 
@router.post(path = "/signin/basic", status_code = status.HTTP_200_OK)
async def signinBasic(
    response: Response,
    session: Annotated[Session, Depends(EngineConfig.get_session)],
    user: Annotated[User, Depends(basic_authenticate)],
    jwt_handler: Annotated[JWTHandler, Depends()],
) -> UserSigninRes:
    # token 생성
    access_token = await jwt_handler.create_access_token(user.email)
    refresh_token = await jwt_handler.create_refresh_token(user.email)
    
    # http 응답 헤더 세팅   
    response.headers["Authorization"] = access_token
    response.headers["Authorization-refresh"] = refresh_token
    user.refresh_token = refresh_token
    user.last_login_date = datetime.now()
    
    # 유저 정보 업데이트
    session.add(user)
    session.commit()

    return UserSigninRes(
        email = user.email, 
        profile_image = user.profile_image,
        role = user.role,
        last_login_date = user.last_login_date,
    )


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
    refresh_token = request.headers['Authorization-Refresh']
    success, payload = await jwt_handler.verify_refresh_token(refresh_token)
    username = payload['username']
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


@router.get("/valid/{session_id}")
async def is_valid_session_id(
    user_email: Annotated[str, Depends(oauth2_authenticate)],
    session_id: Annotated[str, Path()],
    redis_driver: Annotated[RedisDriver, Depends()]
) -> bool:
    user = await redis_driver.get_key(session_id)
    return user != None


@router.get("/signout/{session_id}")
async def signout(
    session_id: Annotated[str, Path()],
    redis_driver: Annotated[RedisDriver, Depends()]
) -> None:
    await redis_driver.del_key(session_id)