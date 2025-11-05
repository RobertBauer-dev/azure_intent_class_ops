import sys
from pathlib import Path

# Ensure project root is in Python path
_project_root = Path(__file__).parent.parent.parent.resolve()
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from model.predict_intent import predict_intent

def test_basic_intent():
    result = predict_intent("Ich kann mich nicht einloggen")
    assert result["intent"] in [
        "login_problems", "general_question"
    ]
    assert "clf_confidence" in result

def test_fallback_trigger():
    result = predict_intent("Was kostet die Erde?")
    assert result["fallback_used"] is True