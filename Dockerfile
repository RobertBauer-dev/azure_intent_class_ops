FROM python:3.10-slim

WORKDIR /app

# Install dependencies first (for better caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/
COPY model/ ./model/
COPY data/ ./data/
COPY config.py .

# Verify required files exist (critical for runtime)
RUN test -f model/artifacts/model.pkl && \
    test -f model/artifacts/label_encoder.pkl && \
    test -f data/vector_db/faiss.index && \
    echo "✓ All required files present" || \
    (echo "ERROR: Missing required files. Check: model/artifacts/model.pkl, model/artifacts/label_encoder.pkl, data/vector_db/faiss.index" && exit 1)

EXPOSE 8001

CMD ["python", "-m", "uvicorn", "app.app:app", "--host", "0.0.0.0", "--port", "8001", "--log-level", "info"]