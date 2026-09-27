# OmniAssist — Autonomous Customer Support & Operations Assistant

A simple, interview-friendly GenAI project: an AI customer-support assistant that
answers natural-language queries by **autonomously choosing the right tool** —
a **RAG search over policy documents (ChromaDB)**, an **order-status lookup**, or a
**calculator** — and returns a clean, structured JSON response through a
**FastAPI** microservice.

Built with: **Python · LangChain · NLTK · ChromaDB · FastAPI · sentence-transformers · Pydantic**

---

## Project overview

You send a customer-support query like *"What is your refund policy?"* or
*"What is the status of order ORD1001?"* to the API. OmniAssist then:

1. **Preprocesses the query with NLTK** (lowercase → tokenize → remove stopwords → extract keywords).
2. **Sends the query to a LangChain agent** that has three tools available.
3. The **agent decides which tool to call** (and can call several tools in sequence).
4. Policy questions are answered with a **lightweight RAG pipeline**: dense sentence
   embeddings (all-MiniLM-L6-v2) + **top-k cosine-similarity search over ChromaDB**.
5. The final answer is returned as **structured, Pydantic-validated JSON**, including
   which tool was used.

## Features

- NLTK query preprocessing with keyword extraction
- LangChain tool-calling agent (single agent, up to 5 steps)
- Lightweight RAG over internal policy documents (ChromaDB + dense embeddings)
- Simple operational tools: order-status lookup and a safe calculator
- Structured JSON responses with Pydantic validation (empty/over-long queries rejected)
- Automatic interactive API docs (Swagger UI)

## Architecture

```
User Query
    ↓
FastAPI
    ↓
NLTK Preprocessing
    ↓
LangChain Agent
    ↓
Tool Selection
    ├── Policy Search → ChromaDB → Policy Documents
    ├── Order Status
    └── Calculator
    ↓
Final Answer
    ↓
Structured JSON
```

## Tech stack

| Layer | Technology | Why |
|---|---|---|
| API | FastAPI + Pydantic v2 | async REST endpoints, automatic validation + Swagger docs |
| Preprocessing | NLTK | tokenization, stopword removal, keyword extraction |
| Agent | LangChain (`create_tool_calling_agent` + `AgentExecutor`) | the LLM picks and calls tools |
| RAG | ChromaDB + sentence-transformers `all-MiniLM-L6-v2` | dense embeddings, top-k cosine similarity |
| LLM | any OpenAI-compatible chat model via `OPENAI_API_KEY` | default: `gpt-4o-mini` |

## Project structure

```
OmniAssist/
│
├── app/
│   ├── __init__.py
│   ├── main.py            # FastAPI app: GET / and POST /ask
│   ├── agent.py           # LangChain agent (tool calling loop)
│   ├── tools.py           # policy_search, order_status, calculator
│   ├── rag.py             # ChromaDB vector store + embedding retrieval
│   ├── preprocessing.py   # NLTK: tokenize, stopwords, keywords
│   └── schemas.py         # Pydantic request/response models
│
├── data/
│   ├── refund_policy.txt
│   ├── cancellation_policy.txt
│   ├── shipping_policy.txt
│   └── account_policy.txt
│
├── scripts/
│   └── ingest.py          # builds the ChromaDB vector store
│
├── chroma_db/             # created by the ingestion script (gitignored)
│
├── .env.example
├── .gitignore
├── requirements.txt
├── README.md
└── pyproject.toml
```

## Installation

Requires Python 3.10+.

```bash
git clone https://github.com/ayush1203kr/OmniAssist.git
cd OmniAssist

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

pip install -r requirements.txt
``` 

## RAG ingestion

Build the vector database once (re-run it any time the policy documents change):

```bash
python scripts/ingest.py
```

```
Loading documents...
Loaded 4 policy documents.
Splitting documents into chunks...
Created 5 chunks.
Creating embeddings and storing documents in ChromaDB...
Ingestion completed successfully.
```

The script reads every `.txt` file in `data/`, splits them into small chunks,
embeds each chunk with **all-MiniLM-L6-v2**, and persists everything in
`./chroma_db`.

## Running the API

```bash
uvicorn app.main:app --reload
```

- API: <http://127.0.0.1:8000>
- Swagger docs: <http://127.0.0.1:8000/docs>

## API endpoint

### `GET /`

```json
{ "message": "OmniAssist API is running" }
```

### `POST /ask`

Request body:

```json
{ "query": "Can I get a refund?" }
```

Response:

```json
{
    "query": "Can I get a refund?",
    "answer": "According to the refund policy, customers can request a full refund within 7 days of receiving their order.",
    "keywords": ["refund"],
    "tool_used": "policy_search",
    "tools_used": ["policy_search"]
}
```

- `tool_used` — the primary tool: `policy_search`, `order_status`, `calculator`, or `none`.
- `tools_used` — every tool the agent called, in order (shows multi-step behaviour).
- Invalid input (empty or >1000 characters) returns an automatic HTTP `422` validation error.

## Demo test cases

1. `{"query": "What is the refund policy?"}` → **policy_search** is used.
2. `{"query": "Can I cancel an order after it has shipped?"}` → **policy_search** is used.
3. `{"query": "What is the status of ORD1001?"}` → **order_status** is used.
4. `{"query": "What is 125 * 8?"}` → **calculator** is used.
5. `{"query": "Check ORD1001 and tell me whether I can cancel it."}` → the agent uses
   **order_status** (Shipped) and then **policy_search** (cancellation policy) in sequence.

Quick test with curl:

```bash
curl -X POST http://127.0.0.1:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"query": "What is the refund policy?"}'
```

## How the agent works

`app/agent.py` builds one LangChain tool-calling agent
(`create_tool_calling_agent` + `AgentExecutor`, `max_iterations=5`):

1. The user query (plus the NLTK keywords) goes into the prompt.
2. The LLM answers either with a **tool call** (name + arguments) or with the final text.
3. `AgentExecutor` runs the requested tool and feeds the result back to the model.
4. Steps 2–3 repeat until the model writes the final answer (or 5 steps pass).

Which tools were used is read from the agent's `intermediate_steps` — no internal
reasoning or chain-of-thought is exposed in the API response.

## How ChromaDB is used (the RAG part)

- `scripts/ingest.py` chunks the four policy files
  (`RecursiveCharacterTextSplitter`, 500 chars / 50 overlap) and stores them in a
  **persisted** ChromaDB collection at `./chroma_db`.
- Each chunk is embedded with sentence-transformers **all-MiniLM-L6-v2**
  (384-dimensional dense vectors, L2-normalised so similarity = cosine similarity).
- At query time, `app/rag.py` runs a **top-3 similarity search** over that
  collection and returns the most relevant policy text, which the agent uses to
  answer policy questions with real policy wording.

## How NLTK preprocessing works

`app/preprocessing.py` lowercases the query, tokenizes it with NLTK, removes
punctuation and English stopwords, and returns the remaining keywords:

```python
"Can I get a refund if I cancel my order?"
→ ["get", "refund", "cancel", "order"]
```

The keywords are (a) shown in the API response and (b) passed to the agent as
extra context, so the model starts from a pruned version of the query.

## How the tools work

| Tool | Input | Behaviour |
|---|---|---|
| `policy_search` | a query string | top-3 cosine-similarity chunks from ChromaDB |
| `order_status` | an order ID | looks up an in-memory dict (`ORD1001`–`ORD1004`); returns `"Order not found."` otherwise |
| `calculator` | an expression string | parses with `ast` and evaluates only `+ - * /` on numbers — never a raw `eval()` |

## Interview explanation

**One-line pitch:** *"It's an autonomous support agent: FastAPI receives a query,
NLTK cleans it, a LangChain agent autonomously picks tools — RAG over policy docs
via ChromaDB for policy questions, small deterministic tools for operations — and
returns validated structured JSON."*

Common follow-up questions:

- **Why RAG here?** Policy answers must use the company's actual wording. Instead of
  fine-tuning, we embed the policies once and retrieve the top-3 chunks per query.
- **Why ChromaDB?** It's a lightweight, local, persistent vector database — perfect
  for a small corpus; no extra infrastructure.
- **Why preprocess with NLTK if the LLM sees the raw query?** It prunes noise, gives
  cheap deterministic signal (keywords) for the response and the prompt, and keeps a
  non-LLM layer in the pipeline you can test and extend.
- **How is the agent "autonomous"?** The model itself decides which tool to call and
  in which order — e.g. it can check an order status first, then fetch the
  cancellation policy, then compose the answer.
- **What this project demonstrates:** multi-step tool calling (LangChain), NLTK
  preprocessing, lightweight RAG (ChromaDB + dense sentence embeddings), async
  FastAPI microservice with Pydantic validation and structured JSON outputs.
