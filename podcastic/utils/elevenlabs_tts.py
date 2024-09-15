from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs
from pathlib import Path
from rich.console import Console

console = Console()

class ElevenLabsTTS:
    def __init__(self, api_key):
        self.api_key = api_key
        self.client = ElevenLabs(api_key=self.api_key)

    def generate_audio(self, text, output_path, voice_id):
        audio = self.client.text_to_speech.convert(
            voice_id=voice_id,
            text=text,
        )
        with open(output_path, 'wb') as file_out:
            file_out.write(audio)