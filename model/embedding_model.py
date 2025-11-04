from openai import AzureOpenAI
import os
from dotenv import load_dotenv
import numpy as np
import logging

logger = logging.getLogger(__name__)

load_dotenv()
logger.info("Environment loaded")

azure_endpoint=os.getenv("EMB_ENDPOINT_BASE")   #("EMB_MODEL_DEPLOY_TARGET_URI")
azure_deployment=os.getenv("EMB_MODEL_DEPLOY_NAME")
api_version=os.getenv("AZURE_OPENAI_APIVERSION")

logger.info(f"Azure endpoint: {azure_endpoint}")
logger.info(f"Azure deployment: {azure_deployment}")
logger.info(f"API version: {api_version}")

embed_client = AzureOpenAI(
    azure_endpoint=azure_endpoint,
    azure_deployment=azure_deployment,
    api_version=api_version,
    api_key=os.getenv("EMB_MODEL_DEPLOY_KEY")
)

if not embed_client.api_key:
    raise ValueError("EMB_MODEL_DEPLOY_KEY environment variable is not set")

logger.info("Embedding client created")

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
