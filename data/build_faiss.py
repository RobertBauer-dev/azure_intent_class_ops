import sys
from pathlib import Path

# Set up project path before importing config
_project_root = Path(__file__).parent.parent.resolve()
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from turtle import clear
import faiss
import numpy as np
import json

import config

# Lade Embeddings und Labels
embeddings = np.load(config.PROJECT_ROOT / "data/embeddings/embeddings.npy").astype("float32")

with open(config.PROJECT_ROOT / "data/embeddings/labels.json") as f:
    labels = json.load(f)

dimension = embeddings.shape[1]

# FAISS Index aufbauen
index = faiss.IndexFlatL2(dimension)
index.add(embeddings)

faiss.write_index(index, str(config.PROJECT_ROOT / "data/vector_db/faiss.index"))

print("✅ FAISS Index gespeichert:", embeddings.shape)