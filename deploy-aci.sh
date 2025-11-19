#!/bin/bash
# deploy_aci.sh

# Lade .env Datei
source .env

# Baue environment-variables String (OHNE zusätzliche Anführungszeichen!)
# Basierend auf tatsächlich verwendeten Variablen in:
# - app/app.py (APP_INSIGHTS_CONN_STR)
# - model/chat_model.py (AZURE_OPENAI_APIVERSION, CHAT_ENDPOINT_URI, CHAT_ENDPOINT_KEY, CHAT_MODEL)
# - model/embedding_model.py (EMB_ENDPOINT_BASE, EMB_MODEL_DEPLOY_NAME, EMB_MODEL_DEPLOY_KEY, EMB_MODEL, EMB_DIM, AZURE_OPENAI_APIVERSION)
# - model/predict_intent.py (CLF_THRESHOLD, RETRIEVAL_THRESHOLD)
ENV_VARS=""
ENV_VARS="${ENV_VARS} AZURE_OPENAI_APIVERSION=${AZURE_OPENAI_APIVERSION}"
ENV_VARS="${ENV_VARS} EMB_ENDPOINT_BASE=${EMB_ENDPOINT_BASE}"
ENV_VARS="${ENV_VARS} EMB_MODEL_DEPLOY_NAME=${EMB_MODEL_DEPLOY_NAME}"
ENV_VARS="${ENV_VARS} EMB_MODEL_DEPLOY_KEY=${EMB_MODEL_DEPLOY_KEY}"
ENV_VARS="${ENV_VARS} EMB_MODEL=${EMB_MODEL}"
ENV_VARS="${ENV_VARS} EMB_DIM=${EMB_DIM}"
ENV_VARS="${ENV_VARS} CHAT_ENDPOINT_URI=${CHAT_ENDPOINT_URI}"
ENV_VARS="${ENV_VARS} CHAT_ENDPOINT_KEY=${CHAT_ENDPOINT_KEY}"
ENV_VARS="${ENV_VARS} CHAT_MODEL=${CHAT_MODEL}"
ENV_VARS="${ENV_VARS} CLF_THRESHOLD=${CLF_THRESHOLD}"
ENV_VARS="${ENV_VARS} RETRIEVAL_THRESHOLD=${RETRIEVAL_THRESHOLD}"

# Optional: Application Insights (wenn gesetzt)
if [ -n "${APP_INSIGHTS_CONN_STR}" ]; then
  ENV_VARS="${ENV_VARS} APP_INSIGHTS_CONN_STR=${APP_INSIGHTS_CONN_STR}"
fi

# Hole ACR Password
ACR_PASSWORD=$(az acr credential show --name acrllmopsdemo2 --query "passwords[0].value" --output tsv 2>/dev/null)

if [ -z "$ACR_PASSWORD" ]; then
  echo "Error: ACR Admin not enabled. Run: az acr update -n acrllmopsdemo2 --admin-enabled true"
  exit 1
fi

# Prüfe ob Container bereits existiert und lösche ihn falls ja
if az container show --resource-group rg-llmops-demo --name llmops-api &>/dev/null; then
  echo "Container llmops-api existiert bereits. Lösche alten Container..."
  az container delete --resource-group rg-llmops-demo --name llmops-api --yes
  echo "Warte auf Löschung..."
  sleep 5
fi

# Erstelle neuen Container
echo "Erstelle neuen Container..."
az container create \
  --resource-group rg-llmops-demo \
  --name llmops-api \
  --image acrllmopsdemo2.azurecr.io/llmops-api:v6 \
  --registry-login-server acrllmopsdemo2.azurecr.io \
  --registry-username acrllmopsdemo2 \
  --registry-password "${ACR_PASSWORD}" \
  --os-type Linux \
  --cpu 1.0 \
  --memory 2.0 \
  --environment-variables $ENV_VARS \
  --ports 8001 \
  --dns-name-label llmops-api \
  --ip-address Public

if [ $? -eq 0 ]; then
  echo "✓ Container erfolgreich erstellt!"
  echo "FQDN: $(az container show --resource-group rg-llmops-demo --name llmops-api --query ipAddress.fqdn -o tsv)"
  echo "IP: $(az container show --resource-group rg-llmops-demo --name llmops-api --query ipAddress.ip -o tsv)"
else
  echo "✗ Fehler beim Erstellen des Containers!"
  exit 1
fi