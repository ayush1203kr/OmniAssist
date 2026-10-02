# OmniAssist — Autonomous Customer Support & Operations Assistant

## Overview
OmniAssist is a GenAI-powered customer-support and operations assistant built with Gemini, LangChain, RAG, ChromaDB, NLTK, FastAPI, and Streamlit.

It provides one conversational interface for policy questions, order-status lookups, arithmetic, and multi-tool customer-support requests.

## Problem It Solves
- Answers questions from internal policy documents.
- Searches refund, cancellation, shipping, and account policies.
- Checks customer order status.
- Performs basic arithmetic safely.
- Lets an LLM select and combine tools dynamically.
- Exposes the assistant through a REST API.
- Provides a Streamlit chat interface.

Example: `Check ORD1001 and tell me whether I can cancel it.` can require the agent to call `order_status`, then `policy_search`, and combine both results.

## Architecture
```text
Streamlit UI
    | POST /ask
    v
FastAPI
    |
    +--> NLTK preprocessing
    |
    v
LangChain tool-calling agent + Gemini
    |
    +--> policy_search --> ChromaDB --> MiniLM embeddings
    +--> order_status
    +--> calculator
    |
    v
Final natural-language response
```

## End-to-End Flow
1. User enters a question in Streamlit.
2. Streamlit sends `POST /ask` to FastAPI.
3. FastAPI validates the request with Pydantic.
4. NLTK preprocessing lowercases, tokenizes, removes punctuation and stopwords, and extracts keywords.
5. The LangChain agent sends the request to Gemini with the available tools.
6. Gemini decides which tool or tools are required.
7. The selected tools execute and return their results.
8. Policy questions use ChromaDB semantic retrieval.
9. Gemini uses the tool results to produce the final answer.
10. FastAPI returns the answer, keywords, primary tool, and all tools used.

## Agent Tools
### 1. policy_search
Used for refund, cancellation, shipping, and account-policy questions.

Flow:
```text
User question
    -> policy_search
    -> ChromaDB similarity search
    -> relevant policy chunks
    -> Gemini
    -> grounded answer
```

Policy files:
- `data/account_policy.txt`
- `data/cancellation_policy.txt`
- `data/refund_policy.txt`
- `data/shipping_policy.txt`

### 2. order_status
Looks up an order ID such as `ORD1001` and returns its demo status.

| Order ID | Status |
|---|---|
| ORD1001 | Shipped |
| ORD1002 | Processing |
| ORD1003 | Delivered |
| ORD1004 | Cancelled |

### 3. calculator
Performs basic arithmetic using restricted AST evaluation rather than arbitrary Python execution.

Supported operations: `+`, `-`, `*`, `/`.

Example: `125 * 8` -> `1000`.

## RAG Pipeline
RAG has two stages.

### Ingestion
```text
Policy TXT files
    -> document loading
    -> chunking
    -> MiniLM embeddings
    -> ChromaDB
```

Run:
```powershell
uv run python scripts/ingest.py
```

### Retrieval
```text
User policy question
    -> query embedding
    -> ChromaDB similarity search
    -> top relevant chunks
    -> Gemini
    -> grounded answer
```

The project uses `all-MiniLM-L6-v2` embeddings and cosine similarity for policy retrieval.

## Why an Agent?
Instead of hardcoding rules such as `if query contains refund`, the LangChain agent allows Gemini to select tools dynamically.

For example:
```text
Check ORD1001 and tell me whether I can cancel it.
        |
        +--> order_status
        |
        +--> policy_search
        |
        v
   combined answer
```

This demonstrates multi-tool agentic behavior instead of a simple chatbot.

## Technology Stack
| Technology | Purpose |
|---|---|
| Python 3.12 | Main programming language |
| Gemini | LLM and reasoning engine |
| LangChain | Agent and tool calling |
| ChromaDB | Vector database for RAG |
| Sentence Transformers | Policy embeddings |
| NLTK | Query preprocessing |
| FastAPI | REST backend |
| Pydantic | Request and response validation |
| Streamlit | Chat UI |
| HTTPX | Frontend-to-backend HTTP |
| uv | Environment and dependency management |

## Project Structure
```text
OmniAssist/
|-- app/
|   |-- agent.py          # Gemini + LangChain agent
|   |-- main.py           # FastAPI application
|   |-- preprocessing.py  # NLTK preprocessing
|   |-- rag.py            # ChromaDB + embeddings
|   |-- schemas.py        # Pydantic models
|   `-- tools.py          # policy, order, calculator tools
|-- data/
|   |-- account_policy.txt
|   |-- cancellation_policy.txt
|   |-- refund_policy.txt
|   `-- shipping_policy.txt
|-- scripts/
|   `-- ingest.py         # Build ChromaDB index
|-- streamlit_app.py      # Streamlit frontend
|-- setup_windows.ps1     # Windows setup helper
|-- pyproject.toml        # Dependencies
|-- requirements.txt      # pip-compatible dependencies
|-- .env.example          # Environment template
|-- .gitignore
`-- README.md
```

## Setup
Use Python 3.12 and uv.

```powershell
git clone https://github.com/ayush1203kr/OmniAssist.git
cd OmniAssist
uv sync
Copy-Item .env.example .env
```

Add your own Gemini API key to `.env`:
```env
GOOGLE_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-3.8-flash
GEMINI_TEMPERATURE=0
API_URL=http://127.0.0.1:8000
```

Never commit `.env` or an API key.

## Build the RAG Index
```powershell
uv run python scripts/ingest.py
```

The generated `chroma_db` directory is ignored by Git and can be rebuilt from the policy files.

## Run
FastAPI:
```powershell
uv run uvicorn app.main:app --reload
```
API: `http://127.0.0.1:8000`
Swagger: `http://127.0.0.1:8000/docs`

Streamlit:
```powershell
uv run streamlit run streamlit_app.py
```
UI: `http://127.0.0.1:8501`

## API Example
```http
POST /ask
Content-Type: application/json

{
  "query": "What is the refund policy?"
}
```

The response contains the query, extracted keywords, final answer, primary tool, and all tools used.

## Demo Queries
- `What is the refund policy?`
- `How long does standard shipping take?`
- `Can I cancel an order after it has shipped?`
- `What is the status of ORD1001?`
- `What is 125 * 8?`
- `Check ORD1001 and tell me whether I can cancel it.`

## Security
- Gemini credentials are loaded from `.env`.
- `.env` is excluded through `.gitignore`.
- The calculator uses restricted AST evaluation.
- Policy answers are grounded in retrieved documents.
- API requests are validated using Pydantic.

For production, add authentication, authorization, persistent databases, rate limiting, monitoring, secret management, and additional validation.

## GenAI Concepts Demonstrated
- LLM tool calling
- Agentic workflows
- Retrieval-Augmented Generation
- Vector databases
- Embeddings
- Semantic similarity search
- Prompt design
- Query preprocessing
- REST API development
- Frontend/backend separation
- Safe tool execution
- Environment and dependency management

## Future Improvements
- PostgreSQL for persistent order and customer data
- Redis for caching and rate limiting
- JWT or OAuth authentication
- Streaming responses
- Conversation memory
- Human-agent escalation
- Observability and tracing
- Automated tests and CI/CD
- Docker-based deployment

## Author
**Ayush Kumar**

Integrated MSc Mathematics and Computing
Birla Institute of Technology, Mesra