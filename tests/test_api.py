import pytest
from fastapi.testclient import TestClient
from src.api import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"

def test_get_rules_endpoint():
    response = client.get("/api/v1/rules")
    assert response.status_code == 200
    data = response.json()
    assert "rules" in data
    assert len(data["rules"]) >= 4

def test_post_rules_endpoint():
    payload = {
        "rules": [
            {
                "rule_id": "API-TEST-01",
                "category": "Confidentiality",
                "description": "NDAs must survive for 3 years post termination."
            }
        ]
    }
    response = client.post("/api/v1/rules", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"

def test_analyze_endpoint():
    file_data = b"Confidentiality agreement with perpetual duration and uncapped liability."
    response = client.post(
        "/api/v1/analyze",
        files={"file": ("nda_agreement.txt", file_data, "text/plain")}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "report" in data
    assert data["report"]["contract_title"] == "nda_agreement.txt"
    assert "overall_risk_score" in data["report"]
