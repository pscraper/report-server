from fastapi import Depends, HTTPException, status
from sqlmodel import Session, select
from typing import Annotated
from database.connection import get_session
from model.user import User
from model.article import Article, CreateArticle


class ArticleService:
    def __init__(
        self, 
        session: Annotated[Session, Depends(get_session)]
    ) -> None:
        self.session = session
        
    
    def get_article(self, article_id: int) -> Article:
        stat = select(Article, article_id)
        result = self.session.exec(stat).first()
        
        if result:
            return result[0]
        
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "게시글을 찾을 수 없습니다."
        )
        
        
    # TODO 유저 권한 확인
    def create_article(
        self,
        create_article: CreateArticle,
        user_id: int
    ) -> Article:
        article = create_article.to_article(user_id)
        
        try:
            self.session.add(article)
            self.session.commit()
            self.session.refresh(article)
            return article
            
        except Exception as e:
            self.session.rollback()
            raise HTTPException(
                status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail = e
            )