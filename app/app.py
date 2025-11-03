import sys
from pathlib import Path

# Set up project path before importing config
_project_root = Path(__file__).parent.parent.resolve()
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel

from model.predict_intent import predict_intent

load_dotenv()

app = FastAPI()


class Query(BaseModel):
    text: str


@app.post("/predict")
def predict(q: Query):
    return predict_intent(q.text)


@app.get("/")
def root():
    return {"status": "running", "message": "LLM-Ops Intent Model API"}