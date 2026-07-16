import os
import asyncio
from dotenv import load_dotenv
from google.adk.runners import InMemoryRunner
from google.adk import Agent
from agents.orchestrator import orchestrator_agent

# Load environment variables
load_dotenv()

# Configuration from environment or defaults
PROJECT_ID = os.getenv("PROJECT_ID", "qwiklabs-gcp-01-f01da7845174")
LOCATION = os.getenv("LOCATION", "us-central1")
# Using gemini-2.5-flash for background ADK tasks for stability
MODEL_PATH = f"projects/{PROJECT_ID}/locations/{LOCATION}/publishers/google/models/gemini-2.5-flash"

# Ensure the ADK is using the correct model path
Agent.set_default_model(MODEL_PATH)

# Initialize the runner globally for the bridge
runner = InMemoryRunner(agent=orchestrator_agent)

async def run_orchestrator(user_text: str) -> str:
    """
    Calls the existing ADK orchestrator with user text and returns the final synthesized response.
    """
    try:
        # Run the orchestrator. quiet=True prevents double printing to console.
        events = await runner.run_debug(user_text, verbose=False, quiet=True)
        
        response_parts = []
        for event in events:
            # We look for events authored by the root orchestrator agent
            if event.author == "healthcare_orchestrator":
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if part.text:
                            response_parts.append(part.text)
        
        final_text = "".join(response_parts).strip()
        
        # Robust fallback: find the last text-containing model event
        if not final_text and events:
            for event in reversed(events):
                if event.author != "user" and event.content and event.content.parts:
                    for part in event.content.parts:
                        if part.text:
                            return part.text.strip()
                            
        return final_text or "I'm sorry, I couldn't generate a response."
        
    except Exception as e:
        print(f"Error in ADK bridge: {e}")
        return f"I encountered an error processing your request: {str(e)}"
