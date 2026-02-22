from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

from app.api.endpoints import router as api_router

app = FastAPI(title="Cerebras Document Generator")

# Include the endpoints router
app.include_router(api_router)

# Mount static files (will be created in next step)
try:
    app.mount("/static", StaticFiles(directory="static"), name="static")
except Exception:
    pass # Will mount successfully once we move CSS/JS

@app.get("/", response_class=HTMLResponse)
def serve_frontend():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return f.read()

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
