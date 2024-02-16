from config.ini_config import Config, SQLITE
from sqlmodel import SQLModel, Session, create_engine


engine = create_engine(
    url = Config().read_value(SQLITE, "db_conn_url"), 
    echo = True,
    connect_args = {"check_same_thread": False}
)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
    
    
def get_session():
    with Session(engine) as session:
        yield session