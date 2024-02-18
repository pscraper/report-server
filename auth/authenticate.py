from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from auth.jwt_handler import JWTHandler


oauth2_scheme = OAuth2PasswordBearer(tokenUrl = "/user/signin")


async def authenticate(
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
