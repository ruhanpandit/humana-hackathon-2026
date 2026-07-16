import os
import re
import json
from collections import Counter, defaultdict

TRANSCRIPT_DIR = "humana-hackathon-2026/data/unstructured/call_transcripts"


def _read_text_file(path):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def _extract_duration_minutes(content):
    """
    Handles formats like:
    Duration: 8 minutes
    Duration: 8 min
    Call Duration: 8 minutes
    """
    patterns = [
        r"Duration:\s*(\d+(?:\.\d+)?)\s*(?:minutes|minute|min|mins)",
        r"Call Duration:\s*(\d+(?:\.\d+)?)\s*(?:minutes|minute|min|mins)",
    ]

    for pattern in patterns:
        match = re.search(pattern, content, flags=re.IGNORECASE)
        if match:
            return float(match.group(1))

    return None


def _extract_scenario(content, filename):
    """
    Handles:
    Scenario: Claim denial explanation
    """
    match = re.search(r"Scenario:\s*(.+)", content, flags=re.IGNORECASE)
    if match:
        return match.group(1).strip()

    # fallback from filename
    return filename.replace(".txt", "").replace("_", " ").title()


def _count_speaker_turns(content):
    """
    Counts speaker turns if transcript has lines like:
    Agent:
    Member:
    Caller:
    Representative:
    """
    turns = 0
    speaker_counts = Counter()

    for line in content.splitlines():
        speaker_match = re.match(
            r"^\s*(Agent|Member|Caller|Representative|Rep|Customer|Assistant|Patient)\s*:",
            line,
            flags=re.IGNORECASE,
        )
        if speaker_match:
            turns += 1
            speaker = speaker_match.group(1).lower()
            speaker_counts[speaker] += 1

    return turns, dict(speaker_counts)


def _keyword_count(content, keywords):
    content_lower = content.lower()
    return sum(content_lower.count(k.lower()) for k in keywords)


def _detect_topics(content):
    """
    Simple keyword-based topic detection for dashboard stats.
    Adjust these to match your actual problem statement.
    """
    topic_keywords = {
        "claims": ["claim", "denied", "denial", "modifier", "billing", "procedure"],
        "benefits": ["benefit", "coverage", "covered", "copay", "deductible"],
        "prior_authorization": ["prior authorization", "preauth", "authorization", "approved", "approval"],
        "roi": ["roi", "release of information", "authorization expired", "expired authorization"],
        "care_gaps": ["care gap", "screening", "preventive", "stars", "measure"],
        "provider": ["provider", "doctor", "pcp", "specialist"],
        "appointment": ["appointment", "schedule", "slot", "available"],
        "compliance": ["compliance", "flag", "risk", "audit"],
    }

    detected = []
    for topic, keywords in topic_keywords.items():
        if _keyword_count(content, keywords) > 0:
            detected.append(topic)

    return detected


def analyze_call_transcripts(transcript_dir=TRANSCRIPT_DIR):
    if not os.path.exists(transcript_dir):
        return {
            "error": f"Transcript directory not found: {transcript_dir}",
            "total_transcripts": 0,
        }

    transcript_files = [
        f for f in os.listdir(transcript_dir)
        if f.lower().endswith(".txt")
    ]

    durations = []
    scenarios = Counter()
    topic_counts = Counter()
    speaker_turns = []
    transcript_details = []

    escalation_keywords = [
        "supervisor",
        "escalate",
        "manager",
        "call back",
        "follow up",
        "case number",
        "unable to resolve",
    ]

    frustration_keywords = [
        "frustrated",
        "confused",
        "upset",
        "angry",
        "waiting",
        "again",
        "not helpful",
        "don't understand",
    ]

    resolution_keywords = [
        "resolved",
        "next steps",
        "confirmation",
        "approved",
        "completed",
        "submitted",
        "fixed",
    ]

    total_escalation_mentions = 0
    total_frustration_mentions = 0
    total_resolution_mentions = 0

    for filename in transcript_files:
        path = os.path.join(transcript_dir, filename)
        content = _read_text_file(path)

        duration = _extract_duration_minutes(content)
        if duration is not None:
            durations.append(duration)

        scenario = _extract_scenario(content, filename)
        scenarios[scenario] += 1

        turns, speaker_counts = _count_speaker_turns(content)
        speaker_turns.append(turns)

        topics = _detect_topics(content)
        for topic in topics:
            topic_counts[topic] += 1

        escalation_mentions = _keyword_count(content, escalation_keywords)
        frustration_mentions = _keyword_count(content, frustration_keywords)
        resolution_mentions = _keyword_count(content, resolution_keywords)

        total_escalation_mentions += escalation_mentions
        total_frustration_mentions += frustration_mentions
        total_resolution_mentions += resolution_mentions

        transcript_details.append({
            "filename": filename,
            "scenario": scenario,
            "duration_minutes": duration,
            "speaker_turns": turns,
            "speaker_counts": speaker_counts,
            "topics": topics,
            "escalation_mentions": escalation_mentions,
            "frustration_mentions": frustration_mentions,
            "resolution_mentions": resolution_mentions,
        })

    total_transcripts = len(transcript_files)
    avg_duration = sum(durations) / len(durations) if durations else 0
    min_duration = min(durations) if durations else 0
    max_duration = max(durations) if durations else 0
    avg_turns = sum(speaker_turns) / len(speaker_turns) if speaker_turns else 0

    return {
        "total_transcripts": total_transcripts,
        "transcripts_with_duration": len(durations),
        "average_duration_minutes": round(avg_duration, 2),
        "average_duration_seconds": round(avg_duration * 60, 0),
        "min_duration_minutes": round(min_duration, 2),
        "max_duration_minutes": round(max_duration, 2),
        "average_speaker_turns": round(avg_turns, 1),
        "scenarios": dict(scenarios),
        "topic_counts": dict(topic_counts),
        "quality_signals": {
            "escalation_mentions": total_escalation_mentions,
            "frustration_mentions": total_frustration_mentions,
            "resolution_mentions": total_resolution_mentions,
        },
        "transcript_details": transcript_details,
    }


if __name__ == "__main__":
    results = analyze_call_transcripts()
    print(json.dumps(results, indent=2))