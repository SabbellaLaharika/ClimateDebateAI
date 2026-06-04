from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
import json
import os
from typing import List

from agents.debater import generate_turn, DebateMessage

app = FastAPI()

class DebateRequest(BaseModel):
    topic: str
    rounds: int = Field(ge=1, le=5)

class DebateResponse(BaseModel):
    messages: List[DebateMessage]

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/policies/{country_code}")
def get_policy(country_code: str):
    country_code = country_code.lower()
    if country_code not in ["usa", "eu", "china"]:
        raise HTTPException(status_code=404, detail="Country not found")
    
    filepath = f"data/policies/{country_code}_policy.json"
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Policy file missing")
        
    with open(filepath, "r") as f:
        return json.load(f)

@app.post("/debate/start", response_model=DebateResponse)
def start_debate(req: DebateRequest):
    agents = ["USA", "EU", "China"]
    history = []
    
    for round_num in range(1, req.rounds + 1):
        for agent in agents:
            try:
                turn = generate_turn(agent, round_num, req.topic, history)
                history.append(turn)
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
                
    return {"messages": history}

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def serve_index():
    return FileResponse("static/index.html")
