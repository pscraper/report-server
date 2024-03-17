import time
from datetime import datetime
from typing import Any
from jose import jwt
from config.ini_config import IniConfig, APP



class JWTHandler:
    config = IniConfig()

    async def _create_token(self, payload: dict[str, Any], secret_key: str) -> str:
        token = jwt.encode(payload, secret_key, algorithm = "HS256")
        return token


    async def create_access_token(self, username: str) -> str:
        payload = {"username": username, "expires": time.time() + 900}
        secret_key = self.config.read_value(APP, "secret_key")
        return await self._create_token(payload, secret_key)


    async def create_refresh_token(self, username: str) -> str:
        payload = {"username": username, "expires": time.time() + (3600 * 24 * 60)}
        secret_key = self.config.read_value(APP, "refresh_secret_key")
        return await self._create_token(payload, secret_key)


    async def _verify_token(self, token: str, secret_key: str) -> tuple[bool, dict[str, Any]]:
        data = jwt.decode(token, secret_key, algorithms = "HS256")
        expire = data.get("expires")

        if expire is None:
            return False, data
        
        if datetime.utcnow() > datetime.utcfromtimestamp(expire):
            return False, data
        
        return True, data


    async def verify_access_token(self, token: str) -> tuple[bool, dict[str, Any]]:
        secret_key = self.config.read_value(APP, "secret_key")
        return await self._verify_token(token, secret_key)


    async def verify_refresh_token(self, token: str) -> tuple[bool, dict[str, Any]]:
        secret_key = self.config.read_value(APP, "refresh_secret_key")
        return await self._verify_token(token, secret_key)

        
