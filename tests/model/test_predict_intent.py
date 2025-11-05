import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
import numpy as np

# Ensure project root is in Python path
_project_root = Path(__file__).parent.parent.parent.resolve()
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from model.predict_intent import predict_intent


def test_basic_intent():
    """Test basic intent prediction with mocked dependencies."""
    # Mock embedding
    mock_embedding = np.random.rand(512).astype(np.float32)
    
    # Mock classifier with high confidence
    mock_clf = MagicMock()
    mock_clf.predict.return_value = np.array([0])  # login_problems
    mock_clf.predict_proba.return_value = np.array([[0.85, 0.15]])  # High confidence
    
    # Mock label encoder
    mock_le = MagicMock()
    mock_le.inverse_transform.return_value = np.array(["login_problems"])
    
    # Mock FAISS index with low distance
    mock_index = MagicMock()
    mock_index.search.return_value = (np.array([[0.5]]), np.array([[0]]))
    
    with patch("model.predict_intent.embed_query", return_value=mock_embedding.reshape(1, -1)), \
         patch("model.predict_intent._load_models"):
        # Set the global variables directly
        import model.predict_intent as predict_module
        predict_module.clf = mock_clf
        predict_module.le = mock_le
        predict_module.index = mock_index
        
        result = predict_intent("Ich kann mich nicht einloggen")
        
        assert result["intent"] in ["login_problems", "general_question"]
        assert "clf_confidence" in result
        assert result["clf_confidence"] > 0.5


def test_fallback_trigger():
    """Test that fallback is triggered when confidence is low."""
    # Mock embedding
    mock_embedding = np.random.rand(512).astype(np.float32)
    
    # Mock classifier with low confidence
    mock_clf = MagicMock()
    mock_clf.predict.return_value = np.array([0])
    mock_clf.predict_proba.return_value = np.array([[0.4, 0.6]])  # Low confidence
    
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