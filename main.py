import asyncio
import os
from dotenv import load_dotenv
from google.adk.runners import InMemoryRunner
from google.adk import Agent
from agents.orchestrator import orchestrator_agent

# Load environment variables
load_dotenv()

# Use Vertex AI backend by specifying the full model path
# This resolves "PERMISSION_DENIED" errors on the public Gemini API
PROJECT_ID = "qwiklabs-gcp-01-f01da7845174"
LOCATION = "us-central1"
MODEL_PATH = f"projects/{PROJECT_ID}/locations/{LOCATION}/publishers/google/models/gemini-2.5-flash"
Agent.set_default_model(MODEL_PATH)

async def main():
    # Initialize the runner with our root orchestrator
    runner = InMemoryRunner(agent=orchestrator_agent)
    
    print("--- Healthcare Multi-Agent Pipeline ---")
    print("Type 'exit' to quit.\n")
    
    while True:
        user_input = input("User: ")
        if user_input.lower() in ['exit', 'quit']:
            break
            
        print("\nOrchestrating response...\n")
        
        # run_debug is a convenience method for testing
        # It handles session creation and prints events (including tool calls if verbose=True)
        events = await runner.run_debug(
            user_input, 
            verbose=True  # Set to True to see tool calls and subagent delegation
        )
        
        # The last event usually contains the final response
        # In a real app, you'd iterate through events or use run_async
        print("-" * 40)

if __name__ == "__main__":
    asyncio.run(main())
