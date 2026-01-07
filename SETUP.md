# Setup e Avvio dell'Applicazione RAG

Questa guida descrive come avviare tutti i componenti necessari per l'applicazione RAG.

## Prerequisiti

- Docker installato e in esecuzione
- Node.js 18+ e npm installati (per Inngest CLI e React frontend)
- Python 3.13+ con `uv` installato
- Ollama installato e in esecuzione (per sviluppo locale)
- Modelli Ollama installati:
  - `llama3:8b` (per LLM)
  - `embeddinggemma:latest` (per embeddings)

### Verifica Ollama

Prima di avviare l'applicazione, verifica che Ollama sia configurato correttamente:

Se i modelli non sono installati:

```bash
ollama pull llama3:8b
ollama pull embeddinggemma:latest
```

## Configurazione

1. **Copia il file di configurazione**:

   ```bash
   # Per sviluppo locale con Ollama (default)
   copy env_samples\env.ollama .env

   # Oppure per produzione con OpenAI
   copy env_samples\env.openai .env

   # Oppure per altri provider:
   # copy env_samples\env.google .env
   # copy env_samples\env.anthropic .env
   ```

2. **Modifica il file `.env`** con le tue API keys se necessario.

3. **Installa le dipendenze del frontend**:

   ```bash
   cd frontend
   npm install
   cd ..
   ```

## Step per Avviare l'Applicazione

### 1. Avvia Qdrant (Vector Database)

```bash
docker run -d --name qdrant -p 6333:6333 -v "$(pwd)/qdrant_storage:/qdrant/storage" qdrant/qdrant
```

**Su Windows PowerShell:**

```powershell
docker run -d --name qdrant -p 6333:6333 -v "${PWD}/qdrant_storage:/qdrant/storage" qdrant/qdrant
```

**Su Windows CMD:**

```cmd
docker run -d --name qdrant -p 6333:6333 -v "%CD%/qdrant_storage:/qdrant/storage" qdrant/qdrant
```

Verifica che Qdrant sia in esecuzione:

```bash
docker ps | findstr qdrant
```

### 2. Avvia FastAPI (Backend API)

In un terminale separato:

```bash
uv run uvicorn app:app --host 127.0.0.1 --port 8000
```

Il server sarà disponibile su: `http://127.0.0.1:8000`
L'endpoint Inngest sarà su: `http://127.0.0.1:8000/api/inngest`
L'API documentation sarà su: `http://127.0.0.1:8000/docs`

### 3. Installa le dipendenze del frontend

```bash
cd frontend
npm install
cd ..
```

### 4. Avvia React Frontend

In un altro terminale separato:

```bash
cd frontend
npm run dev
```

L'applicazione sarà disponibile su: `http://localhost:3000`

### 5. Avvia Inngest Dev Server

In un altro terminale separato:

```bash
npx inngest-cli@latest dev -u http://127.0.0.1:8000/api/inngest --no-discovery
```

Il dashboard Inngest sarà disponibile su: `http://localhost:8288`

## Avvio Automatico con Script

Puoi usare lo script PowerShell `start.ps1` per avviare tutti i servizi automaticamente:

```powershell
.\start.ps1
```

Lo script:
1. Verifica e avvia Qdrant (se non già attivo)
2. Riavvia FastAPI (se già attivo) o lo avvia
3. Riavvia React Frontend (se già attivo) o lo avvia
4. Avvia Inngest dev server

**Nota**: Assicurati di aver eseguito `npm install` nella directory `frontend` prima di usare lo script.

Per fermare tutti i servizi:

```powershell
.\stop.ps1
```

## Verifica che Tutto Funzioni

1. **Qdrant**: Apri `http://localhost:6333/dashboard` nel browser
2. **FastAPI**: Verifica `http://127.0.0.1:8000/api/inngest` (dovrebbe restituire JSON)
3. **React Frontend**: Apri `http://localhost:3000`
4. **Inngest**: Apri `http://localhost:8288` e verifica che l'app sia sincronizzata

## Ordine Consigliato di Avvio

1. Qdrant (può rimanere sempre attivo)
2. FastAPI server
3. Inngest dev server
4. React Frontend

## Troubleshooting

### Qdrant non si avvia

- Verifica che Docker sia in esecuzione
- Controlla se il container esiste già: `docker ps -a | findstr qdrant`
- Se esiste, rimuovilo: `docker rm qdrant`

### FastAPI non si avvia

- Verifica che la porta 8000 non sia già in uso
- Controlla gli errori nel terminale
- Verifica che il file `.env` sia configurato correttamente

### React Frontend non si avvia

- Verifica che Node.js e npm siano installati: `node --version` e `npm --version`
- Assicurati di aver eseguito `npm install` nella directory `frontend`
- Verifica che la porta 3000 non sia già in uso
- Controlla gli errori nel terminale

### Inngest non sincronizza

- Verifica che FastAPI sia in esecuzione sulla porta 8000
- Controlla l'URL: deve essere `http://127.0.0.1:8000/api/inngest`
- Verifica che non ci siano errori nel terminale di FastAPI

### Ollama non risponde o errore 404

- Verifica che Ollama sia in esecuzione: `ollama list`
- Controlla che i modelli siano installati:
  ```bash
  ollama pull llama3:8b
  ollama pull embeddinggemma:latest
  ```
- Verifica l'URL in `.env`: `OLLAMA_BASE_URL=http://localhost:11434`
- Se l'errore persiste, verifica che Ollama sia avviato: `ollama serve`

## Stop dei Servizi

Per fermare tutti i servizi:

```bash
# Ferma React Frontend: Ctrl+C nel terminale
# Ferma FastAPI: Ctrl+C nel terminale
# Ferma Inngest: Ctrl+C nel terminale
# Ferma Qdrant:
docker stop qdrant
```

Oppure usa lo script:

```powershell
.\stop.ps1
```

## Architettura

L'applicazione è composta da:

- **FastAPI**: Backend API server con endpoint REST (`app.py`)
- **React + TypeScript + Vite**: Frontend web moderno, type-safe e performante
- **Tailwind CSS**: Styling utility-first
- **Inngest**: Event-driven workflow orchestration
- **Qdrant**: Vector database per embeddings
- **Ollama**: Local LLM e embedding server (sviluppo)
- **OpenAI/Google/Anthropic**: Cloud LLM providers (produzione)

### Struttura del Codice

Il codice Python è organizzato in:

- **`src/api/`**: Endpoint REST API (upload, query, files)
- **`src/core/`**: Logica core dell'applicazione (config, data_loader, vector_db, custom_types)
- **`src/providers/`**: Provider per LLM e embedding (Ollama, OpenAI, Google, Anthropic)

## Note

- Il frontend React comunica con il backend FastAPI tramite API REST
- CORS è configurato per permettere richieste da `localhost:3000` a `localhost:8000`
- In produzione, il frontend può essere buildato e servito direttamente da FastAPI
- I file di configurazione `.env` sono nella cartella `env_samples/` - copia quello che ti serve nella root come `.env`
- La cartella `uploads/` contiene i PDF caricati (non committare file sensibili)
- La cartella `qdrant_storage/` contiene i dati del database vettoriale (persistente)
