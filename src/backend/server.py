import sys
import os
import re

# Ensure project root is in sys.path so server can be executed directly
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from urllib.parse import urlparse
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Any
import uvicorn

from src.backend.puzzle_state import PuzzleEngine, PhaseEnum, file_lock

app = FastAPI(
    title="The Midnight Audit (1928) — Local Daemon Bridge",
    description="Bridge connecting 1990s Excel VBA Client with 2026 Kiro Agent Mastermind.",
    version="1.3.0"
)

class SecurityHeadersAndOriginMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        origin = request.headers.get("origin")
        if origin:
            host = (urlparse(origin).hostname or "").lower()
            if host not in {"localhost", "127.0.0.1", "::1"}:
                return JSONResponse(
                    status_code=403,
                    content={"detail": "Cross-origin requests from untrusted origins are forbidden."}
                )

        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Content-Security-Policy"] = "default-src 'none'"
        response.headers["Referrer-Policy"] = "no-referrer"
        return response

app.add_middleware(SecurityHeadersAndOriginMiddleware)

engine = PuzzleEngine(load_existing=True)

class EventRequest(BaseModel):
    event_type: str = Field(..., max_length=50)
    cell: Optional[str] = Field(None, max_length=30)
    value: Optional[Any] = None
    button: Optional[str] = Field(None, max_length=50)

    @field_validator("value")
    @classmethod
    def validate_value_size(cls, v):
        if v is not None:
            if isinstance(v, str) and len(v) > 2000:
                raise ValueError("Value string exceeds maximum allowed length of 2000 characters.")
            elif not isinstance(v, (int, float, bool, str)):
                if len(str(v)) > 2000:
                    raise ValueError("Value payload exceeds maximum allowed size.")
        return v

class HauntRequest(BaseModel):
    haunt_type: str = Field(..., max_length=50)
    target_cell: Optional[str] = Field(None, max_length=30)
    message: Optional[str] = Field(None, max_length=2000)

class BanishRequest(BaseModel):
    phrase: str = Field(..., max_length=500)

@app.get("/")
def root():
    engine.load_state()
    return {
        "service": "The Midnight Audit (1928) Local Daemon Bridge",
        "status": "haunting",
        "phase": engine.phase_number,
        "phase_name": engine.current_phase.value
    }

@app.get("/api/status")
def get_status():
    engine.load_state()
    return engine.get_state()

@app.post("/api/event")
def handle_event(req: EventRequest):
    with file_lock():
        engine.load_state()
        event = req.event_type.lower()
        
        if event == "cell_change":
            if not req.cell:
                raise HTTPException(status_code=400, detail="Missing cell coordinate for cell_change event.")
            cell_clean = req.cell.strip().upper()
            if not re.match(r"^[A-Z]{1,3}\d{1,5}(?::[A-Z]{1,3}\d{1,5})?$", cell_clean):
                raise HTTPException(status_code=400, detail="Invalid cell coordinate.")
            res = engine.handle_cell_change(cell_clean, req.value)
        elif event in ["reagent_spray", "spray_reagent"] or (event == "button_click" and req.button == "SPRAY_REAGENT"):
            res = engine.handle_reagent_spray()
        elif event == "banish":
            phrase = str(req.value or "").strip()
            res = engine.judge_ritual(phrase)
        else:
            res = {
                "accepted": False,
                "current_phase": engine.phase_number,
                "message": f"Unknown event type: {req.event_type}"
            }

        # Append any queued haunt actions to response
        pending = engine.pop_pending_effects()
        if pending:
            actions = res.get("actions", [])
            for p in pending:
                actions.append({
                    "command": "TRIGGER_HAUNT",
                    "haunt_type": p["type"],
                    "cell": p["target_cell"],
                    "message": p["message"]
                })
            res["actions"] = actions

        return res

@app.get("/api/pixel_radar")
def get_pixel_radar():
    engine.load_state()
    return engine.get_pixel_radar()

@app.post("/api/haunt")
def queue_haunt(req: HauntRequest):
    with file_lock():
        engine.load_state()
        try:
            engine.queue_haunt(req.haunt_type, req.target_cell, req.message)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        return {"queued": True, "message": "Spectral haunt queued for dispatch."}

@app.post("/api/banish")
def banish(req: BanishRequest):
    with file_lock():
        engine.load_state()
        return engine.judge_ritual(req.phrase)

@app.post("/api/reset")
def reset_game():
    global engine
    with file_lock():
        engine = PuzzleEngine()
        engine.save_state()
        return {"reset": True, "phase": 1}

if __name__ == "__main__":
    port = int(os.environ.get("SERVER_PORT", "8000"))
    uvicorn.run("src.backend.server:app", host="127.0.0.1", port=port, reload=False)
