from typing import Annotated, Callable, Any
from fastapi import Depends
from sqlmodel import Session
from config.engine_config import EngineConfig


class Transactional:
    def __init__(self, func) -> None:
        self.func = func

    # 인스턴스가 호출되었을 때 실행
    def __call__(
        self, 
        session: Annotated[Session, Depends(EngineConfig.get_session)]
    ) -> Callable:
        async def _transactional(*args, **kwargs) -> Any:
            try:
                result = await self.func(*args, **kwargs)
                session.commit()
            
            except Exception as e:
                session.rollback()
                raise e
            
            finally:
                session.close()
            
            return result
        
        return _transactional
        
