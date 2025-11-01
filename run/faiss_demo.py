import faiss
import numpy as np

# Beispiel: 100 Embeddings mit 1536 Dimension
dimension = 1536
embeddings = np.random.rand(100, dimension).astype('float32')

# FAISS Index bauen
index = faiss.IndexFlatL2(dimension)
index.add(embeddings)

# Suche top 5 ähnlichste Embeddings
query = np.random.rand(1, dimension).astype('float32')
D, I = index.search(query, 5)
print("Top 5 ähnliche Einträge:", I)