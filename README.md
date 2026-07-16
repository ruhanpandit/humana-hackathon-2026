# Healthcare Multi-Agent Pipeline

This project implements a multi-agent system for healthcare member services using the Google Agent Development Kit (ADK).

## Project Structure

- `agents/`: Contains agent definitions and system instructions.
  - `orchestrator.py`: Root agent that delegates to specialized subagents.
  - `claim_story_agent.py`: Explains claims and denials.
  - `benefits_agent.py`: Handles coverage and benefits lookups.
  - `roi_agent.py`: Verifies Release of Information (ROI) status.
  - `compliance_agent.py`: Monitors for risk and systemic issues.
- `tools/`: Reusable healthcare data tools.
  - `healthcare_tools.py`: Implementation of `lookup_claim`, `lookup_member`, etc.
- `data/`: Mock healthcare datasets (CSV).
- `prompts/`: (Optional) Externalized prompt templates.
- `main.py`: Entry point for running the orchestrator.

## Orchestrator Routing

The `Healthcare Orchestrator` intelligently routes tasks based on the user's intent:

1. **Inquiry Analysis**: The orchestrator receives the user's request.
2. **ROI Verification**: If the request involves member data, it may first invoke the `ROI Agent` to ensure privacy compliance.
3. **Delegation**: 
   - Requests about claim status or denials are sent to the `Claim Story Agent`.
   - General coverage or procedure questions are sent to the `Benefits Agent`.
   - If the `Claim Story Agent` identifies a potential systemic error or high-risk provider, the `Compliance Agent` is invoked.
4. **Synthesis**: The orchestrator combines insights from all active subagents into a final, plain-language response for the member.

## Tools

The following tools are available to the agents:

- `lookup_claim(claim_id)`
- `lookup_member(member_id)`
- `lookup_provider(provider_id)`
- `lookup_benefits(member_id, cpt_code)`
- `lookup_cpt(cpt_code)`
- `check_prior_authorization(claim_id)`
- `check_roi_status(member_id, caller_name)`
- `generate_claim_timeline(claim_id)`
- `calculate_claim_risk(claim_id)`

## Running the Pipeline

Ensure `google-adk` is installed and run:

```bash
python3 main.py
```

## Gemini Live Voice Integration

A voice layer has been added to allow real-time interaction via the Gemini Multimodal Live API.

### Setup

1. Update package index and install system dependencies (for audio):
   ```bash
   sudo apt-get update
   sudo apt-get install -y portaudio19-dev
   ```
2. Install Python dependencies:
   ```bash
   pip install pyaudio google-genai
   ```
3. Ensure your `.env` contains:
   - `PROJECT_ID`: Your GCP Project ID.
   - `LOCATION`: GCP region (e.g., `us-central1`).
   - `GOOGLE_API_KEY`: A valid API key if not using Vertex AI ADC.

> **Note on Cloud Shell**: Real-time audio capture via `PyAudio` requires access to local microphone hardware. If running in Google Cloud Shell, you may need to run the application in a local environment or use a tool to bridge your local audio to the remote session.

### Running Voice Mode

Execute the voice application:

```bash
python3 voice_app.py
```

### Architecture
- **Voice Interface**: `voice_app.py` manages microphone audio and Gemini Live session.
- **Session Manager**: `voice/live_session.py` handles the connection to the Multimodal Live API.
- **ADK Bridge**: `voice/adk_bridge.py` routes transcripts to the existing Healthcare Orchestrator and returns synthesized text to be spoken.
