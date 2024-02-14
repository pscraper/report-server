from sqlmodel import Session, create_engine, SQLModel


engine = create_engine("sqlite:///./report-server.db", connect_args={"check_same_thread": False})


def conn():
    SQLModel.metadata.create_all(engine)   


def get_session():
    with Session(engine) as session:
        yield session


