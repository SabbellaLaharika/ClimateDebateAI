from fastapi.testclient import TestClient
from unittest.mock import patch
from main import app
from agents.debater import DebateMessage
from datetime import datetime, timezone

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_get_policy_usa():
    response = client.get("/policies/usa")
    assert response.status_code == 200
    assert response.json()["country"] == "USA"
    assert "key_positions" in response.json()

def test_get_policy_invalid():
    response = client.get("/policies/invalid_country")
    assert response.status_code == 404

@patch("main.generate_turn")
def test_debate_start_logic(mock_generate_turn):
    # Mock the generate_turn to avoid calling the actual LLM during fast unit tests
    def side_effect(agent, round_num, topic, history):
        return DebateMessage(
            round=round_num,
            agent=agent,
            message=f"Mocked response from {agent}",
            stance="supportive",
            timestamp=datetime.now(timezone.utc).isoformat()
        )
    mock_generate_turn.side_effect = side_effect

    # Start a 2-round debate
    response = client.post("/debate/start", json={"topic": "Test Topic", "rounds": 2})
    
    assert response.status_code == 200
    data = response.json()
    assert "messages" in data
    
    messages = data["messages"]
    
    # Verify requirement 7: Total messages = rounds (2) * agents (3) = 6
    assert len(messages) == 6
    
    # Verify requirement 8: Fixed turn order (USA -> EU -> China)
    expected_agents = ["USA", "EU", "China", "USA", "EU", "China"]
    for i, msg in enumerate(messages):
        assert msg["agent"] == expected_agents[i]
        
        # Verify requirement 9: Message structure schema
        assert "round" in msg
        assert "message" in msg
        assert "stance" in msg
        assert "timestamp" in msg
        assert msg["stance"] in ["supportive", "opposed", "neutral"]
        
        # Verify correct round numbers
        if i < 3:
            assert msg["round"] == 1
        else:
            assert msg["round"] == 2
