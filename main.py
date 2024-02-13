import uvicorn
from fastapi import FastAPI, Response
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from database.connection import conn
from route.user import router as user_router


app = FastAPI()
app.include_router(user_router, prefix="/user")
app.add_middleware(
    CORSMiddleware,
    
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


@app.on_event("startup")
def startup():
    conn()
    
    
@app.post("/cookie")
async def create_cookie():
    content = {"message": "hi"}
    response = JSONResponse(content)
    response.set_cookie(key="fake", value="fake value")
    return response


def run():
    uvicorn.run(app="main:app", host="127.0.0.1", port=8000, reload=True, workers=1)


if __name__ == "__main__":
    run()