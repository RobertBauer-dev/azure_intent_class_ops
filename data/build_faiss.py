from turtle import clear
import faiss
import numpy as np
import json

# Lade Embeddings und Labels
embeddings = np.load("data/embeddings/embeddings.npy").astype("float32")

with open("labels.json") as f:
    labels = json.load(f)

dimension = embeddings.shape[1]

# FAISS Index aufbauen
index = faiss.IndexFlatL2(dimension)
index.add(embeddings)

faiss.write_index(index, "data/vector_db/faiss.index")

print("✅ FAISS Index gespeichert:", embeddings.shape)