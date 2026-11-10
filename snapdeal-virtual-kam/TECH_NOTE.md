# AI models and voice technologies

## Voice interface
- **Speech-to-text:** Browser Web Speech API (`SpeechRecognition` / `webkitSpeechRecognition`). It converts the seller's spoken input into text in supported browsers. Language is set to `en-IN` for the demo.
- **Text-to-speech:** Browser `speechSynthesis` and `SpeechSynthesisUtterance`. It speaks the agent response using an available English India voice when installed, otherwise an available English voice.
- A typed-input fallback is included because SpeechRecognition support varies between browsers and operating systems. The prototype does not upload or store raw audio by itself; browser speech services may have their own processing/privacy behavior.

## Reasoning and business logic
- **Deterministic Python analytics:** calculates visits, orders, revenue and conversion changes, then applies explicit thresholds to identify traffic, conversion, stock, cancellation and rating risks.
- **Optional LLM:** Google Gemini via the Google Gen AI SDK, default model configured as `gemini-2.5-flash`. It receives computed facts and action plans, not raw authority to invent or calculate metrics. Configure `GOOGLE_API_KEY`; without it, a deterministic response keeps the demo working.
- **Why hybrid:** business diagnosis must be reproducible and auditable. Generative AI is used to make the interaction conversational, while calculations and priority rules remain code-driven.

## Production considerations
A real account manager needs seller consent, authenticated seller identity, scoped data access, data minimization, audit trails, call-quality monitoring, human escalation, localized languages and explicit confirmation before any write operation (such as changing a listing or launching a campaign). This assignment demo does not take real marketplace actions.
