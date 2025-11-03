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
from model.chat_model import chat_client
from model.fallback_promt import INTENT_DESCRIPTIONS, build_fallback_prompt


load_dotenv()

# Laden - use absolute paths relative to project root
clf = joblib.load(config.PROJECT_ROOT / "model/artifacts/model.pkl")
le = joblib.load(config.PROJECT_ROOT / "model/artifacts/label_encoder.pkl")
index = faiss.read_index(str(config.PROJECT_ROOT / "data/vector_db/faiss.index"))


# Thresholds
CLF_THRESHOLD = float(os.getenv("CLF_THRESHOLD"))
RETRIEVAL_THRESHOLD = float(os.getenv("RETRIEVAL_THRESHOLD")) # abhängig von embedding-Dimension & Distanz-Metrik


def llm_fallback(text):
    prompt = INTENT_DESCRIPTIONS + "\n" + build_fallback_prompt(text)
    r = chat_client.chat.completions.create(
        model=os.getenv("CHAT_MODEL"),
        messages=[{"role": "system", "content": prompt}]
    )
    return r.choices[0].message.content.strip()


def predict_intent(text):

    emb = embed_query(text)

    # Klassischer ML-Pred
    class_pred = clf.predict(emb)[0]
    class_conf = max(clf.predict_proba(emb)[0])

    clf_intent = le.inverse_transform([class_pred])[0]

    # Retrieval
    D, I = index.search(emb.astype("float32"), 1)
    retrieval_intent = le.inverse_transform([clf.predict(emb)[0]])[0]
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
        "retrieval_intent": retrieval_intent,
        "retrieval_distance": retrieval_distance,
        "fallback_used": fallback_used
    }

if __name__ == "__main__":
    #test = "Ich wurde doppelt abgebucht"
    test = "Mein Passwort funktioniert nicht und ich kann mich nicht einloggen."
    print(predict_intent(test))