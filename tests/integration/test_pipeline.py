"""
End-to-end pipeline integration tests.
Tests the complete prediction pipeline with mocked external services.
"""
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
import numpy as np

# Ensure project root is in Python path
_project_root = Path(__file__).parent.parent.parent.resolve()
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from model.predict_intent import predict_intent


class MockEmbeddingResponse:
    """Mock response for embedding API."""
    def __init__(self, embedding):
        self.data = [MagicMock(embedding=embedding)]


class MockChatResponse:
    """Mock response for chat completion API."""
    def __init__(self, content):
        self.choices = [MagicMock(message=MagicMock(content=content))]


def test_pipeline_with_high_confidence():
    """Test the complete pipeline when classifier has high confidence."""
    # Mock embedding
    mock_embedding = np.random.rand(1536).astype(np.float32)
    
    # Mock classifier
    mock_clf = MagicMock()
    mock_clf.predict.return_value = np.array([0])  # login_problems
    mock_clf.predict_proba.return_value = np.array([[0.9, 0.1]])  # High confidence
    
    # Mock label encoder
    mock_le = MagicMock()
    mock_le.inverse_transform.return_value = np.array(["login_problems"])
    
    # Mock FAISS index
    mock_index = MagicMock()
    mock_index.search.return_value = (np.array([[0.3]]), np.array([[0]]))  # Low distance
    
    with patch("model.predict_intent.embed_query", return_value=mock_embedding.reshape(1, -1)), \
         patch("model.predict_intent._load_models"):  # Skip model loading
        # Set the global variables directly
        import model.predict_intent as predict_module
        predict_module.clf = mock_clf
        predict_module.le = mock_le
        predict_module.index = mock_index
        
        result = predict_intent("Ich kann mich nicht einloggen")
        
        assert result["intent"] == "login_problems"
        assert result["clf_confidence"] == 0.9
        assert result["fallback_used"] is False
        assert "retrieval_distance" in result


def test_pipeline_with_low_confidence_triggers_fallback():
    """Test the pipeline when low confidence triggers LLM fallback."""
    mock_embedding = np.random.rand(1536).astype(np.float32)
    
    # Mock classifier with low confidence
    mock_clf = MagicMock()
    mock_clf.predict.return_value = np.array([0])
    mock_clf.predict_proba.return_value = np.array([[0.5, 0.5]])  # Low confidence
    
    # Mock label encoder
    mock_le = MagicMock()
    mock_le.inverse_transform.return_value = np.array(["general_question"])
    
    # Mock FAISS index with high distance
    mock_index = MagicMock()
    mock_index.search.return_value = (np.array([[1.5]]), np.array([[0]]))  # High distance
    
    # Mock LLM fallback
    mock_llm_response = "general_question"
    
    with patch("model.predict_intent.embed_query", return_value=mock_embedding.reshape(1, -1)), \
         patch("model.predict_intent.llm_fallback", return_value=mock_llm_response), \
         patch("model.predict_intent._load_models"):
        # Set the global variables directly
        import model.predict_intent as predict_module
        predict_module.clf = mock_clf
        predict_module.le = mock_le
        predict_module.index = mock_index
        
        result = predict_intent("Was kostet die Erde?")
        
        assert result["fallback_used"] is True
        assert result["intent"] == "general_question"
        assert result["clf_confidence"] == 0.5


def test_pipeline_with_high_distance_triggers_fallback():
    """Test the pipeline when high retrieval distance triggers fallback."""
    mock_embedding = np.random.rand(1536).astype(np.float32)
    
    # Mock classifier with good confidence
    mock_clf = MagicMock()
    mock_clf.predict.return_value = np.array([0])
    mock_clf.predict_proba.return_value = np.array([[0.85, 0.15]])  # Good confidence
    
    # Mock label encoder
    mock_le = MagicMock()
    mock_le.inverse_transform.return_value = np.array(["general_question"])
    
    # Mock FAISS index with very high distance
    mock_index = MagicMock()
    mock_index.search.return_value = (np.array([[2.0]]), np.array([[0]]))  # Very high distance
    
    # Mock LLM fallback
    mock_llm_response = "general_question"
    
    with patch("model.predict_intent.embed_query", return_value=mock_embedding.reshape(1, -1)), \
         patch("model.predict_intent.llm_fallback", return_value=mock_llm_response), \
         patch("model.predict_intent._load_models"):
        # Set the global variables directly
        import model.predict_intent as predict_module
        predict_module.clf = mock_clf
        predict_module.le = mock_le
        predict_module.index = mock_index
        
        result = predict_intent("Some unusual query")
        
        # High distance should trigger fallback even with good confidence
        assert result["fallback_used"] is True
        assert result["retrieval_distance"] == 2.0


def test_pipeline_returns_all_expected_fields():
    """Test that the pipeline returns all expected fields in the result."""
    mock_embedding = np.random.rand(1536).astype(np.float32)
    
    mock_clf = MagicMock()
    mock_clf.predict.return_value = np.array([0])
    mock_clf.predict_proba.return_value = np.array([[0.8, 0.2]])
    
    mock_le = MagicMock()
    mock_le.inverse_transform.return_value = np.array(["login_problems"])
    
    mock_index = MagicMock()
    mock_index.search.return_value = (np.array([[0.5]]), np.array([[0]]))
    
    with patch("model.predict_intent.embed_query", return_value=mock_embedding.reshape(1, -1)), \
         patch("model.predict_intent._load_models"):
        # Set the global variables directly
        import model.predict_intent as predict_module
        predict_module.clf = mock_clf
        predict_module.le = mock_le
        predict_module.index = mock_index
        
        result = predict_intent("Test query")
        
        # Check all expected fields are present
        expected_fields = [
            "text", "intent", "clf_intent", "clf_confidence",
            "retrieval_intent", "retrieval_distance", "fallback_used"
        ]
        
        for field in expected_fields:
            assert field in result, f"Missing field: {field}"
        
        assert isinstance(result["clf_confidence"], float)
        assert isinstance(result["retrieval_distance"], float)
        assert isinstance(result["fallback_used"], bool)

