from fastapi import APIRouter, Depends, status, Body, Path
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from model.user import User, UserSignup, TokenResponse
from service.user_service import UserService
from auth.authenticate import authenticate


router = APIRouter()


@router.post(path = "/signup", status_code = status.HTTP_201_CREATED)
def signup(
    userSignup: Annotated[UserSignup, Body()],
    userService: Annotated[UserService, Depends(UserService)]
) -> User:
    return userService.signup(userSignup)
    

@router.post(path = "/signin", status_code = status.HTTP_200_OK)
def signin(
    userForm: Annotated[OAuth2PasswordRequestForm, Depends()],
    userService: Annotated[UserService, Depends()]
) -> TokenResponse:
    return userService.signin(userForm.username, userForm.password)


@router.get(path = "/", status_code = status.HTTP_200_OK)
def getUser(
    email: Annotated[str, Depends(authenticate)],
    userService: Annotated[UserService, Depends(UserService)]
) -> User:
    return userService.getUser(email)