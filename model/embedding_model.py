from openai import AzureOpenAI
import os
from dotenv import load_dotenv
import numpy as np

load_dotenv()

embed_client = AzureOpenAI(
    api_version=os.getenv("AZURE_OPENAI_APIVERSION"),
    azure_endpoint=os.getenv("EMB_MODEL_DEPLOY_TARGET_URI"),
    api_key=os.getenv("EMB_MODEL_DEPLOY_KEY")
)

def embed_query(q):
    r = embed_client.embeddings.create(
        model=os.getenv("EMB_MODEL"),
        input=q,
        dimensions=int(os.getenv("EMB_DIM"))
    )
    return np.array(r.data[0].embedding, dtype="float32").reshape(1, -1)

def embed_texts(texts):
    r = embed_client.embeddings.create(
        model=os.getenv("EMB_MODEL"),
        input=texts,
        dimensions=int(os.getenv("EMB_DIM"))
    )
    return [d.embedding for d in r.data]