from pydantic import BaseModel
from sqlmodel import SQLModel, Field
from model.enums import UserRole


class User(SQLModel, table = True):
    id: int = Field(default = None, primary_key = True)
    email: str = Field(nullable = False, unique = True)
    password: str = Field(nullable = False)
    role: UserRole = Field(default = UserRole.USER.value, nullable = False)
    
    
class UserSignup(BaseModel):
    email: str 
    password: str
    
    def toUser(self) -> User:
        return User(
            email = self.email,
            password = self.password,
            role = UserRole.USER.value
        )


class TokenResponse(BaseModel):
    access_token: str
    token_type: str

