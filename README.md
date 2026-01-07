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
