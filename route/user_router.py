from fastapi import APIRouter, Depends, status, Body, Path
from typing import Annotated
from model.user import User, UserSignup
from service.user_service import UserService


router = APIRouter()


@router.post(path = "/", status_code = status.HTTP_201_CREATED)
def signup(
    userSignup: Annotated[UserSignup, Body()],
    userService: Annotated[UserService, Depends(UserService)]
) -> User:
    return userService.signup(userSignup)
    

@router.get(path = "/{id}", status_code = status.HTTP_200_OK)
def getUser(
    id: Annotated[int, Path()],
    userService: Annotated[UserService, Depends(UserService)]
) -> User:
    return userService.getUser(id)