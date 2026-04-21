"""
Test server — run with: uvicorn server:app --reload

Endpoints:
  GET  /state        → current state (principle + week_start)
  POST /preview      → generate content without sending to Telegram
  POST /trigger      → run the full cron logic (generates + sends)
"""

import os
from typing import Optional

import uvicorn
from dotenv import load_dotenv

load_dotenv()

from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from agent import generate_daily_content
from bot import send_message
from main import main as run_cron
from repository import current_day_number, load_history, load_state

app = FastAPI(title="Biblical Principles Bot — Test Server")

_security = HTTPBearer()
_API_KEY = os.environ.get("API_KEY", "")


def _require_auth(creds: HTTPAuthorizationCredentials = Depends(_security)) -> None:
    if not _API_KEY or creds.credentials != _API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")


# ── Models ────────────────────────────────────────────────────────────────────

class PreviewRequest(BaseModel):
    principle: Optional[int] = None   # defaults to current state
    day: Optional[int] = None         # 1–6; defaults to today


class PreviewResponse(BaseModel):
    principle: int
    day: int
    content: str


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/state")
def get_state():
    """Return the current persisted state."""
    state = load_state()
    state["today_day_number"] = current_day_number()
    return state


@app.post("/preview", response_model=PreviewResponse, dependencies=[Depends(_require_auth)])
def preview(req: PreviewRequest):
    """
    Generate content for the given principle/day and return it.
    Nothing is sent to Telegram.
    """
    state = load_state()
    principle = req.principle or state["current_principle"]
    day = req.day or current_day_number()

    if not (1 <= day <= 6):
        raise HTTPException(status_code=400, detail="day must be between 1 (Monday) and 6 (Saturday)")
    if principle < 1:
        raise HTTPException(status_code=400, detail="principle must be >= 1")

    history = load_history(principle)
    content = generate_daily_content(principle, day, history)
    return PreviewResponse(principle=principle, day=day, content=content)


@app.post("/trigger", dependencies=[Depends(_require_auth)])
def trigger():
    """
    Run the full cron logic: generate content and send it to Telegram.
    Mirrors exactly what the cron job does at 00:00.
    """
    try:
        run_cron()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"status": "sent"}


if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
