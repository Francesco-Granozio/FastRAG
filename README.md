# RAG Application

Applicazione RAG (Retrieval-Augmented Generation) per l'ingest e query di documenti PDF utilizzando modelli LLM e embedding configurabili.

## Caratteristiche

- **Provider LLM configurabili**: Ollama (locale), OpenAI, Google Gemini, Anthropic Claude
- **Provider Embedding configurabili**: Ollama, OpenAI, Google
- **Vector Database**: Qdrant per la ricerca semantica
- **Workflow**: Inngest per la gestione asincrona delle operazioni
- **Frontend**: Streamlit per l'interfaccia utente
- **Backend**: FastAPI con endpoint Inngest

## Quick Start

Per una guida completa, consulta [SETUP.md](SETUP.md).

### Setup Rapido

1. **Avvia Qdrant**:

   ```bash
   docker run -d --name qdrant -p 6333:6333 -v "$(pwd)/qdrant_storage:/qdrant/storage" qdrant/qdrant
   ```

2. **Configura l'ambiente**:

   ```bash
   copy env.ollama .env  # Per sviluppo locale
   # Oppure
   copy env.openai .env  # Per produzione
   ```

3. **Avvia i servizi**:

   ```powershell
   .\start.ps1  # Avvia tutto automaticamente
   ```

   Oppure manualmente:

   ```bash
   # Terminale 1: FastAPI
   uv run uvicorn main:app --host 127.0.0.1 --port 8000

   # Terminale 2: Streamlit
   uv run streamlit run streamlit_app.py

   # Terminale 3: Inngest
   npx inngest-cli@latest dev -u http://127.0.0.1:8000/api/inngest --no-discovery
   ```

### Script Utili

- **`start.ps1`**: Avvia/riavvia tutti i servizi (Qdrant, FastAPI, Streamlit, Inngest)
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

Vedi i file `env.*` per esempi completi di configurazione.

## Struttura del Progetto

```
.
├── main.py                 # FastAPI app con funzioni Inngest
├── streamlit_app.py        # Interfaccia Streamlit
├── data_loader.py          # Caricamento e chunking PDF
├── vector_db.py            # Interfaccia Qdrant
├── config.py               # Gestione configurazione
├── llm_providers.py        # Provider LLM (Ollama, OpenAI, Google, Anthropic)
├── embedding_providers.py  # Provider Embedding (Ollama, OpenAI, Google)
├── custom_types.py         # Tipi Pydantic
├── env.*                   # Template configurazione
└── SETUP.md                # Guida setup completa
```

## Dipendenze

Le dipendenze sono gestite con `uv`. Installa con:

```bash
uv sync
```

## Documentazione

- [SETUP.md](SETUP.md) - Guida completa per setup e avvio
- File `env.example` - Esempi di configurazione
