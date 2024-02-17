from typing import Annotated
from fastapi import Depends, HTTPException, status
from repository.user_repository import UserRepository
from model.user import User, UserSignup
from database.transactional import Transactional


class UserService:
    def __init__(
        self,
        userRepository: Annotated[UserRepository, Depends()]
    ) -> None:
        self.userRepository = userRepository
    
    def signup(self, userSignup: UserSignup) -> User:
        user = userSignup.toUser()
        exist = self.userRepository.existUserByEmail(user.email)

        if not exist:
            return self.userRepository.signup(user)
        
        raise HTTPException(
            status_code = status.HTTP_409_CONFLICT,
            detail = f"DUPLICATED EMAIL ADDRESS {user.email}"
        )
    
    def getUser(self, id: int) -> User:
        user = self.userRepository.findUserById(id)

        if user:
            return user
        
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = f"USER ID {id} DOES NOT EXISTS"
        )
    