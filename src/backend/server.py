from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Any, Dict, List
import uvicorn

from src.backend.puzzle_state import PuzzleEngine

app = FastAPI(
    title="The Midnight Audit (1928) — Local Daemon Bridge",
    description="Bridge connecting 1990s Excel VBA Client with 2026 Kiro Agent Mastermind.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = PuzzleEngine()

class EventRequest(BaseModel):
    event_type: str
    cell: Optional[str] = None
    value: Optional[Any] = None
    button: Optional[str] = None

class HauntRequest(BaseModel):
    haunt_type: str
    target_cell: Optional[str] = None
    message: Optional[str] = None

class BanishRequest(BaseModel):
    phrase: str

@app.get("/")
def root():
    return {
        "service": "The Midnight Audit (1928) Local Daemon Bridge",
        "status": "haunting",
        "phase": engine.phase_number,
        "phase_name": engine.current_phase.value
    }

@app.get("/api/status")
def get_status():
    return engine.get_state()

@app.post("/api/event")
def handle_event(req: EventRequest):
    event = req.event_type.lower()
    
    if event == "cell_change":
        if not req.cell:
            raise HTTPException(status_code=400, detail="Missing cell coordinate for cell_change event.")
        res = engine.handle_cell_change(req.cell, req.value)
    elif event in ["reagent_spray", "spray_reagent"] or (event == "button_click" and req.button == "SPRAY_REAGENT"):
        res = engine.handle_reagent_spray()
    elif event == "banish":
        res = engine.judge_ritual(str(req.value or ""))
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
    return engine.get_pixel_radar()

@app.post("/api/haunt")
def queue_haunt(req: HauntRequest):
    engine.queue_haunt(req.haunt_type, req.target_cell, req.message)
    return {"queued": True, "message": "Spectral haunt queued for dispatch."}

@app.post("/api/banish")
def banish(req: BanishRequest):
    return engine.judge_ritual(req.phrase)

@app.post("/api/reset")
def reset_game():
    global engine
    engine = PuzzleEngine()
    return {"reset": True, "phase": 1}

if __name__ == "__main__":
    uvicorn.run("src.backend.server:app", host="127.0.0.1", port=8000, reload=False)
