from fastapi import Depends, HTTPException, status
from sqlmodel import Session
from typing import Annotated
from model.article import Article, CreateArticle
from config.engine_config import EngineConfig


class ArticleService:
    def __init__(
        self, 
        session: Annotated[Session, Depends(EngineConfig.get_session)]
    ) -> None:
        self.session = session
        
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