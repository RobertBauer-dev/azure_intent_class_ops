# Deployment-Anleitung: Von lokal zu Azure

Diese Anleitung erklärt Schritt für Schritt, wie du deine lokale FastAPI-Anwendung auf Azure Container Instances deployst.

## 🎯 Übersicht: Was passiert beim Deployment?

Du nimmst deine lokale Anwendung und packst sie in einen **Container** (Docker), der dann auf **Azure** läuft. Das ermöglicht:
- ✅ Deine App läuft 24/7 in der Cloud
- ✅ Zugriff von überall aus dem Internet
- ✅ Automatische Skalierung und Monitoring möglich

---

## 📦 Phase 1: Docker Image erstellen

### Was ist Docker?
Docker packt deine App und alle Abhängigkeiten in ein "Paket" (Image), das überall gleich läuft - lokal, in der Cloud, etc.

### Schritt 1: Docker Image bauen

```bash
docker build -t llmops-api .
```

**Was passiert hier?**
- Das `Dockerfile` wird gelesen
- Ein Basis-Image wird geladen (Python 3.10)
- Alle Python-Pakete werden installiert (`requirements.txt`)
- Dein Code wird kopiert (`app/`, `model/`, `data/`)
- **Wichtig:** Es wird geprüft, ob alle benötigten Dateien vorhanden sind:
  - `model/artifacts/model.pkl` (trainiertes ML-Modell)
  - `model/artifacts/label_encoder.pkl` (Label-Encoder)
  - `data/vector_db/faiss.index` (FAISS-Vektorindex)
- Am Ende hast du ein **lokales Docker Image** mit dem Namen `llmops-api`

**Tipp:** Wenn hier ein Fehler kommt wie "Missing required files", dann fehlen die Dateien oben. Diese müssen lokal vorhanden sein, bevor du buildest.

---

## ☁️ Phase 2: Azure-Vorbereitung

### Schritt 2: Azure Login

```bash
az login
```

**Was passiert hier?**
- Du meldest dich bei deinem Azure-Account an
- Ein Browser-Fenster öffnet sich für die Authentifizierung
- Nach erfolgreichem Login kannst du Azure-Ressourcen verwalten

**Warum?** Azure muss wissen, wer du bist, bevor du Ressourcen erstellen kannst.

---

## 📦 Phase 3: Container Registry (ACR)

### Was ist Azure Container Registry (ACR)?
Ein **privates Repository** für Docker Images - wie GitHub für Code, aber für Container.

### Schritt 3: ACR Login

```bash
az acr login -n acrllmopsdemo2
```

**Was passiert hier?**
- Du authentifizierst dich bei deiner Container Registry (`acrllmopsdemo2`)
- Docker kann jetzt Images in diese Registry pushen

**Warum?** Azure Container Instances kann nur Images aus einer Registry ziehen, nicht von deinem lokalen Rechner.

### Schritt 4: Admin Account aktivieren

```bash
az acr update -n acrllmopsdemo2 --admin-enabled true
```

**Was passiert hier?**
- Der Admin-Account für die Registry wird aktiviert
- Das ermöglicht einfache Authentifizierung mit Username/Password

**Warum?** Beim ersten Mal muss das aktiviert werden. Danach kann man Images pushen.

---

## 🏷️ Phase 4: Image taggen und pushen

### Schritt 5: Image taggen

```bash
docker tag llmops-api acrllmopsdemo2.azurecr.io/llmops-api:v1
```

**Was passiert hier?**
- Dein lokales Image `llmops-api` bekommt einen neuen "Tag" (Name)
- Der neue Name ist: `acrllmopsdemo2.azurecr.io/llmops-api:v1`
- Das sagt: "Gehe zur Registry `acrllmopsdemo2.azurecr.io`, finde das Image `llmops-api` in Version `v1`"

**Warum?** Azure muss wissen, wo das Image liegt (in welcher Registry) und welche Version es ist.

**Analogie:** Wie ein Paket mit Adresse - ohne Adresse weiß niemand, wo es hin soll.

### Schritt 6: Image in ACR pushen

```bash
docker push acrllmopsdemo2.azurecr.io/llmops-api:v1
```

**Was passiert hier?**
- Das Docker Image wird von deinem lokalen Rechner hochgeladen
- Es landet in deiner Azure Container Registry
- Das kann je nach Größe einige Minuten dauern

**Warum?** Azure Container Instances kann das Image nur von dort abrufen, nicht von deinem Rechner.

---

## 🚀 Phase 5: Deployment auf Azure Container Instances

### Was ist Azure Container Instances (ACI)?
Ein Service, der Container direkt startet - ohne komplexe Orchestrierung. Perfekt für einfache Deployments.

### Schritt 7: Deployment Script ausführen

```bash
bash deploy-aci.sh
```

**Was passiert hier genau?** (Das Script macht mehrere Dinge automatisch)

#### 7a: Environment-Variablen laden
- Das Script liest deine `.env` Datei
- Es sammelt alle benötigten Variablen:
  - `AZURE_OPENAI_APIVERSION` - API Version für OpenAI
  - `EMB_ENDPOINT_BASE` - Endpoint für Embeddings
  - `EMB_MODEL_DEPLOY_KEY` - API Key für Embeddings
  - `CHAT_ENDPOINT_URI` - Endpoint für Chat
  - `CHAT_ENDPOINT_KEY` - API Key für Chat
  - `CLF_THRESHOLD`, `RETRIEVAL_THRESHOLD` - ML-Thresholds
  - `APP_INSIGHTS_CONN_STR` - Optional: Für Monitoring

**Warum?** Die App braucht diese Variablen, um zu funktionieren (API Keys, Endpoints, etc.)

#### 7b: ACR Password holen
- Das Script holt automatisch das Passwort für die Container Registry
- Damit kann Azure das Image aus der Registry abrufen

#### 7c: Alten Container löschen (falls vorhanden)
- Wenn bereits ein Container mit dem Namen `llmops-api` existiert, wird er gelöscht
- Das ermöglicht ein sauberes Update

#### 7d: Neuen Container erstellen
- Azure Container Instances wird angewiesen, einen neuen Container zu starten
- Mit diesen Einstellungen:
  - **Image:** `acrllmopsdemo2.azurecr.io/llmops-api:v1` (aus der Registry)
  - **CPU:** 1.0 Core
  - **Memory:** 2.0 GB
  - **Port:** 8001 (deine FastAPI-App läuft darauf)
  - **Environment Variables:** Alle aus deiner `.env` Datei
  - **DNS Name:** `llmops-api` (öffentliche URL)
  - **IP Address:** Public (von überall erreichbar)

#### 7e: URLs ausgeben
- Nach erfolgreichem Deployment zeigt das Script:
  - **FQDN:** `llmops-api.westeurope.azurecontainer.io` (Domain-Name)
  - **IP:** `52.123.45.67` (IP-Adresse)

**Warum?** Du brauchst diese Adresse, um deine API aufzurufen.

---

## ✅ Nach dem Deployment

### Deine API ist jetzt erreichbar unter:

```bash
# Mit Domain-Name
curl -X POST "http://llmops-api.westeurope.azurecontainer.io:8001/predict" \
     -H "Content-Type: application/json" \
     -d '{"text": "Ich kann mich nicht einloggen"}'

# Oder mit IP-Adresse
curl -X POST "http://52.123.45.67:8001/predict" \
     -H "Content-Type: application/json" \
     -d '{"text": "Ich kann mich nicht einloggen"}'
```

### Wichtige Punkte:

1. **Port 8001:** Deine App läuft auf Port 8001, nicht auf 80!
2. **HTTP (nicht HTTPS):** Standardmäßig ist HTTP aktiviert
3. **Container Status:** Du kannst im Azure Portal sehen, ob der Container läuft

---

## 🔍 Troubleshooting

### Container startet nicht?

1. **Logs anschauen:**
   ```bash
   az container logs --resource-group rg-llmops-demo --name llmops-api
   ```

2. **Prüfe Environment-Variablen:**
   - Sind alle Variablen in `.env` gesetzt?
   - Sind die API Keys korrekt?

3. **Prüfe ob Image gepusht wurde:**
   ```bash
   az acr repository list --name acrllmopsdemo2
   ```

### Fehler beim Push?

- **ACR Admin nicht aktiviert?** → `az acr update -n acrllmopsdemo2 --admin-enabled true`
- **Nicht eingeloggt?** → `az acr login -n acrllmopsdemo2`

### Fehlende Dateien beim Build?

- Stelle sicher, dass diese Dateien lokal vorhanden sind:
  - `model/artifacts/model.pkl`
  - `model/artifacts/label_encoder.pkl`
  - `data/vector_db/faiss.index`

---

## 📊 Überblick: Der komplette Flow

```
┌─────────────────┐
│  Lokaler Code   │
│  + .env Datei   │
└────────┬────────┘
         │
         │ docker build
         ▼
┌─────────────────┐
│  Docker Image   │
│  (lokal)        │
└────────┬────────┘
         │
         │ docker tag + push
         ▼
┌─────────────────┐
│  Azure ACR      │
│  (Registry)     │
└────────┬────────┘
         │
         │ deploy-aci.sh
         │ (lädt .env, erstellt Container)
         ▼
┌─────────────────┐
│  Azure ACI      │
│  (läuft)        │
│  http://...:8001│
└─────────────────┘
```

---

## 💡 Zusammenfassung: Was wurde angepasst?

1. **Dockerfile:** 
   - Prüft automatisch, ob alle benötigten Dateien vorhanden sind
   - Kopiert nur die nötigen Verzeichnisse (besser für Performance)

2. **deploy-aci.sh:**
   - Verwendet nur die tatsächlich genutzten Environment-Variablen
   - Löscht automatisch alte Container
   - Gibt URLs nach Deployment aus

3. **README.md:**
   - Klarere Schritt-für-Schritt-Anleitung
   - Port-Korrektur (8001 statt 8000)

