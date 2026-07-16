import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from google import genai
from google.genai import types


load_dotenv()


class GeminiLiveSessionManager:
    """Manages a Vertex AI Gemini Live session."""

    def __init__(self):
        self.project_id = os.environ["GOOGLE_CLOUD_PROJECT"]
        self.location = os.getenv("GEMINI_LIVE_LOCATION", "us-central1")
        self.model_id = os.getenv(
            "GEMINI_LIVE_MODEL",
            "gemini-live-2.5-flash-native-audio",
        )

        print(
            "Initializing Gemini Live client with Vertex AI OAuth "
            f"(project={self.project_id}, location={self.location})..."
        )

        self.client = genai.Client(
            vertexai=True,
            project=self.project_id,
            location=self.location,
        )

    @asynccontextmanager
    async def connect(self, system_instruction=None):
        """Creates and yields an asynchronous Gemini Live session."""

        config = types.LiveConnectConfig(
            response_modalities=["AUDIO"],
            system_instruction=system_instruction,
        )

        print(f"Connecting to Gemini Live (Model: {self.model_id})...")

        try:
            async with self.client.aio.live.connect(
                model=self.model_id,
                config=config,
            ) as session:
                print("Connected to Gemini Live session.")
                yield session
        except Exception as exc:
            print(f"Gemini Live connection failed: {exc}")
            raise
