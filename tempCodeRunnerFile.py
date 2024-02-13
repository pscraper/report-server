@app.post("/cookie")
async def create_cookie():
    content = {"message": "hi"}
    response = JSONResponse(content)
    response.set_cookie(key="fake", value="fake value")
    return response