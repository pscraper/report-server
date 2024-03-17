from pydantic import BaseModel
from datetime import datetime
from sqlmodel import SQLModel, Field
from const import UserRole
from typing import Optional


class User(SQLModel, table = True):
    id: int = Field(default = None, primary_key = True)
    email: str = Field(nullable = False, unique = True)
    password: str = Field(nullable = False)
    profile_image: Optional[str] = Field(nullable = True)
    role: UserRole = Field(default = UserRole.USER.value, nullable = False)
    last_login_date: datetime = Field(default = datetime.now(), nullable = False)
    refresh_token: str = Field(nullable = True)
    

class UserSignup(BaseModel):
    email: str 
    password: str
    
    def to_user(self) -> User:
        return User(
            email = self.email,
            password = self.password,
            role = UserRole.USER.value
        )
    

class UserSigninRes(BaseModel):
    email: str
    profile_image: Optional[str]
    role: UserRole
    last_login_date: datetime
    

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str