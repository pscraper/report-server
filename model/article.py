from pydantic import BaseModel
from sqlmodel import SQLModel, Field


class Article(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    title: str = Field(nullable=False)
    desc: str = Field(nullable=False)
    writer_id: int = Field(nullable=False, foreign_key="user.id")
    
    
class CreateArticle(BaseModel):
    title: str
    desc: str
    
    def to_article(self, writer_id: int) -> Article:
        return Article(
            title = self.title,
            desc = self.desc,
            writer_id = writer_id
        )
        
