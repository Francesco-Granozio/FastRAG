# Setup e Avvio dell'Applicazione RAG

Questa guida descrive come avviare tutti i componenti necessari per l'applicazione RAG.

## Prerequisiti

- Docker installato e in esecuzione
- Node.js e npm installati (per Inngest CLI)
- Python 3.13+ con `uv` installato
- Ollama installato e in esecuzione (per sviluppo locale)
- Modelli Ollama installati:
  - `llama3:8b` (per LLM)
  - `embeddinggemma:latest` (per embeddings)

### Verifica Ollama

Prima di avviare l'applicazione, verifica che Ollama sia configurato correttamente:

```bash
# Testa la connessione e i modelli
uv run python test_ollama.py
```

Se i modelli non sono installati:

```bash
ollama pull llama3:8b
ollama pull embeddinggemma:latest
```

## Configurazione

1. **Copia il file di configurazione**:

   ```bash
   # Per sviluppo locale con Ollama (default)
   copy env.ollama .env

   # Oppure per produzione con OpenAI
   copy env.openai .env
   ```

2. **Modifica il file `.env`** con le tue API keys se necessario.

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

### 2. Avvia il Server FastAPI (Backend)

In un terminale separato:

```bash
uv run uvicorn main:app --host 127.0.0.1 --port 8000
```

Il server sarà disponibile su: `http://127.0.0.1:8000`
L'endpoint Inngest sarà su: `http://127.0.0.1:8000/api/inngest`

### 3. Avvia Streamlit (Frontend)

In un altro terminale separato:

```bash
uv run streamlit run streamlit_app.py
```

L'applicazione sarà disponibile su: `http://localhost:8501`

### 4. Avvia Inngest Dev Server

In un altro terminale separato:

```bash
npx inngest-cli@latest dev -u http://127.0.0.1:8000/api/inngest --no-discovery
```

Il dashboard Inngest sarà disponibile su: `http://localhost:8288`

## Script di Avvio Rapido

Per avviare/riavviare tutti i servizi automaticamente:

**Windows PowerShell:**

```powershell
.\start.ps1
```

Questo script:

- Verifica e avvia Qdrant se non è attivo
- Riavvia FastAPI se è già attivo, altrimenti lo avvia
- Riavvia Streamlit se è già attivo, altrimenti lo avvia
- Avvia Inngest se non è attivo

Per fermare tutti i servizi:

```powershell
.\stop.ps1
```

## Verifica che Tutto Funzioni

1. **Qdrant**: Apri `http://localhost:6333/dashboard` nel browser
2. **FastAPI**: Verifica `http://127.0.0.1:8000/api/inngest` (dovrebbe restituire JSON)
3. **Streamlit**: Apri `http://localhost:8501`
4. **Inngest**: Apri `http://localhost:8288` e verifica che l'app sia sincronizzata

## Ordine Consigliato di Avvio

1. Qdrant (può rimanere sempre attivo)
2. FastAPI server
3. Inngest dev server
4. Streamlit (opzionale, solo se vuoi usare l'interfaccia web)

## Troubleshooting

### Qdrant non si avvia

- Verifica che Docker sia in esecuzione
- Controlla se il container esiste già: `docker ps -a | findstr qdrant`
- Se esiste, rimuovilo: `docker rm qdrant`

### FastAPI non si avvia

- Verifica che la porta 8000 non sia già in uso
- Controlla gli errori nel terminale
- Verifica che il file `.env` sia configurato correttamente

### Inngest non sincronizza

- Verifica che FastAPI sia in esecuzione sulla porta 8000
- Controlla l'URL: deve essere `http://127.0.0.1:8000/api/inngest`
- Verifica che non ci siano errori nel terminale di FastAPI

### Ollama non risponde o errore 404

- Verifica che Ollama sia in esecuzione: `ollama list`
- Esegui il test: `uv run python test_ollama.py`
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
# Ferma Streamlit: Ctrl+C nel terminale
# Ferma FastAPI: Ctrl+C nel terminale
# Ferma Inngest: Ctrl+C nel terminale
# Ferma Qdrant:
docker stop qdrant
```

Per rimuovere il container Qdrant:

```bash
docker stop qdrant
docker rm qdrant
```
