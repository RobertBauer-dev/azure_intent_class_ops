"""
Component-level integration tests.
Tests individual components with mocked external dependencies.
"""
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
import numpy as np

# Ensure project root is in Python path
_project_root = Path(__file__).parent.parent.parent.resolve()
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))


def test_embed_query_function():
    """Test the embed_query function with mocked Azure OpenAI."""
    from model.embedding_model import embed_query
    
    # Mock embedding response
    mock_embedding = np.random.rand(1536).astype(np.float32)
    mock_response = MagicMock()
    mock_response.data = [MagicMock(embedding=mock_embedding.tolist())]
    
    # Mock the embeddings client
    with patch("model.embedding_model.embed_client") as mock_client:
        mock_client.embeddings.create.return_value = mock_response
        
        result = embed_query("Test query")
        
        assert result.shape == (1, 1536)  # Should be 2D array
        assert result.dtype == np.float32
        mock_client.embeddings.create.assert_called_once()


def test_llm_fallback_function():
    """Test the llm_fallback function with mocked Azure OpenAI."""
    from model.chat_model import llm_fallback
    
    # Mock chat completion response
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="general_question"))]
    
    # Mock the chat client
    with patch("model.chat_model.chat_client") as mock_client:
        mock_client.chat.completions.create.return_value = mock_response
        
        result = llm_fallback("Was kostet die Erde?")
        
        assert result == "general_question"
        mock_client.chat.completions.create.assert_called_once()
        
        # Check that prompt was passed correctly
        call_args = mock_client.chat.completions.create.call_args
        assert "messages" in call_args.kwargs
        assert len(call_args.kwargs["messages"]) == 1
        assert call_args.kwargs["messages"][0]["role"] == "system"
        assert "Was kostet die Erde?" in call_args.kwargs["messages"][0]["content"]


def test_fallback_prompt_building():
    """Test that the fallback prompt is built correctly."""
    from model.fallback_promt import build_fallback_prompt, INTENT_DESCRIPTIONS
    
    test_text = "Ich kann mich nicht einloggen"
    prompt = build_fallback_prompt(test_text)
    
    # build_fallback_prompt returns only the second part, not INTENT_DESCRIPTIONS
    # INTENT_DESCRIPTIONS is added separately in chat_model.py
    assert test_text in prompt
    assert "Classify" in prompt or "classify" in prompt.lower()
    assert "intents described above" in prompt.lower()
    
    # Verify that INTENT_DESCRIPTIONS and build_fallback_prompt can be combined
    # (as done in chat_model.py)
    full_prompt = INTENT_DESCRIPTIONS + "\n" + prompt
    assert INTENT_DESCRIPTIONS in full_prompt
    assert test_text in full_prompt


def test_model_loading_with_missing_files():
    """Test that model loading handles missing files gracefully."""
    from model.predict_intent import _load_models
    
    # Mock file system to return False for all files
    with patch("pathlib.Path.exists", return_value=False):
        try:
            _load_models()
            assert False, "Should have raised an exception"
        except Exception as e:
            # Should raise an error when files don't exist
            assert True


def test_embed_query_with_different_dimensions():
    """Test embed_query with different embedding dimensions."""
    from model.embedding_model import embed_query
    
    # Test with different dimensions
    for dim in [128, 256, 512, 1536]:
        mock_embedding = np.random.rand(dim).astype(np.float32)
        mock_response = MagicMock()
        mock_response.data = [MagicMock(embedding=mock_embedding.tolist())]
        
        with patch("model.embedding_model.embed_client") as mock_client, \
             patch("model.embedding_model.os.getenv") as mock_getenv:
            mock_getenv.side_effect = lambda key, default=None: {
                "EMB_DIM": str(dim)
            }.get(key, default)
            
            mock_client.embeddings.create.return_value = mock_response
            
            result = embed_query("Test")
            
            assert result.shape == (1, dim)
            assert result.dtype == np.float32

