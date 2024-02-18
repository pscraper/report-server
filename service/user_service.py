from typing import Annotated
from fastapi import Depends, HTTPException, status
from repository.user_repository import UserRepository
from model.user import User, UserSignup, UserResponse, TokenResponse
from auth.hash_password import HashPassword
from auth.jwt_handler import create_access_token


class UserService:
    def __init__(
        self,
        userRepository: Annotated[UserRepository, Depends()],
        hashPassword: Annotated[HashPassword, Depends()]
    ) -> None:
        self.userRepository = userRepository
        self.hashPassword = hashPassword
    
    def signup(self, userSignup: UserSignup) -> User:
        user = userSignup.toUser()
        exist = self.userRepository.existUserByEmail(user.email)

        if not exist:
            user.password = self.hashPassword.create_hash(user.password)
            return self.userRepository.signup(user)
        
        raise HTTPException(
            status_code = status.HTTP_409_CONFLICT,
            detail = f"DUPLICATED EMAIL ADDRESS {user.email}"
        )
    
    def signin(self, username: str, password: str) -> TokenResponse:
        user = self.userRepository.findUserByEmail(username)

        if not user:
            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST,
                detail = "CAN'T FIND USER EMAIL {username}"
            )
        
        if not self.hashPassword.verify_hash(password, user.password):
            raise HTTPException(
                status_code = status.HTTP_401_UNAUTHORIZED,
                detail = "UNMATCHED PASSWORD"
            )
        
        return TokenResponse(
            access_token = create_access_token(username),
            token_type = "Bearer"
        )

    def getUser(self, email: int) -> UserResponse:
        user = self.userRepository.findUserByEmail(email)

        if user:
            return UserResponse(id = user.id, email = user.email, role = user.role)
        
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = f"USER NOT EXISTS"
        )
    