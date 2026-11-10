# Snapdeal Virtual KAM — Voice-first seller growth agent

A voice-first AI account manager prototype for the Snapdeal AI First Intern assignment. A seller calls because sales have dropped; the assistant diagnoses the funnel, asks targeted follow-ups, prioritizes likely causes, recommends practical experiments, and creates a follow-up action plan.

> Demo data only. This is an independent prototype and is not connected to Snapdeal systems or real seller accounts.

## Product idea

**Not another FAQ bot:** the agent owns a business outcome. It follows a structured diagnostic loop:

1. **Understand the goal:** confirm the sales decline, period, category and urgency.
2. **Inspect seller signals:** compare visits, conversion, price competitiveness, stock, cancellations, ratings and delivery performance with a previous period.
3. **Ask only the missing questions:** clarify availability, recent listing changes, promotion activity and operational constraints.
4. **Prioritize causes:** use deterministic metrics first, then ask the LLM to explain the evidence and rank actions. Do not let the LLM invent metrics.
5. **Commit next steps:** create an action plan with an owner, time horizon and measurable success metric; ask the seller to confirm.
6. **Close the loop:** summarize the call and save a follow-up record in the demo session.

## MVP features

- Browser voice interaction: speech-to-text via the browser Web Speech API and spoken responses via SpeechSynthesis.
- Text fallback for browsers without speech recognition.
- FastAPI backend with a deterministic seller-diagnostics engine.
- Optional Gemini-powered conversational layer. The application remains usable without an API key; the diagnostic engine still works.
- Mock seller data for a single illustrative seller, editable in `data/seller.json`.
- Evidence-based sales funnel analysis: traffic, conversion and order volume.
- Recommended experiments tied to metrics and time windows.
- Call summary, diagnosis and action-plan UI.
- Clear consent and demo-data notice; no real marketplace writes.

## Architecture

```text
Browser (voice UI)
  ├─ SpeechRecognition (seller speech -> transcript)
  ├─ fetch /api/analyze (seller metrics + seller concern)
  └─ SpeechSynthesis (assistant response -> voice)
             |
             v
         FastAPI
  ├─ diagnostics.py: calculate funnel deltas + identify signals
  ├─ agent.py: optional Gemini explanation / follow-up phrasing
  ├─ plans.py: action-plan templates and follow-up records
  └─ data/seller.json: mock seller account snapshot
```

The core insight is to make numerical diagnosis independent from generative AI. The model can explain and converse, but it must ground recommendations in computed facts.

## Example scenario

The sample seller reports: "My sales have dropped this month."

Illustrative sample data in this repository indicates:
- Visits: 12,000 -> 10,200 (-15%)
- Conversion rate: 3.0% -> 2.4% (-20%)
- Orders: 360 -> 245 (-31.9%)
- In-stock rate: 96% -> 82%
- Cancellation rate: 3% -> 7%
- Average rating: 4.2 -> 3.9

The system should not jump to "run ads". It should explain that traffic and conversion both declined, while availability, cancellations and rating are additional warning signals. It recommends checking stock-outs and cancellation reasons first, then improving listing conversion and testing a controlled promotion only after availability is stable.

## Tech stack

| Layer | Technology | Why |
|---|---|---|
| UI | HTML, CSS, JavaScript | Small, fast, no build step |
| Voice input | Web Speech API | Native browser speech recognition where available |
| Voice output | SpeechSynthesis API | Native spoken responses |
| API | Python, FastAPI, Uvicorn | Lightweight typed backend |
| Business logic | Python | Auditable calculations and deterministic rules |
| Optional LLM | Google Gemini API | Natural dialogue and grounded explanation |
| Data | JSON mock seller profile | Reproducible demo; no private data |

## Run locally (Windows PowerShell)

1. Install Python 3.10+.
2. Open a terminal in this folder:

```powershell
cd snapdeal-virtual-kam
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

3. Optional: set a Gemini key in `.env`. The deterministic demo works without it.

```env
GOOGLE_API_KEY=
GEMINI_MODEL=gemini-2.5-flash
```

4. Start the app:

```powershell
uvicorn app.main:app --reload
```

5. Open [http://127.0.0.1:8000](http://127.0.0.1:8000). Allow microphone access and use Chrome or Edge for the best browser speech support.

## Run on macOS / Linux

```bash
cd snapdeal-virtual-kam
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

## Demo script (1–2 minutes)

**0:00–0:15 — Start:** Open the dashboard, point out that this is a voice-first seller call assistant using synthetic data. Click "Start call" and allow the microphone.

**0:15–0:35 — Seller concern:** Say: "My sales have dropped this month. I don't know why." The assistant acknowledges the concern and begins the analysis.

**0:35–1:00 — Evidence:** The assistant says that visits fell 15%, conversion fell 20%, and orders fell about 32%. It also highlights the lower in-stock rate and increased cancellations. Show the funnel and risk indicators on screen.

**1:00–1:25 — Action ownership:** Ask: "What should I do first?" The assistant prioritizes restoring stock availability and investigating cancellations, then suggests improving listing content and a controlled price/promotion test.

**1:25–1:45 — Commitment:** Say: "I can restock the top products today." The assistant records the seller commitment, a next step and a success metric. Show the action-plan panel.

**1:45–2:00 — Close:** Show the call summary and explain that the diagnostic logic is deterministic and the LLM is optional for natural conversation.

## Important design decisions

- **Voice-first but graceful:** speech recognition is browser-dependent. A text input remains available for unsupported browsers and reliable testing.
- **No fabricated insights:** all percentages and funnel values are calculated by backend functions from the mock snapshot.
- **LLM is optional:** a missing API key never breaks the demo. The LLM is not asked to calculate KPIs.
- **Seller ownership:** advice becomes an explicit action with a time horizon and a measurable result.
- **No unauthorized actions:** the prototype proposes actions; it does not edit listings, change prices, launch campaigns or contact customers.
- **Privacy:** the demo uses synthetic data. A real rollout would require consent, authentication, access controls, audit logs, retention limits and seller-specific authorization.

## Limitations and next steps

1. Replace JSON with an authenticated marketplace data API and event stream.
2. Add Hindi and other Indian language ASR/TTS and test accents/noisy calls.
3. Persist seller history, recommendations, commitments and outcomes in PostgreSQL.
4. Add role-based tool permissions and seller confirmation before any write action.
5. Add experiments/attribution to estimate incremental sales lift rather than claiming causality.
6. Add call recording consent, redaction, monitoring, retries and human handoff.
7. Evaluate recommendation quality with seller-support specialists and offline replay tests.

## AI and voice technology note

- **Speech input:** browser Web Speech API `SpeechRecognition` (Chrome/Edge support varies by operating system and browser version).
- **Speech output:** browser `speechSynthesis` with the best available voice for English.
- **Reasoning:** Python diagnostic rules compute actual changes, signal severity and action priorities. Optional Google Gemini `gemini-2.5-flash` can produce natural-language turns from these verified facts. It is configured through `GOOGLE_API_KEY`.
- **Why this split:** financial and operational figures should be calculated by code; an LLM is useful for flexible dialogue, not as the source of truth.

## Repository

This assignment is contained in `snapdeal-virtual-kam/` so it remains separate from the existing OmniAssist project.
