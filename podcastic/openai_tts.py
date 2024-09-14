import os
from pathlib import Path
import openai
from tts_services import TTSService, CONFIG

class OpenAITTS(TTSService):
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        openai.api_key = self.api_key

    def generate_audio(self, text: str, output_path: Path, speaker: str) -> Path:
        voice = CONFIG['openai'][speaker]['voice']
        response = openai.audio.speech.create(
            model="tts-1-hd",
            voice=voice,
            input=text
        )
        
        response.stream_to_file(output_path)
        return output_path