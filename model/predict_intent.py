import numpy as np
import joblib
import faiss
import os
import json
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()

# Laden
clf = joblib.load("model/artifacts/model.pkl")
le = joblib.load("model/artifacts/label_encoder.pkl")
index = faiss.read_index("data/vector_db/faiss.index")

client = AzureOpenAI(
    api_version=os.getenv("AZURE_OPENAI_APIVERSION"),
    azure_endpoint=os.getenv("EMB_MODEL_DEPLOY_TARGET_URI"),
    api_key=os.getenv("EMB_MODEL_DEPLOY_KEY")
)


def embed_query(q):
    r = client.embeddings.create(
        model=os.getenv("EMB_MODEL"),
        input=q,
        dimensions=int(os.getenv("EMB_DIM"))
    )
    return np.array(r.data[0].embedding, dtype="float32").reshape(1, -1)


def predict_intent(text):
    emb = embed_query(text)

    # Klassischer ML-Pred
    class_pred = clf.predict(emb)[0]
    class_conf = max(clf.predict_proba(emb)[0])

    # FAISS-Retrieval
    D, I = index.search(emb.astype("float32"), 1)
    faiss_label = le.inverse_transform([clf.predict(emb)[0]])[0]

    return {
        "clf_prediction": le.inverse_transform([class_pred])[0],
        "clf_confidence": float(class_conf),
        "retrieval_label": faiss_label,
        "retrieval_distance": float(D[0][0])
    }

if __name__ == "__main__":
    test = "Ich wurde doppelt abgebucht"
    print(predict_intent(test))