from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, OAuth2PasswordBearer, HTTPBasicCredentials
from auth.jwt_handler import JWTHandler
from repository.user_repository import UserRepository
from auth.hash_password import HashPassword
from model.user import User


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
    
    decoded_token = jwtHandler.verify_access_token(token)
    return decoded_token["username"]


async def basic_authenticate(
    credentials: Annotated[HTTPBasicCredentials, Depends(basic_security)],
    userRepository: Annotated[UserRepository, Depends()],
    hashPassword: Annotated[HashPassword, Depends()]
) -> User:
    username = credentials.username
    password = credentials.password
    user = userRepository.findUserByEmail(username)
    if not user or not hashPassword.verify_hash(password, user.password):
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = "Invalid Credentials",
            headers = {"WWW-Authenticate": "Basic"}
        )

    return user