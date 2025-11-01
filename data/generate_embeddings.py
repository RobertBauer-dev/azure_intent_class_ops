import os
import json
import numpy as np
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()

# To logs?
print(os.getenv("AZURE_OPENAI_APIVERSION"))
print(os.getenv("EMB_MODEL_DEPLOY_TARGET_URI"))
print(os.getenv("EMB_MODEL"))
print(os.getenv("EMB_DIM"))

# Hole API-Key aus ENV
client = AzureOpenAI(
    api_version=os.getenv("AZURE_OPENAI_APIVERSION"),
    azure_endpoint=os.getenv("EMB_MODEL_DEPLOY_TARGET_URI"),
    api_key=os.getenv("EMB_MODEL_DEPLOY_KEY")
)

# Zeige verfügbare Deployments
"""print("\nVerfügbare Deployments:")
deployments = client.models.list()
for model in deployments:
    print(f"  - {model.id}")"""

# Lade Dataset
with open("data/input/intents.json") as f:
    INTENTS = json.load(f)

all_texts = []
all_labels = []

for label, texts in INTENTS.items():
    for t in texts:
        all_texts.append(t)
        all_labels.append(label)

# Embeddings holen
def embed_texts(texts):
    response = client.embeddings.create(
        model=os.getenv("EMB_MODEL"),
        input=texts,
        dimensions=int(os.getenv("EMB_DIM"))
    )
    return [d.embedding for d in response.data]

embeddings = embed_texts(all_texts)

# Speicher Embeddings & Labels
np.save("data/embeddings/embeddings.npy", np.array(embeddings))

with open("data/embeddings/labels.json", "w") as f:
    json.dump(all_labels, f, indent=2)

print("✅ Embeddings gespeichert")