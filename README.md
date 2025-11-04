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
# if not already built
docker build -t llmops-api .
# this can not made in Azure portal only via terminal
# 1. login
az login
# 2. ACR login (Azure Container Registry)
az acr login -n acrllmopsdemo2 
# 3. tag image
docker tag llmops-api acrllmopsdemo2.azurecr.io/llmops-api:v1
# 4. push into ACR
docker push acrllmopsdemo2.azurecr.io/llmops-api:v1
# 5. admin account aktivieren
az acr update -n acrllmopsdemo2 --admin-enabled true
# 6. Deployment in Azure Container Instances
bash deploy-aci.sh

# example usage
curl -X POST "http://<deine-azure-ip>:8000/predict" \
     -H "Content-Type: application/json" \
     -d '{"text": "Meine Bezahlung schlägt fehl"}'