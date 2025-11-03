import sys
from pathlib import Path

# Set up project path before importing config
_project_root = Path(__file__).parent.parent.resolve()
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

import faiss
import json
from dotenv import load_dotenv

import config
from model.embedding_model import embed_query

load_dotenv()

# Lade FAISS Index
index = faiss.read_index(str(config.PROJECT_ROOT / "data/vector_db/faiss.index"))

# Labels
with open(config.PROJECT_ROOT / "data/embeddings/labels.json") as f:
    labels = json.load(f)

if __name__ == "__main__":
    query = "Ich wurde doppelt abgebucht"
    q_emb = embed_query(query)

    D, I = index.search(q_emb, 3)

    print("Anfrage:", query)
    print("Top Treffer:")

    for idx in I[0]:
        print(" -", labels[idx])