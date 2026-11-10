# 1–2 minute screen recording script

## Recording setup
- Start the app locally and open it in Chrome.
- Zoom browser to 90–100% so the voice controls and business panel are visible.
- Use a working microphone and allow browser permission.
- Record the browser and microphone using Windows Snipping Tool screen recording, OBS, or Loom.
- Use only the mock seller data in this repository.

## Spoken walkthrough (about 100 seconds)

**0:00–0:12 — Intro**

"Hi Sourav, this is my Mini AI Virtual KAM for the seller experience assignment. I focused on making it a voice-first business assistant, not a generic question-answering bot. This demo uses synthetic seller data."

**0:12–0:30 — Seller calls**

Click **Start voice call** and say:

"My sales have dropped this month. Can you help me understand why?"

Pause for the assistant response and show the transcript.

**0:30–0:55 — Diagnose**

Point to the KPI cards:

"The agent calculates the funnel from the previous and current 30-day periods. In this sample, visits are down 15%, conversion is down 20%, and orders are down about 32%. It also sees in-stock rate falling from 96 to 82 percent and cancellations rising from 3 to 7 percent."

**0:55–1:20 — Take ownership**

"The agent prioritizes stock availability and cancellations before recommending more ad spend. It also gives each recommendation a time horizon and a measurable success metric. The LLM is not allowed to invent the numbers; the backend calculates them."

**1:20–1:40 — Commit**

Say or type: "I can restock the top products today."

Enter the same commitment in the Seller Commitment field and click Confirm. Show the confirmation and the call summary.

**1:40–1:55 — Close**

"Speech input and spoken output run in the browser. FastAPI handles the diagnostic logic, and Gemini is optional for more natural conversation. In production, this would connect to authorized seller data and persist consented follow-ups."

## Backup if speech recognition fails
Use the text input and type the seller's statement. Speech synthesis still reads the assistant's answer aloud in supported browsers. Mention that the browser's speech recognition availability varies.
