import sys
from pathlib import Path
import logging
import os

# Custom Formatter mit Farben
class ColoredFormatter(logging.Formatter):
    """Custom Formatter mit Farben für verschiedene Log-Level"""
    
    # ANSI Color Codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Grün
        'WARNING': '\033[33m',    # Orange/Gelb
        'ERROR': '\033[31m',      # Rot
        'CRITICAL': '\033[35m',   # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record):
        # Farbe für das Log-Level
        log_color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{log_color}{record.levelname}{self.RESET}"
        
        # Formatiere die Nachricht
        return super().format(record)

# Set up logging to stdout/stderr so Azure can capture it
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Handler für stdout
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.INFO)

# Colored Formatter verwenden (nur wenn TTY, sonst einfacher Formatter)
# In Azure Container Instances ist stdout kein TTY, daher einfacher Formatter
if sys.stdout.isatty():
    formatter = ColoredFormatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
else:
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
handler.setFormatter(formatter)
logger.addHandler(handler)

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

# OpenTelemetry Setup (optional - nur wenn Connection String vorhanden)
connection_string = os.getenv("APP_INSIGHTS_CONN_STR")
connection_string_valid = False

if connection_string:
    # Strip quotes and whitespace
    connection_string = connection_string.strip('"\' \t\n\r')
    
    # Basic validation: check if it contains InstrumentationKey
    if connection_string and "InstrumentationKey=" in connection_string:
        try:
            from opentelemetry import trace
            from opentelemetry.sdk.trace import TracerProvider
            from opentelemetry.sdk.trace.export import BatchSpanProcessor
            from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter
            from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
            
            # Tracer Provider einrichten = central component for spans (traces)
            tracer_provider = TracerProvider()
            # set to global provider for all libraries, middleware, etc.
            trace.set_tracer_provider(tracer_provider)
            
            # Azure Monitor Exporter hinzufügen, connect to Azure Application insights
            # send spans to Azure
            exporter = AzureMonitorTraceExporter.from_connection_string(connection_string)
            
            # batch spans and send them to the exporter, faster than for each span
            span_processor = BatchSpanProcessor(exporter)
            
            # add span processor to the tracer provider
            tracer_provider.add_span_processor(span_processor)
            
            logger.info("OpenTelemetry configured for Application Insights")
            connection_string_valid = True
        except Exception as e:
            logger.warning(f"OpenTelemetry/Application Insights setup failed: {e}")
            logger.warning("Continuing without Application Insights monitoring...")
            connection_string = None
            connection_string_valid = False
    else:
        logger.warning(f"APP_INSIGHTS_CONN_STR appears invalid (missing InstrumentationKey), skipping Application Insights")
        connection_string = None
        connection_string_valid = False
else:
    logger.warning("APP_INSIGHTS_CONN_STR not set, skipping Application Insights")

try:
    logger.info("Importing predict_intent...")
    from model.predict_intent import predict_intent
    logger.info("✓ predict_intent imported successfully")
except Exception as e:
    logger.error(f"ERROR importing predict_intent: {e}")
    import traceback
    logger.error(traceback.format_exc())
    def predict_intent(text):
        return {"error": f"Model not loaded: {str(e)}", "text": text}

app = FastAPI()
logger.info("FastAPI app created")

# FastAPI Instrumentation (automatisches Tracing)
if connection_string_valid:
    try:
        FastAPIInstrumentor.instrument_app(app)
        logger.info("FastAPI instrumentation enabled")
    except Exception as e:
        logger.warning(f"Could not instrument FastAPI: {e}")

class Query(BaseModel):
    text: str

@app.post("/predict")
def predict(q: Query):
    try:
        result = predict_intent(q.text)
        logger.info(f"Predict result: {result}")
        return result
    except Exception as e:
        logger.error(f"Error in predict: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return {"error": str(e), "text": q.text}

@app.get("/")
def root():
    return {"status": "running", "message": "LLM-Ops Intent Model API"}

logger.info("App startup complete")