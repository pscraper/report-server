from fastapi import APIRouter, Request, Response, Depends, status, Body, Form
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from model.user import User, UserSignup, UserResponse, TokenResponse
from service.user_service import UserService
from auth.authenticate import basic_authenticate, oauth2_authenticate 


router = APIRouter()


@router.post(path = "/signup", status_code = status.HTTP_201_CREATED)
def signup(
    userSignup: Annotated[UserSignup, Body()],
    userService: Annotated[UserService, Depends()]
) -> UserResponse:
    return userService.signup(userSignup)
    

@router.post(path = "/signin/basic", status_code = status.HTTP_200_OK)
def signinBasic(
    response: Response,
    user: Annotated[User, Depends(basic_authenticate)],
    userService: Annotated[UserService, Depends()]
) -> User:
    return userService.signinBasic(response, user)


@router.get(path = "/basic/me", status_code = status.HTTP_200_OK)
def getMyInfo(
    request: Request,
    userService: Annotated[UserService, Depends()]
) -> User:
    session_id = request.headers["session_id"]
    return userService.getUserBySession(session_id)


@router.post(path = "/signin/oauth2", status_code = status.HTTP_200_OK)
def signinOAuth2(
    userForm: Annotated[OAuth2PasswordRequestForm, Depends()],
    userService: Annotated[UserService, Depends()]
) -> TokenResponse:
    return userService.signinOAuth2(userForm.username, userForm.password)


@router.get(path = "/", status_code = status.HTTP_200_OK)
def getUser(
    email: Annotated[str, Depends(oauth2_authenticate)],
    userService: Annotated[UserService, Depends()]
) -> UserResponse:
    return userService.getUser(email)


@router.post(path = "/refresh", status_code = status.HTTP_201_CREATED)
def refreshAllTokens(
    email: Annotated[str, Form()],
    userService: Annotated[UserService, Depends()]
) -> TokenResponse:
    return userService.refreshAllTokens(email)