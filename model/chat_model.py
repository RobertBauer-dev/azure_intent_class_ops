from openai import AzureOpenAI
import os
from dotenv import load_dotenv

load_dotenv()

chat_client = AzureOpenAI(
    api_version=os.getenv("AZURE_OPENAI_APIVERSION"),
    azure_endpoint=os.getenv("CHAT_ENDPOINT_URI"),
    api_key=os.getenv("CHAT_ENDPOINT_KEY") # AZURE_OPENAI_KEY1
)