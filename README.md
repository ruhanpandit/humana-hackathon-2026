# Humana Resolve

AI-powered claims assistant for healthcare member services. A member or representative asks a question in plain English (typed or spoken), and the system routes it through specialized agents that look up claims, benefits, ROI authorization, and compliance risk, then returns a single plain-language answer with voice playback.

Built at the **Humana Hackathon (July 2026)** by a team of 5:

- Bhoomi Patni
- Dylan Kane
- Ruhan Pandit
- Sai Brinda Akuthota
- Sanjit Kakaria

## How it works

The backend is a FastAPI server (`app.py`) that serves a chat UI and three API endpoints: `/chat`, `/stt` (speech-to-text), and `/tts` (text-to-speech).

When a message arrives at `/chat`, it is handed to an **orchestrator agent** built with the [Google Agent Development Kit (ADK)](https://google.github.io/adk-docs/). The orchestrator decides which sub-agents to invoke and combines their outputs into one response. All agents run on **Gemini 2.5 Flash** via Vertex AI.

```
User (text or voice)
        │
        ▼
   Orchestrator
   ┌────┼────────────┬──────────────┐
   ▼    ▼            ▼              ▼
 Claim  Benefits     ROI         Compliance
 Story  Agent        Agent       Agent
 Agent
   │    │            │              │
   └────┴────────────┴──────────────┘
        │
        ▼
  Combined response (text + voice)
```

### Agents

| Agent | What it does | Tools it calls |
|---|---|---|
| **Claim Story** | Explains claim status, denial reasons, and timelines in plain language | `lookup_claim`, `generate_claim_timeline` |
| **Benefits** | Looks up coverage rules, CPT code descriptions, and cost-sharing details | `lookup_member`, `lookup_benefits`, `lookup_cpt` |
| **ROI** | Checks whether the caller has a valid Release of Information on file (HIPAA) | `check_roi_status` |
| **Compliance** | Scores claims for risk: denial trends, modifier mismatches, provider flags | `calculate_claim_risk`, `lookup_claim`, `lookup_provider` |

The orchestrator may chain agents within a single request. For example, a third-party caller asking about a denied claim triggers the ROI agent first; if authorized, the claim story agent runs next and may hand off to the benefits agent if the denial is coverage-related.

### Voice

- **Speech-to-text:** The browser records audio via MediaRecorder, sends WebM/Opus to `/stt`, which calls the Google Cloud Speech-to-Text API.
- **Text-to-speech:** Agent responses are sent to `/tts`, which uses `edge-tts` (Microsoft Edge neural voices) to generate audio streamed back to the browser.

### Data

All tools read from CSV files in `data/structured/`. The dataset is synthetic and includes claims, members, providers, coverage rules, ROI authorizations, compliance flags, and more. No real member data is used.

## Setup

### Prerequisites

- Python 3.10+
- A Google Cloud project with the Vertex AI and Speech-to-Text APIs enabled
- Application Default Credentials configured (`gcloud auth application-default login`)

### Install dependencies

```bash
pip install -r requirements.txt
```

### Configure environment

Copy the example and fill in your project ID:

```bash
cp .env.example .env
```

### Run

```bash
python app.py
```

The server starts on `http://localhost:8080`. Open it in a browser to use the chat and voice interface.

There is also a CLI REPL for testing without the web UI:

```bash
python main.py
```

### Example questions

- "I'm calling about claim CLM000806. Why was it denied and can it be fixed?"
- "Does member MBR00001's plan cover CPT 83036, and is prior authorization required?"
- "I'm Daniel Barrett, calling for member MBR00001. Can you tell me about their recent claims?"

## Tech stack

- **Agents:** Google Agent Development Kit (ADK) with Gemini 2.5 Flash on Vertex AI
- **Backend:** FastAPI + Uvicorn
- **Frontend:** Single-page HTML/CSS/JS (no build step)
- **Speech-to-text:** Google Cloud Speech-to-Text
- **Text-to-speech:** edge-tts

## Project structure

```
.env.example                          # Environment variable template
.gitignore
README.md
requirements.txt                      # Python dependencies
app.py                                # FastAPI server with /chat, /stt, /tts endpoints
main.py                               # CLI REPL for testing agents without the web UI
index.html                            # Single-page chat and voice UI
agents/
    __init__.py
    orchestrator.py                   # Root agent that routes to sub-agents
    claim_story_agent.py              # Explains claim status, denials, and timelines
    benefits_agent.py                 # Looks up coverage rules and cost-sharing details
    roi_agent.py                      # Checks Release of Information authorization (HIPAA)
    compliance_agent.py               # Scores claims for compliance risk
tools/
    __init__.py
    healthcare_tools.py               # Tool functions called by agents (lookups, risk calc)
    analyze_data.py                   # Data analysis utilities
data/
    hackathon_data.zip                # Original zipped dataset
    structured/                       # CSV files: claims, members, providers, coverage, etc.
    unstructured/
        call_transcripts/             # Sample call transcript text files
        stars_performance_report.md   # Star rating performance report
```
