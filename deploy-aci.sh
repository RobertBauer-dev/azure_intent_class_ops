
  #!/bin/bash
# deploy_aci.sh

# Lade .env Datei
source .env

# Baue environment-variables String (OHNE zusätzliche Anführungszeichen!)
ENV_VARS=""
ENV_VARS="${ENV_VARS} AZURE_OPENAI_APIVERSION=${AZURE_OPENAI_APIVERSION}"
ENV_VARS="${ENV_VARS} AZURE_OPENAI_ENDPOINT=${AZURE_OPENAI_ENDPOINT}"
ENV_VARS="${ENV_VARS} AZURE_OPENAI_KEY1=${AZURE_OPENAI_KEY1}"
ENV_VARS="${ENV_VARS} CHAT_ENDPOINT_URI=${CHAT_ENDPOINT_URI}"
ENV_VARS="${ENV_VARS} CHAT_ENDPOINT_KEY=${CHAT_ENDPOINT_KEY}"
ENV_VARS="${ENV_VARS} EMB_MODEL=${EMB_MODEL}"
ENV_VARS="${ENV_VARS} EMB_DIM=${EMB_DIM}"
ENV_VARS="${ENV_VARS} EMB_MODEL_DEPLOY_NAME=${EMB_MODEL_DEPLOY_NAME}"
ENV_VARS="${ENV_VARS} EMB_MODEL_DEPLOY_TARGET_URI=${EMB_MODEL_DEPLOY_TARGET_URI}"
ENV_VARS="${ENV_VARS} EMB_MODEL_DEPLOY_KEY=${EMB_MODEL_DEPLOY_KEY}"
ENV_VARS="${ENV_VARS} CLF_THRESHOLD=${CLF_THRESHOLD}"
ENV_VARS="${ENV_VARS} RETRIEVAL_THRESHOLD=${RETRIEVAL_THRESHOLD}"
ENV_VARS="${ENV_VARS} CHAT_MODEL=${CHAT_MODEL}"

# Hole ACR Password
ACR_PASSWORD=$(az acr credential show --name acrllmopsdemo2 --query "passwords[0].value" --output tsv 2>/dev/null)

if [ -z "$ACR_PASSWORD" ]; then
  echo "Error: ACR Admin not enabled. Run: az acr update -n acrllmopsdemo2 --admin-enabled true"
  exit 1
fi

az container create \
  --resource-group rg-llmops-demo \
  --name llmops-api \
  --image acrllmopsdemo2.azurecr.io/llmops-api:v1 \
  --registry-login-server acrllmopsdemo2.azurecr.io \
  --registry-username acrllmopsdemo2 \
  --registry-password "${ACR_PASSWORD}" \
  --os-type Linux \
  --cpu 1.0 \
  --memory 2.0 \
  --environment-variables $ENV_VARS \
  --ports 8001