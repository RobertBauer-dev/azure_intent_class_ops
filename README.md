# LLM-Ops Demo Projekt (Azure OpenAI + Lokale Vektorsuche)

## Setup
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export OPENAI_KEY="..."

## Start backend
uvicorn app.app:app --reload --port 8001

# Example usage
curl -X POST "http://localhost:8001/predict" \
     -H "Content-Type: application/json" \
     -d '{"text": "Ich kann mich nicht einloggen"}'

## Docker deploy on prem 
docker build -t llmops-api .

# HOST_PORT:CONTAINER_PORT, FastAPI used 8001, hence CONTAINER_PORT=8001
docker run -p 8001:8001 --env-file .env llmops-api

# use adress in chrome instead safari
http://0.0.0.0:8001/docs

## Docker deploy on Azure

**WICHTIG:** Stelle sicher, dass diese Dateien lokal vorhanden sind (werden ins Docker Image kopiert):
- `model/artifacts/model.pkl`
- `model/artifacts/label_encoder.pkl`
- `data/vector_db/faiss.index`

```bash
# 1. Docker Image bauen (prüft automatisch ob alle benötigten Dateien vorhanden sind)
docker build -t llmops-api .

# 2. Azure Login
az login

# 3. ACR Login (Azure Container Registry)
az acr login -n acrllmopsdemo2 

# 4. Admin Account aktivieren (nur beim ersten Mal oder wenn disabled)
az acr update -n acrllmopsdemo2 --admin-enabled true

# 5. Image taggen
docker tag llmops-api acrllmopsdemo2.azurecr.io/llmops-api:v1

# 6. Image in ACR pushen
docker push acrllmopsdemo2.azurecr.io/llmops-api:v1

# 7. Deployment in Azure Container Instances
# (stellt sicher, dass .env Datei vorhanden ist und alle ENV-Variablen enthält)
bash deploy-aci.sh
```

**Hinweis:** Das `deploy-aci.sh` Script gibt nach erfolgreichem Deployment automatisch die Container-URLs aus (FQDN und IP).

# example usage
curl -X POST "http://<deine-azure-ip>:8001/predict" \
     -H "Content-Type: application/json" \
     -d '{"text": "Meine Bezahlung schlägt fehl"}'


## Application Insights activate (Azure)
az monitor app-insights component create \
  --app ins-llmops-demo \
  --location westeurope \
  --resource-group rg-llmops-demo

# See metrics
# portal -> Application Insights -> ins-llmops-demo
# -> Investigate -> Transaction search
