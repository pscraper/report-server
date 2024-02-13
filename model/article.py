from sqlmodel import SQLModel, Field


class Article(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    title: str = Field(nullable=False)
    desc: str = Field(nullable=False)
    writer: int = Field(nullable=False, foreign_key="user.id")