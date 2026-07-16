import asyncio
import os
import sys

from dotenv import load_dotenv

from voice.adk_bridge import run_orchestrator
from voice.live_session import GeminiLiveSessionManager


load_dotenv()

MIC_REQUESTED = os.getenv("VOICE_ENABLE_MIC", "false").lower() in {
    "1",
    "true",
    "yes",
}

try:
    if MIC_REQUESTED:
        import pyaudio

        HAS_PYAUDIO = True
    else:
        pyaudio = None
        HAS_PYAUDIO = False
except ImportError:
    pyaudio = None
    HAS_PYAUDIO = False


FORMAT = pyaudio.paInt16 if HAS_PYAUDIO else None
CHANNELS = 1
RATE = 16000
CHUNK = 512


class VoiceApp:
    def __init__(self):
        self.manager = GeminiLiveSessionManager()
        self.p = None
        self.audio_stream = None
        self.has_mic = False

        if HAS_PYAUDIO:
            try:
                self.p = pyaudio.PyAudio()

                input_devices = []

                for index in range(self.p.get_device_count()):
                    info = self.p.get_device_info_by_index(index)

                    if int(info.get("maxInputChannels", 0)) > 0:
                        input_devices.append(index)

                self.has_mic = bool(input_devices)

                if not self.has_mic:
                    print(
                        "No microphone input device was found. "
                        "Using terminal input."
                    )
            except Exception as exc:
                print(
                    f"Microphone initialization unavailable: {exc}. "
                    "Using terminal input."
                )
                self.has_mic = False

    async def start(self):
        system_instruction = (
            "You are the voice interface for a Healthcare Member Services "
            "system. Speak the backend response clearly and professionally. "
            "Do not invent or alter healthcare information."
        )

        try:
            print("Attempting to connect to Gemini Live...")

            async with self.manager.connect(
                system_instruction=system_instruction
            ) as session:
                tasks = [
                    asyncio.create_task(
                        self.receive_messages_loop(session)
                    )
                ]

                if self.has_mic:
                    print("Microphone mode enabled.")
                    tasks.append(
                        asyncio.create_task(self.send_audio_loop(session))
                    )
                else:
                    print("Terminal input mode enabled.")
                    tasks.append(
                        asyncio.create_task(self.text_input_loop(session))
                    )

                await asyncio.gather(*tasks)

        except Exception as exc:
            print(f"\nGemini Live session failed: {exc}")
            print("Starting terminal-only mode without the Live relay.")
            await self.text_input_loop(None)

        finally:
            await self.cleanup()

    async def text_input_loop(self, session):
        """Reads terminal input and sends it to the ADK orchestrator."""

        print("\nType a message and press Enter. Press Ctrl+C to quit.\n")

        loop = asyncio.get_running_loop()

        while True:
            try:
                user_input = await loop.run_in_executor(
                    None,
                    sys.stdin.readline,
                )

                if not user_input:
                    break

                user_input = user_input.strip()

                if not user_input:
                    continue

                print(f"\n{user_input}")
                print(">>> Querying ADK Orchestrator...")

                adk_response = await run_orchestrator(user_input)
                print(f"[ADK Response]: {adk_response}")

                if session and adk_response:
                    try:
                        await session.send_realtime_input(
                            text=(
                                "Speak the following backend response exactly "
                                "and do not add new information:\n\n"
                                f"{adk_response}"
                            )
                        )
                    except Exception as exc:
                        print(f"Could not send response to Live session: {exc}")

            except EOFError:
                break

    async def send_audio_loop(self, session):
        """Captures microphone audio and streams PCM data to Gemini Live."""

        try:
            self.audio_stream = self.p.open(
                format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK,
            )

            print("\n>>> Voice session active. Speak now.")

            while True:
                data = await asyncio.to_thread(
                    self.audio_stream.read,
                    CHUNK,
                    False,
                )

                await session.send_realtime_input(
                    audio={
                        "data": data,
                        "mime_type": "audio/pcm;rate=16000",
                    }
                )

        except Exception as exc:
            print(f"Microphone streaming error: {exc}")

    async def receive_messages_loop(self, session):
        """Receives transcriptions and model output from Gemini Live."""

        async for message in session.receive():
            server_content = getattr(message, "server_content", None)

            if not server_content:
                continue

            input_transcription = getattr(
                server_content,
                "input_transcription",
                None,
            )

            if input_transcription:
                user_text = getattr(input_transcription, "text", "").strip()

                if user_text:
                    print(f"\n[User Transcript]: {user_text}")
                    print(">>> Querying ADK Orchestrator...")

                    adk_response = await run_orchestrator(user_text)
                    print(f"[ADK Response]: {adk_response}")

                    if adk_response:
                        await session.send_realtime_input(
                            text=(
                                "Speak the following backend response exactly "
                                "and do not add new information:\n\n"
                                f"{adk_response}"
                            )
                        )

            output_transcription = getattr(
                server_content,
                "output_transcription",
                None,
            )

            if output_transcription:
                text = getattr(output_transcription, "text", "")

                if text:
                    print(text, end="", flush=True)

    async def cleanup(self):
        if self.audio_stream:
            self.audio_stream.stop_stream()
            self.audio_stream.close()

        if self.p:
            self.p.terminate()


if __name__ == "__main__":
    app = VoiceApp()

    try:
        asyncio.run(app.start())
    except KeyboardInterrupt:
        print("\nClosing voice application...")
