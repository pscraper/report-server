from typing import Annotated, Optional
from sqlmodel import Session, select
from fastapi import Depends
from config.engine_config import EngineConfig
from model.user import User


class UserRepository:
    def __init__(self, session: Annotated[Session, Depends(EngineConfig.get_session)]):
        self.session = session
    
    def addUser(self, user: User) -> User:
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

    def findUserById(self, id: int) -> Optional[User]:
        try:
            return self.session.get(User, id)
        
        except Exception as e:
            raise e
        
        finally:
            self.session.close()

    def findUserByEmail(self, email: str) -> Optional[User]:
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