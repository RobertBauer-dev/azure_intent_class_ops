from openai import AzureOpenAI
import os
from dotenv import load_dotenv
import logging

from model.fallback_promt import INTENT_DESCRIPTIONS, build_fallback_prompt

logger = logging.getLogger(__name__)

load_dotenv()
logger.info("Environment loaded")

api_version=os.getenv("AZURE_OPENAI_APIVERSION")
azure_endpoint=os.getenv("CHAT_ENDPOINT_URI")

logger.info(f"API version: {api_version}")
logger.info(f"Azure endpoint: {azure_endpoint}")

chat_client = AzureOpenAI(
    api_version=api_version,
    azure_endpoint=azure_endpoint,
    api_key=os.getenv("CHAT_ENDPOINT_KEY") # AZURE_OPENAI_KEY1
)

if not chat_client.api_key:
    raise ValueError("CHAT_ENDPOINT_KEY environment variable is not set")

logger.info("Chat client created")


def llm_fallback(text):
    prompt = INTENT_DESCRIPTIONS + "\n" + build_fallback_prompt(text)
    r = chat_client.chat.completions.create(
        model=os.getenv("CHAT_MODEL"),
        messages=[{"role": "system", "content": prompt}]
    )
    return r.choices[0].message.content.strip()


