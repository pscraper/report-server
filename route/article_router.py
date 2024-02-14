from fastapi import APIRouter, Body, Cookie, Depends
from typing import Annotated
from model.article import Article, CreateArticle
from model.enums import UserRole
from service.article_service import ArticleService


router = APIRouter()


@router.get("/{article_id}")
async def get_article(
    article_id: int,
    article_service: Annotated[ArticleService, Depends(ArticleService)]
) -> Article:
    return article_service.get_article(article_id)
    

@router.post("/")
async def create_article(
    create_article: Annotated[CreateArticle, Body()],
    user_id: Annotated[int, Cookie()],
    article_service: Annotated[ArticleService, Depends(ArticleService)]
) -> Article:
    return article_service.create_article(create_article, user_id)
