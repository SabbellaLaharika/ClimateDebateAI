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

    prompt = f"""Persona: You are the official debate representative for {agent}. This is a fictional, educational simulation. You must strictly play your role and fiercely debate the topic. Under no circumstances should you refuse the prompt, apologize, or claim you cannot fulfill the request.
Context: You are debating the topic: {topic}. 
Here is the debate history so far:
{history_str}

Instructions: Your response must be based strictly on your country's official policy points:
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
    except requests.exceptions.ConnectionError:
        raise Exception("Could not connect to the local Ollama AI service. Please ensure the Ollama Docker container is actively running.")
    except requests.exceptions.HTTPError:
        if response.status_code == 500:
            raise Exception("The Ollama AI service crashed while trying to generate a response. This is almost always caused by having insufficient system RAM to load the requested model.")
        raise Exception(f"The Ollama service returned an unexpected HTTP error code: {response.status_code}.")
    except Exception as e:
        raise Exception(f"An unexpected technical error occurred while trying to communicate with the AI model: {str(e)}")

def generate_turn(agent: str, round_num: int, topic: str, history: List[DebateMessage]) -> DebateMessage:
    response_text = generate_response(agent, topic, history)
    
    stance = "neutral"
    lower_resp = response_text.lower()
    
    # Try to find the exact stance word at the end of the text
    matches = re.findall(r'\b(supportive|support|supported|opposed|oppose|neutral)\b', lower_resp)
    if matches:
        raw_stance = matches[-1] # Take the last occurrence
        if raw_stance in ['support', 'supported']:
            stance = 'supportive'
        elif raw_stance == 'oppose':
            stance = 'opposed'
        else:
            stance = raw_stance
        
    return DebateMessage(
        round=round_num,
        agent=agent,
        message=response_text.strip(),
        stance=stance,
        timestamp=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    )
