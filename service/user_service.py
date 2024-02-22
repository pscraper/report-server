from typing import Annotated
from fastapi import Response, Depends, HTTPException, status
from repository.user_repository import UserRepository
from model.user import User, UserSignup, UserResponse, TokenResponse
from auth.hash_password import HashPassword
from auth.jwt_handler import JWTHandler
from uuid import uuid4


class UserService:
    session = dict()

    def __init__(
        self,
        userRepository: Annotated[UserRepository, Depends()],
        hashPassword: Annotated[HashPassword, Depends()],
        jwtHandler: Annotated[JWTHandler, Depends()]
    ) -> None:
        self.userRepository = userRepository
        self.hashPassword = hashPassword
        self.jwtHandler = jwtHandler
    
    def signup(self, userSignup: UserSignup) -> UserResponse:
        user = userSignup.toUser()
        exist = self.userRepository.existUserByEmail(user.email)

        if not exist:
            user.password = self.hashPassword.create_hash(user.password)
            user = self.userRepository.addUser(user)
            return UserResponse(id = user.id, email = user.email, role = user.role)
        
        raise HTTPException(
            status_code = status.HTTP_409_CONFLICT,
            detail = f"DUPLICATED EMAIL ADDRESS {user.email}"
        )
    
    def signinOAuth2(self, username: str, password: str) -> TokenResponse:
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
        
        access_token = self.jwtHandler.create_access_token(username)
        refresh_token = self.jwtHandler.create_refresh_token(username)
        user.refresh_token = refresh_token
        self.userRepository.addUser(user)

        return TokenResponse(
            access_token = access_token,
            refresh_token = refresh_token,
            token_type = "Bearer"
        )
    

    def signinBasic(self, response: Response, user: User) -> User:
        session_id = str(uuid4())
        self.session[session_id] = user
        access_token = self.jwtHandler.create_access_token(user.email)
        refresh_token = self.jwtHandler.create_refresh_token(user.email)
        session = f"session_id={session_id}"

        response.headers["session_id"] = session_id
        response.headers["set-cookie"] = session
        response.headers["Authorization"] = access_token
        response.headers["Authorization-refresh"] = refresh_token
        user.refresh_token = refresh_token
        self.userRepository.addUser(user)

        return user

    def getUser(self, email: int) -> UserResponse:
        user = self.userRepository.findUserByEmail(email)

        if user:
            return UserResponse(id = user.id, email = user.email, role = user.role)
        
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = f"USER NOT EXISTS"
        )
    

    def getUserBySession(self, session_id: str) -> User:
        user = self.session[session_id]

        if not user:
            raise HTTPException(
                status_code = status.HTTP_401_UNAUTHORIZED,
                detail = "Invalid Session"
            )
        
        return user

    
    def refreshAllTokens(self, email: str) -> TokenResponse:
        user = self.userRepository.findUserByEmail(email)

        if user:
            data = self.jwtHandler.verify_refresh_token(user.refresh_token)

            if data['username'] != email:
                raise HTTPException(
                    status_code = status.HTTP_403_FORBIDDEN,
                    detail = "UNMATCHED EMAIL INFO"
                )

            access_token = self.jwtHandler.create_access_token(email)
            refresh_token = self.jwtHandler.create_refresh_token(email)
            user.refresh_token = refresh_token
            self.userRepository.addUser(user)

            return TokenResponse(
                access_token = access_token,
                refresh_token = refresh_token,
                token_type = "Bearer" 
            )
        
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "USER NOT EXISTS"
        )