import time
from fastapi import HTTPException, status
from typing import Any
from datetime import datetime
from jose import jwt, JWTError
from config.ini_config import Config, APP



class JWTHandler:
    def __init__(self):
        self.config = Config()

    def _create_token(self, payload: dict[str, Any], secret_key: str) -> str:
        token = jwt.encode(payload, secret_key, algorithm = "HS256")
        return token


    def create_access_token(self, username: str) -> str:
        payload = {"username": username, "expires": time.time() + 1800}
        secret_key = self.config.read_value(APP, "secret_key")
        return self._create_token(payload, secret_key)


    def create_refresh_token(self, username: str) -> str:
        payload = {"username": username, "expires": time.time() + (3600 * 24 * 60)}
        secret_key = self.config.read_value(APP, "refresh_secret_key")
        return self._create_token(payload, secret_key)


    def _verify_token(self, token: str, secret_key: str) -> dict[str, Any]:
        try:
            data = jwt.decode(token, secret_key, algorithms = "HS256")
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

        except JWTError as e:
            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST,
                detail = e
            )


    def verify_access_token(self, token: str) -> dict[str, Any]:
        secret_key = self.config.read_value(APP, "secret_key")
        return self._verify_token(token, secret_key)


    def verify_refresh_token(self, token: str) -> dict[str, Any]:
        secret_key = self.config.read_value(APP, "refresh_secret_key")
        return self._verify_token(token, secret_key)

        
