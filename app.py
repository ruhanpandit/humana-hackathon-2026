import os, sys, uuid, uvicorn
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse, Response
from pydantic import BaseModel
from google.cloud import speech, texttospeech

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tools.analyze_data import analyze_synthetic_data

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

speech_client = speech.SpeechClient()
tts_client    = texttospeech.TextToSpeechClient()

app = FastAPI()

class Msg(BaseModel):
    message: str
    session_id: Optional[str] = None

class TTSReq(BaseModel):
    text: str

@app.get("/impact")
def impact():
    return analyze_synthetic_data()

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

@app.post("/stt")
async def stt(audio: UploadFile = File(...)):
    content = await audio.read()
    audio_obj = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.WEBM_OPUS,
        sample_rate_hertz=48000,
        language_code="en-US",
    )
    result = speech_client.recognize(config=config, audio=audio_obj)
    transcript = " ".join(r.alternatives[0].transcript for r in result.results)
    return {"transcript": transcript}

@app.post("/tts")
async def tts(req: TTSReq):
    synthesis_input = texttospeech.SynthesisInput(text=req.text[:5000])
    voice = texttospeech.VoiceSelectionParams(
        language_code="en-US",
        name="en-US-Neural2-F",
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )
    resp = tts_client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )
    return Response(content=resp.audio_content, media_type="audio/mpeg")

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8080, reload=False)
