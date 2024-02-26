from fastapi import APIRouter, Body, Cookie, Depends
from typing import Annotated
from model.article import Article, CreateArticle
from config.transaction_route import TransactionRoute


router = APIRouter(route_class = TransactionRoute)
