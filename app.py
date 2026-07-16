import os, sys, uuid, uvicorn
from pathlib import Path
from typing import Optional
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load agents
from dotenv import load_dotenv; load_dotenv()
from google.adk.runners import InMemoryRunner
from google.adk import Agent
from agents.orchestrator import orchestrator_agent

PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "qwiklabs-gcp-01-f01da7845174")
LOCATION   = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
Agent.set_default_model(
    f"projects/{PROJECT_ID}/locations/{LOCATION}/publishers/google/models/gemini-2.5-flash"
)
runner = InMemoryRunner(agent=orchestrator_agent)

app = FastAPI()

class Msg(BaseModel):
    message: str
    session_id: Optional[str] = None

@app.get("/", response_class=HTMLResponse)
def root():
    return HTMLResponse((Path(__file__).parent / "index.html").read_text(encoding="utf-8"))

@app.post("/chat")
async def chat(req: Msg):
    sid = req.session_id or str(uuid.uuid4())
    try:
        events = await runner.run_debug(req.message, verbose=False)
        text = ""
        for ev in events:
            if hasattr(ev, "content") and ev.content:
                for part in ev.content.parts:
                    if hasattr(part, "text") and part.text:
                        text = part.text
        return {"reply": text or "No response.", "session_id": sid}
    except Exception as e:
        return {"reply": f"Error: {e}", "session_id": sid}

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8080, reload=False)
