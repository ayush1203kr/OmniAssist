# OmniAssist — Autonomous Customer Support & Operations Assistant

Interview-friendly GenAI project combining **Gemini, LangChain, NLTK, ChromaDB RAG, FastAPI and Streamlit**.

## Architecture

```text
Streamlit UI
    │ POST /ask
    ▼
FastAPI
    │
    ├── NLTK preprocessing
    └── LangChain tool-calling agent
            ├── policy_search → ChromaDB → MiniLM embeddings
            ├── order_status
            └── calculator
                    │
                  Gemini
```

## Features

- Gemini tool-calling agent using LangChain.
- Policy RAG with ChromaDB, `all-MiniLM-L6-v2`, normalized dense embeddings and cosine similarity.
- NLTK preprocessing with a lightweight fallback if optional native NLP dependencies are unavailable.
- Deterministic order-status and safe arithmetic tools.
- FastAPI `/ask` REST endpoint with Pydantic validation.
- Streamlit chat UI that calls the FastAPI backend.

## Windows setup

Use Python 3.12 and `uv`. From the project directory:

```powershell
uv sync
Copy-Item .env.example .env
```

Put your Gemini key in `.env` only; never commit it.

```env
GOOGLE_API_KEY=
GEMINI_MODEL=gemini-3.8-flash
GEMINI_TEMPERATURE=0
API_URL=http://127.0.0.1:8000
```

If `chroma_db` needs to be rebuilt after changing policy files:

```powershell
uv run python scripts/ingest.py
```

## Run

### Terminal 1 — FastAPI

```powershell
uv run uvicorn app.main:app --reload
```

API: `http://127.0.0.1:8000`
Swagger: `http://127.0.0.1:8000/docs`

### Terminal 2 — Streamlit

```powershell
uv run streamlit run streamlit_app.py
```

UI: `http://127.0.0.1:8501`

## API example

```json
POST /ask
{"query":"What is the refund policy?"}
```

The response contains the answer, extracted keywords, primary tool and all tools used.

## Demo queries

- `What is the refund policy?`
- `Can I cancel an order after it has shipped?`
- `What is the status of ORD1001?`
- `What is 125 * 8?`
- `Check ORD1001 and tell me whether I can cancel it.`

## Important

The project does not require `scikit-learn` directly. Removing that unnecessary native dependency avoids the Windows `vcomp140.dll` failure that can prevent NLTK from importing. NumPy and SciPy are pinned to stable Python 3.12-compatible versions.
