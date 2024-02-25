from sqlalchemy import Engine
from sqlmodel import SQLModel, Session, create_engine
from pathlib import Path


class EngineConfig:
    _engine_ = None

    @classmethod
    def init_engine(cls, DB_CONN_URL: str):
        if cls._engine_ == None:
            cls._engine_ = create_engine(DB_CONN_URL, echo = True)
        SQLModel.metadata.create_all(cls._engine_)

    @classmethod
    def get_engine(self) -> Engine:
        return self._engine_

    @classmethod
    def remove_db_file(self) -> None:
        file = Path.cwd() / "api-server.db"
        if file.exists() and file.is_file():
            file.unlink()
    
    @classmethod
    def get_session(self):
        with Session(self._engine_) as session:
            yield session
