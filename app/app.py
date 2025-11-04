import sys
from pathlib import Path
import logging

# Set up logging to stdout/stderr so Azure can capture it
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
        #logging.StreamHandler(sys.stderr)
    ]
)
logger = logging.getLogger(__name__)

# Set up project path before importing config
_project_root = Path(__file__).parent.parent.resolve()
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

logger.info(f"Project root: {_project_root}")

from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel

load_dotenv()
logger.info("Environment loaded")

try:
    logger.info("Importing predict_intent...")
    from model.predict_intent import predict_intent
    logger.info("✓ predict_intent imported successfully")
except Exception as e:
    logger.error(f"ERROR importing predict_intent: {e}")
    import traceback
    logger.error(traceback.format_exc())
    # Fallback: App startet trotzdem, aber predict gibt Fehler zurück
    def predict_intent(text):
        return {"error": f"Model not loaded: {str(e)}", "text": text}

app = FastAPI()

logger.info("FastAPI app created")

class Query(BaseModel):
    text: str

@app.post("/predict")
def predict(q: Query):
    try:
        return predict_intent(q.text)
    except Exception as e:
        logger.error(f"Error in predict: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return {"error": str(e), "text": q.text}

@app.get("/")
def root():
    return {"status": "running", "message": "LLM-Ops Intent Model API"}

logger.info("App startup complete")