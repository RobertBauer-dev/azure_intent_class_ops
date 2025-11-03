import os
import sys
import json
import numpy as np
from pathlib import Path
from openai import AzureOpenAI
from dotenv import load_dotenv

# Set up project path before importing config
_project_root = Path(__file__).parent.parent.resolve()
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

import config
from model.embedding_model import embed_texts

load_dotenv()

# Lade Dataset
with open(config.PROJECT_ROOT / "data/input/intents.json") as f:
    INTENTS = json.load(f)

all_texts = []
all_labels = []

for label, texts in INTENTS.items():
    for t in texts:
        all_texts.append(t)
        all_labels.append(label)


embeddings = embed_texts(all_texts)

# Speicher Embeddings & Labels
np.save(config.PROJECT_ROOT / "data/embeddings/embeddings.npy", np.array(embeddings))

with open(config.PROJECT_ROOT / "data/embeddings/labels.json", "w") as f:
    json.dump(all_labels, f, indent=2)

print("✅ Embeddings gespeichert")