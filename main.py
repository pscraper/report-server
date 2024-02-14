import uvicorn
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database.connection import conn
from route.user_router import router as user_router
from route.article_router import router as article_router


# 생명주기 -> app.on_event: Deprecated
@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    conn()
    logging.info("startup")
    
    # 라우터 등록
    app.include_router(user_router, prefix="/user")
    app.include_router(article_router, prefix="/article")
    
    yield
    

app = FastAPI(lifespan=lifespan)    

# 미들웨어 등록
app.add_middleware(
    middleware_class=CORSMiddleware,
    
    # 교차 출처 요청을 보낼 수 있는 출처의 리스트
    allow_origins=["http://localhost:3000"],
    
    # 교차 출처 요청시 쿠키 지원 여트
    # 해당 설정이 True인 경우 origins는 모든 출처를 허용할 수 없다
    # -> allow_origins: ["*"] 불가, 출처를 특정해야 함 
    allow_credentials=True,    
    
    # 교차 출처 요청을 허용하는 HTTP 메소드 리스트, Default: ['GET']
    allow_methods=["*"],
    
    # 교차 출처를 지원하는 HTTP 요청 헤더 리스트, Default: []
    # Accept, Accept-Language, Content-Language, Contet-Type 헤더는 CORS 요청시 언제나 허용됨.
    allow_headers=["*"]
)


def run():
    uvicorn.run(app="main:app", host="127.0.0.1", port=8000, reload=True, workers=1)


if __name__ == "__main__":
    run()