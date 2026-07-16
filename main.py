import asyncio
from google.adk.runners import InMemoryRunner
from agents.orchestrator import orchestrator_agent

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
