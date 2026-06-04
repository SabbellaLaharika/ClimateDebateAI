import os
import requests
import re
from datetime import datetime, timezone
from pydantic import BaseModel
from typing import List

from core.rag_service import rag_service

OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
LLM_MODEL_NAME = os.environ.get("LLM_MODEL_NAME", "llama3:8b")

class DebateMessage(BaseModel):
    round: int
    agent: str
    message: str
    stance: str
    timestamp: str

def generate_response(agent: str, topic: str, history: List[DebateMessage]) -> str:
    query = topic
    if history:
        query += " " + history[-1].message
    
    retrieved_points = rag_service.retrieve(agent, query)
    context_str = "\n".join(f"- {p}" for p in retrieved_points) if retrieved_points else "No specific policy points found."

    history_str = ""
    for msg in history:
        history_str += f"{msg.agent} (Round {msg.round}): {msg.message}\n"

    prompt = f"""Persona: You are the debate representative for {agent}.
Context: You are debating the topic: {topic}. 
Here is the debate history so far:
{history_str}

Instructions: Your response must be based on your country's official policy points:
{context_str}

Format Constraints: Your response must be a single paragraph. Conclude your response by stating your stance explicitly as either 'supportive', 'opposed', or 'neutral'."""

    payload = {
        "model": LLM_MODEL_NAME,
        "prompt": prompt,
        "stream": False
    }
    
    try:
        response = requests.post(f"{OLLAMA_BASE_URL}/api/generate", json=payload)
        response.raise_for_status()
        data = response.json()
        return data.get("response", "")
    except Exception as e:
        print(f"Error calling LLM: {e}")
        return "I am unable to respond at this time due to a technical error. My stance is neutral."

def generate_turn(agent: str, round_num: int, topic: str, history: List[DebateMessage]) -> DebateMessage:
    response_text = generate_response(agent, topic, history)
    
    stance = "neutral"
    lower_resp = response_text.lower()
    
    # Try to find the exact stance word at the end of the text
    matches = re.findall(r'\b(supportive|opposed|neutral)\b', lower_resp)
    if matches:
        stance = matches[-1] # Take the last occurrence
        
    return DebateMessage(
        round=round_num,
        agent=agent,
        message=response_text.strip(),
        stance=stance,
        timestamp=datetime.now(timezone.utc).isoformat()
    )
