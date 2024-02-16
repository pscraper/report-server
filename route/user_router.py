from fastapi import APIRouter, Depends, HTTPException, status
from typing import Annotated
from sqlmodel import select
from sqlalchemy.orm import Session
from database.connection import get_session
from model.user import User, UserSignup


router = APIRouter()


@router.get("/{id}")
async def get_user(
    id: int,
    session: Annotated[Session, Depends(get_session)]
) -> User:
    stat = select(User, id)
    result = session.execute(stat).first()
    
    if result:
        return result[0]
    
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="CAN'T FIND USER ID"
    ) 


@router.get("/")
async def get_all_users(
    session: Annotated[Session, Depends(get_session)]
) -> list[User]:
    stat = select(User)
    return session.exec(stat).all()


@router.post("/", status_code = status.HTTP_201_CREATED)
async def signup(
    user_signup: UserSignup,
    session: Session = Depends(get_session),
) -> User:
    stat = select(User).where(User.email == user_signup.email)
    result = session.exec(stat).first()
    
    # db.add(): 메모리에 객체 유지
    # db.commit(): 메모리에 있는 객체를 DB에 반영, 다음 commit까지 메모리는 유지됨
    # db.refresh(): 메모리에 있는 객체 삭제
    if result == None:
        new_user = user_signup.to_user()
        session.add(new_user)
        session.commit()
        # session.refresh()   
        return new_user
    
    raise HTTPException(
        status_code = 409,
        detail = "이미 존재하는 이메일"
    )
    
    
@router.delete("/{id}", status_code = status.HTTP_200_OK)
async def deleteUser(
    id: int,
    session: Session = Depends(get_session)
) -> None:
    stat = select(User, id)
    result = session.exec(stat).first()
    
    if result != None:
        session.delete(result[0])
        session.commit()
        return None
    
    raise HTTPException(
        status_code = 400,
        detail = "유저를 찾을 수 없습니다"
    )