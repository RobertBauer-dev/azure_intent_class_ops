import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import faiss
import joblib

# Set up project path before importing config
_project_root = Path(__file__).parent.parent.resolve()
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

import config
from model.embedding_model import embed_query
from model.chat_model import llm_fallback


load_dotenv()

# Globale Variablen für Lazy Loading
clf = None # classifier
le = None # label encoder
index = None # FAISS index

def _load_models():
    """Lade Modelle beim ersten Aufruf (Lazy Loading)"""
    global clf, le, index
    if clf is None or le is None or index is None:
        try:
            print(f"Loading models from: {config.PROJECT_ROOT}")
            print(f"Checking if files exist...")
            print(f"model.pkl exists: {(config.PROJECT_ROOT / 'model/artifacts/model.pkl').exists()}")
            print(f"label_encoder.pkl exists: {(config.PROJECT_ROOT / 'model/artifacts/label_encoder.pkl').exists()}")
            print(f"faiss.index exists: {(config.PROJECT_ROOT / 'data/vector_db/faiss.index').exists()}")
            
            clf = joblib.load(config.PROJECT_ROOT / "model/artifacts/model.pkl")
            print("✓ model.pkl loaded")
            
            le = joblib.load(config.PROJECT_ROOT / "model/artifacts/label_encoder.pkl")
            print("✓ label_encoder.pkl loaded")
            
            index = faiss.read_index(str(config.PROJECT_ROOT / "data/vector_db/faiss.index"))
            print("✓ faiss.index loaded")
        except Exception as e:
            print(f"ERROR loading models: {e}")
            print(f"Error type: {type(e).__name__}")
            import traceback
            traceback.print_exc()
            raise

# Thresholds (confidence thresholds for classifier and retrieval)
CLF_THRESHOLD = float(os.getenv("CLF_THRESHOLD", 0.60))
RETRIEVAL_THRESHOLD = float(os.getenv("RETRIEVAL_THRESHOLD", 1.2)) # dependent on embedding dimension & distance metric


def predict_intent(text) -> dict:
    # Load models on first call (Lazy Loading)
    _load_models()

    emb = embed_query(text)

    # Classical ML-Prediction
    class_pred = clf.predict(emb)[0] # integer
    clf_intent = le.inverse_transform([class_pred])[0] # string
    # Confidence of the classifier prediction
    class_conf = max(clf.predict_proba(emb)[0])

    # Retrieval
    D, _ = index.search(emb.astype("float32"), 1) # D: distance, _: index
    retrieval_distance = float(D[0][0])

    # Decision Logic
    fallback_used = False
    final_intent = clf_intent

    if class_conf < CLF_THRESHOLD or retrieval_distance > RETRIEVAL_THRESHOLD:
        fallback_used = True
        final_intent = llm_fallback(text)

    return {
        "text": text,
        "intent": final_intent,
        "clf_intent": clf_intent,
        "clf_confidence": float(class_conf),
        "retrieval_intent": clf_intent,
        "retrieval_distance": retrieval_distance,
        "fallback_used": fallback_used
    }

if __name__ == "__main__":
    #test = "Ich wurde doppelt abgebucht"
    test = "Mein Passwort funktioniert nicht und ich kann mich nicht einloggen."
    result = predict_intent(test)
    print(result)
    print(f"Intent: {result['intent']}")
    print(f"CLF Intent: {result['clf_intent']}")
    print(f"CLF Confidence: {result['clf_confidence']}")
    print(f"Retrieval Intent: {result['retrieval_intent']}")
    print(f"Retrieval Distance: {result['retrieval_distance']}")
    print(f"Fallback Used: {result['fallback_used']}")