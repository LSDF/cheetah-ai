from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv
import uuid
import os
from pathlib import Path

from agent.core import CheetahAgent

load_dotenv()

app = FastAPI(title="Cheetah AI", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

agent = CheetahAgent()

FRONTEND_DIR = Path(__file__).parent / "frontend"

class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None
    mode: str = "private"

class ChatResponse(BaseModel):
    reply: str
    session_id: str

@app.get("/api")
def api_root():
    return {
        "name": "Cheetah AI",
        "status": "online",
        "version": "0.1.0",
        "capabilities": ["chat", "memory", "self-improvement (scaffolded)", "tools"]
    }

@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    session_id = req.session_id or str(uuid.uuid4())
    mode = req.mode if req.mode in ("private", "public") else "private"

    try:
        reply = agent.chat(session_id, req.message, mode)
        return ChatResponse(reply=reply, session_id=session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/improve")
def trigger_improvement():
    result = agent.improve_self()
    return result

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/")
async def serve_frontend():
    index_path = FRONTEND_DIR / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return {"error": "Frontend not found. Check deployment."}

if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")
