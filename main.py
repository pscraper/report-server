import uvicorn
from fastapi import FastAPI
from database.connection import conn
from route.user import router as user_router


app = FastAPI()
app.include_router(user_router, prefix="/user")


@app.on_event("startup")
def startup():
    conn()


def run():
    uvicorn.run(app="main:app", host="127.0.0.1", port=8000, reload=True, workers=1)


if __name__ == "__main__":
    run()