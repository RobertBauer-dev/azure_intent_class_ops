"""
Integration tests for FastAPI endpoints.
Tests the API endpoints with mocked model dependencies.
"""
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Ensure project root is in Python path
_project_root = Path(__file__).parent.parent.parent.resolve()
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from fastapi.testclient import TestClient
from app.app import app


def test_root_endpoint():
    """Test the health check endpoint."""
    client = TestClient(app)
    response = client.get("/")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "running"
    assert "message" in data


def test_predict_endpoint_success():
    """Test the predict endpoint with a valid query."""
    client = TestClient(app)
    
    # Mock the predict_intent function
    mock_result = {
        "text": "Ich kann mich nicht einloggen",
        "intent": "login_problems",
        "clf_intent": "login_problems",
        "clf_confidence": 0.85,
        "retrieval_intent": "login_problems",
        "retrieval_distance": 0.5,
        "fallback_used": False
    }
    
    with patch("app.app.predict_intent", return_value=mock_result):
        response = client.post(
            "/predict",
            json={"text": "Ich kann mich nicht einloggen"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["intent"] == "login_problems"
        assert data["clf_confidence"] == 0.85
        assert data["fallback_used"] is False
        assert data["text"] == "Ich kann mich nicht einloggen"


def test_predict_endpoint_with_fallback():
    """Test the predict endpoint when fallback is used."""
    client = TestClient(app)
    
    mock_result = {
        "text": "Was kostet die Erde?",
        "intent": "general_question",
        "clf_intent": "general_question",
        "clf_confidence": 0.45,
        "retrieval_intent": "general_question",
        "retrieval_distance": 1.5,
        "fallback_used": True
    }
    
    with patch("app.app.predict_intent", return_value=mock_result):
        response = client.post(
            "/predict",
            json={"text": "Was kostet die Erde?"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["fallback_used"] is True
        assert data["clf_confidence"] < 0.60  # Below threshold


def test_predict_endpoint_empty_text():
    """Test the predict endpoint with empty text."""
    client = TestClient(app)
    
    response = client.post(
        "/predict",
        json={"text": ""}
    )
    
    # Should still return 200 but with a result
    assert response.status_code == 200


def test_predict_endpoint_invalid_json():
    """Test the predict endpoint with invalid JSON."""
    client = TestClient(app)
    
    response = client.post(
        "/predict",
        json={"invalid": "field"}
    )
    
    # Should return 422 validation error
    assert response.status_code == 422


def test_predict_endpoint_missing_text():
    """Test the predict endpoint without text field."""
    client = TestClient(app)
    
    response = client.post(
        "/predict",
        json={}
    )
    
    # Should return 422 validation error
    assert response.status_code == 422


def test_predict_endpoint_error_handling():
    """Test error handling when predict_intent raises an exception."""
    client = TestClient(app)
    
    with patch("app.app.predict_intent", side_effect=Exception("Model error")):
        response = client.post(
            "/predict",
            json={"text": "Test query"}
        )
        
        assert response.status_code == 200  # API returns 200 even on error
        data = response.json()
        assert "error" in data
        assert data["text"] == "Test query"


def test_predict_endpoint_multiple_queries():
    """Test multiple sequential queries to the predict endpoint."""
    client = TestClient(app)
    
    queries = [
        "Ich kann mich nicht einloggen",
        "Meine Zahlung wird abgelehnt",
        "Wie ändere ich meine E-Mail?"
    ]
    
    for query in queries:
        mock_result = {
            "text": query,
            "intent": "general_question",
            "clf_intent": "general_question",
            "clf_confidence": 0.75,
            "retrieval_intent": "general_question",
            "retrieval_distance": 0.8,
            "fallback_used": False
        }
        
        with patch("app.app.predict_intent", return_value=mock_result):
            response = client.post(
                "/predict",
                json={"text": query}
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["text"] == query

