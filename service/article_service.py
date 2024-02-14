from fastapi import Depends, HTTPException, status
from sqlmodel import select
from sqlalchemy.ext.asyncio.session import AsyncSession
from typing import Annotated
from database.connection import get_session
from model.user import User
from model.article import Article, CreateArticle


class ArticleService:
    def __init__(
        self, 
        session: Annotated[AsyncSession, Depends(get_session)]
    ) -> None:
        self.session = session
        
    
    async def get_article(self, article_id: int) -> Article:
        try:
            stat = select(Article).where(Article.id == article_id)
            result = await self.session.execute(stat)
        
            if result.scalars().first():
                return result.scalars().first()
        
        except Exception as e:
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = e
            )

        finally:
            self.session.remove()
        
        
    # TODO 유저 권한 확인
    async def create_article(
        self,
        create_article: CreateArticle,
        user_id: int
    ) -> Article:
        article = create_article.to_article(user_id)
        
        try:
            self.session.begin()
            self.session.commit()
            self.session.refresh(article)
            return article
            
        except Exception as e:
            self.session.rollback()
            raise HTTPException(
                status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail = e
            )