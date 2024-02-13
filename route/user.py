from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from database.connection import get_session
from model.user import User


router = APIRouter()


@router.get("/")
async def get_all_users(
    session: Session = Depends(get_session)
) -> list[User]:
    stat = select(User)
    return session.exec(stat).all()