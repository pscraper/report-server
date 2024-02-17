from typing import Annotated
from sqlmodel import Session, select
from fastapi import Depends
from database.connection import get_session
from model.user import User


class UserRepository:
    def __init__(self, session: Annotated[Session, Depends(get_session)]):
        self.session = session
    
    def signup(self, user: User) -> User:
        try:
            self.session.add(user)
            self.session.commit()
            stat = select(User).where(User.email == user.email)
            return self.session.exec(stat).first()

        except Exception as e:
            self.session.rollback()
            raise e

        finally:
            self.session.close()

    def findUserById(self, id: int) -> User | None:
        try:
            return self.session.get(User, id)
        
        except Exception as e:
            raise e
        
        finally:
            self.session.close()

    def findUserByEmail(self, email: str) -> User | None:
        try:
            stat = select(User).where(User.email == email)
            return self.session.exec(stat).first()

        except Exception as e:
            raise e
        
        finally:
            self.session.close()
            
    def existUserByEmail(self, email: str) -> bool:
        try:
            stat = select(User).where(User.email == email)
            uop = self.session.exec(stat).first()
            return True if uop else False
        
        except Exception as e:
            raise e
        
        finally:
            self.session.close()