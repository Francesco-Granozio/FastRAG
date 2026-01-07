# RAG Application

Applicazione RAG (Retrieval-Augmented Generation) per l'ingest e query di documenti PDF utilizzando modelli LLM e embedding configurabili.

## Caratteristiche

- **Modern React UI**: Interfaccia utente moderna, veloce e responsive
- **Provider LLM configurabili**: Ollama (locale), OpenAI, Google Gemini, Anthropic Claude
- **Provider Embedding configurabili**: Ollama, OpenAI, Google
- **Vector Database**: Qdrant per la ricerca semantica
- **Workflow**: Inngest per la gestione asincrona delle operazioni
- **Frontend**: React + TypeScript + Vite + Tailwind CSS
- **Backend**: FastAPI con endpoint REST

## Demo

L'applicazione RAG offre un'interfaccia intuitiva per l'upload di documenti PDF, la loro elaborazione e embedding nel database vettoriale, e la possibilità di interrogare i documenti tramite modelli LLM. Di seguito alcune schermate che illustrano le funzionalità principali.

### Schermata Principale - Upload e Query

La schermata principale permette di:

- **Upload PDF**: Caricare documenti PDF tramite drag-and-drop o selezione file. I file vengono processati in modo asincrono e i chunk vengono embeddati nel database vettoriale.
- **Query LLM**: Porre domande ai documenti caricati. Il sistema recupera i chunk più rilevanti e genera una risposta utilizzando il modello LLM configurato.

![Schermata principale con upload, domanda e risposta](docs/images/demo-main-screen.png)

### Gestione File Embeddati

La sezione "Embedded Files" consente di:

- **Visualizzare i chunk**: Esplorare i chunk generati da ciascun documento, con anteprima del contenuto testuale.
- **Gestire i file**: Selezionare ed eliminare file embeddati dal database vettoriale.

![Embedded Files con visualizzazione chunk e opzioni di eliminazione](docs/images/demo-embedded-files.png)

### Orchestrator - Fase di Embedding

L'orchestrator Inngest gestisce l'elaborazione asincrona dei PDF. Durante la fase di embedding, il sistema:

- Carica e segmenta il documento PDF in chunk
- Genera gli embedding per ciascun chunk utilizzando il provider configurato
- Inserisce i chunk nel database vettoriale Qdrant

![Orchestrator in fase di embedding](docs/images/demo-orchestrator-embedding.png)

### Orchestrator - Fase di Query

Durante l'esecuzione di una query, l'orchestrator:

- Recupera i chunk più rilevanti dal database vettoriale basandosi sulla domanda dell'utente
- Passa i chunk al modello LLM insieme alla domanda
- Genera e restituisce la risposta finale

![Orchestrator in fase di query](docs/images/demo-orchestrator-query.png)

## Quick Start

Per una guida completa, consulta [SETUP.md](SETUP.md).

### Setup Rapido

1. **Avvia Qdrant**:

   ```bash
   docker run -d --name qdrant -p 6333:6333 -v "$(pwd)/qdrant_storage:/qdrant/storage" qdrant/qdrant
   ```

2. **Configura l'ambiente**:

   ```bash
   # Per sviluppo locale con Ollama (default)
   copy env_samples\env.ollama .env

   # Oppure per produzione con OpenAI
   copy env_samples\env.openai .env
   ```

3. **Installa le dipendenze del frontend**:

   ```bash
   cd frontend
   npm install
   cd ..
   ```

4. **Avvia i servizi**:

   ```powershell
   .\start.ps1  # Avvia tutto automaticamente
   ```

   Oppure manualmente:

   ```bash
   # Terminale 1: FastAPI
   uv run uvicorn app:app --host 127.0.0.1 --port 8000

   # Terminale 2: React Frontend
   cd frontend
   npm run dev

   # Terminale 3: Inngest
   npx inngest-cli@latest dev -u http://127.0.0.1:8000/api/inngest --no-discovery
   ```

### Script Utili

- **`start.ps1`**: Avvia/riavvia tutti i servizi (Qdrant, FastAPI, React Frontend, Inngest)
- **`stop.ps1`**: Ferma tutti i servizi

## Configurazione Provider

L'applicazione supporta diversi provider per LLM e embedding. Configura tramite variabili d'ambiente nel file `.env`:

### Locale (Ollama)

```env
LLM_PROVIDER=ollama
EMBEDDING_PROVIDER=ollama
OLLAMA_LLM_MODEL=llama3:8b
OLLAMA_EMBEDDING_MODEL=embeddinggemma:latest
```

### Produzione (OpenAI)

```env
LLM_PROVIDER=openai
EMBEDDING_PROVIDER=openai
OPENAI_API_KEY=sk-...
```

Vedi i file in `env_samples/` per esempi completi di configurazione.

## Struttura del Progetto

```
.
├── app.py                  # FastAPI application entry point
├── src/                    # Codice sorgente Python
│   ├── api/               # Endpoint REST API
│   │   ├── upload.py     # Upload PDF
│   │   ├── query.py      # Query LLM
│   │   └── files.py      # Gestione file embeddati
│   ├── core/              # Core application logic
│   │   ├── config.py     # Gestione configurazione
│   │   ├── data_loader.py # Caricamento e chunking PDF
│   │   ├── vector_db.py  # Interfaccia Qdrant
│   │   └── custom_types.py # Tipi Pydantic
│   └── providers/         # Provider LLM e Embedding
│       ├── llm_providers.py # Provider LLM (Ollama, OpenAI, Google, Anthropic)
│       └── embedding_providers.py # Provider Embedding (Ollama, OpenAI, Google)
├── frontend/              # React + TypeScript frontend
│   ├── src/
│   │   ├── components/   # Componenti React
│   │   ├── hooks/        # Custom hooks
│   │   └── services/     # API client
│   └── package.json
├── uploads/               # File PDF uploadati
├── qdrant_storage/        # Storage Qdrant (persistente)
├── pyproject.toml         # Configurazione progetto Python
├── env_samples/            # Template configurazione (.env)
│   ├── env.ollama         # Configurazione Ollama (locale)
│   ├── env.openai         # Configurazione OpenAI
│   ├── env.google         # Configurazione Google
│   ├── env.anthropic      # Configurazione Anthropic
│   └── env.example        # Esempio completo
├── README.md               # Documentazione principale
└── SETUP.md                # Guida setup completa
```

## Dipendenze

### Backend (Python)

Le dipendenze sono gestite con `uv`. Installa con:

```bash
uv sync
```

### Frontend (Node.js)

Le dipendenze sono gestite con `npm`. Installa con:

```bash
cd frontend
npm install
```

## Documentazione

- [SETUP.md](SETUP.md) - Guida completa per setup e avvio
- `env_samples/env.example` - Esempio completo di configurazione
- `env_samples/env.ollama` - Configurazione per sviluppo locale con Ollama
- `env_samples/env.openai` - Configurazione per produzione con OpenAI
