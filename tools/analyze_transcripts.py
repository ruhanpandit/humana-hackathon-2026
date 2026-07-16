import os
import re
import json

TRANSCRIPT_DIR = "humana-hackathon-2026/data/unstructured/call_transcripts"

def analyze_transcripts():
    durations = []
    scenarios = {}
    total_calls = 0
    
    if not os.path.exists(TRANSCRIPT_DIR):
        return {"error": "Transcript directory not found"}
        
    for filename in os.listdir(TRANSCRIPT_DIR):
        if filename.endswith(".txt"):
            path = os.path.join(TRANSCRIPT_DIR, filename)
            with open(path, 'r') as f:
                content = f.read()
                
                # Extract Duration
                duration_match = re.search(r"Duration:\s*(\d+)\s*minutes", content)
                if duration_match:
                    dur = int(duration_match.group(1))
                    durations.append(dur)
                
                # Extract Scenario
                scenario_match = re.search(r"Scenario:\s*(.*)", content)
                if scenario_match:
                    scenario = scenario_match.group(1).strip()
                    scenarios[scenario] = scenarios.get(scenario, 0) + 1
                
                total_calls += 1

    avg_duration_min = sum(durations) / len(durations) if durations else 0
    
    return {
        "total_transcripts": total_calls,
        "average_duration_minutes": round(avg_duration_min, 1),
        "average_duration_seconds": round(avg_duration_min * 60, 0),
        "scenarios": scenarios,
        "min_duration": min(durations) if durations else 0,
        "max_duration": max(durations) if durations else 0
    }

if __name__ == "__main__":
    results = analyze_transcripts()
    print(json.dumps(results, indent=2))
