from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, OAuth2PasswordBearer, HTTPBasicCredentials
from sqlmodel import Session, select
from auth.jwt_handler import JWTHandler
from auth.hash_password import HashPassword
from model.user import User
from config.engine_config import EngineConfig


oauth2_scheme = OAuth2PasswordBearer(tokenUrl = "/user/signin/oauth2")
basic_security = HTTPBasic()


async def oauth2_authenticate(
    token: Annotated[str, Depends(oauth2_scheme)],
    jwtHandler: Annotated[JWTHandler, Depends()]
) -> str:
    if not token:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "UNAUTHORIZED"
        )
    
    success, data = await jwtHandler.verify_access_token(token)
    if success:
        return data["username"]
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)


async def basic_authenticate(
    session: Annotated[Session, Depends(EngineConfig.get_session)],
    credentials: Annotated[HTTPBasicCredentials, Depends(basic_security)],
    hashPassword: Annotated[HashPassword, Depends()]
) -> User:
    username = credentials.username
    password = credentials.password
    stat = select(User).where(User.email == username)
    user = session.exec(stat).first()

    if not user or not hashPassword.verify_hash(password, user.password):
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Invalid Credentials",
            headers = {"WWW-Authenticate": "Basic"}
        )

    return user