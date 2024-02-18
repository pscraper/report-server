import time
from fastapi import HTTPException, status
from typing import Any
from datetime import datetime
from jose import jwt, JWTError
from config.ini_config import Config, APP


config = Config()
secret_key = config.read_value(APP, "secret_key")


def create_access_token(username: str) -> str:
    payload = {
        "username": username,
        "expires": time.time() + 1800
    }

    token = jwt.encode(payload, secret_key, algorithm = "HS256")
    return token


def verify_access_token(token: str) -> dict[str, Any]:
    try:
        data = jwt.decode(token, secret_key, algorithms = ["HS256"])
        expire = data.get("expires")

        if expire is None:
            raise HTTPException(
                status_code = status.HTTP_401_UNAUTHORIZED,
                detail = "No Access Token Supplied"
            )
        
        if datetime.utcnow() > datetime.utcfromtimestamp(expire):
            raise HTTPException(
                status_code = status.HTTP_401_UNAUTHORIZED,
                detail = "Token Expired"
            )
        
        return data
    
    except Exception as e:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = e
        )

        
