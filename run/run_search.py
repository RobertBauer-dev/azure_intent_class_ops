import faiss
import numpy as np
import json
from openai import AzureOpenAI
import os
from dotenv import load_dotenv

load_dotenv()

# To logs?
print(os.getenv("AZURE_OPENAI_APIVERSION"))
print(os.getenv("EMB_MODEL_DEPLOY_TARGET_URI"))
print(os.getenv("EMB_MODEL"))
print(os.getenv("EMB_DIM"))


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

# Lade FAISS Index
index = faiss.read_index("data/vector_db/faiss.index")

# Labels
with open("data/embeddings/labels.json") as f:
    labels = json.load(f)

if __name__ == "__main__":
    query = "Ich wurde doppelt abgebucht"
    q_emb = embed_query(query)

    D, I = index.search(q_emb, 3)

    print("Anfrage:", query)
    print("Top Treffer:")

    for idx in I[0]:
        print(" -", labels[idx])