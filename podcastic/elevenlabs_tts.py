import os
from pathlib import Path
import requests
from tts_services import TTSService, CONFIG

class ElevenLabsTTS(TTSService):
    def __init__(self):
        self.api_key = os.getenv("ELEVEN_LABS_API_KEY")
        if not self.api_key:
            raise ValueError("ELEVEN_LABS_API_KEY environment variable is not set")

    def generate_audio(self, text: str, output_path: Path, speaker: str) -> Path:
        voice_id = CONFIG['elevenlabs'][speaker]['voice_id']
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key
        }
        
        data = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.5
            }
        }
        
        response = requests.post(url, json=data, headers=headers)
        
        if response.status_code == 200:
            with open(output_path, "wb") as audio_file:
                audio_file.write(response.content)
            return output_path
        else:
            raise Exception(f"Error generating audio: {response.status_code}\n{response.text}")