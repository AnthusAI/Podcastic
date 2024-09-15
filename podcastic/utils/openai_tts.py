import yaml
from openai import OpenAI
from pathlib import Path
from rich.console import Console

console = Console()

class OpenAITTS:
    def __init__(self, api_key):
        self.client = OpenAI(api_key=api_key)
        self.voice_mapping = self.load_voice_mapping()

    def load_voice_mapping(self):
        with open("podcastic/config.yaml", "r") as f:
            config = yaml.safe_load(f)
        return {name: data['voice'] for name, data in config['openai'].items()}

    def generate_audio(self, text, output_path, voice):
        mapped_voice = self.voice_mapping.get(voice.lower(), 'alloy')
        console.print(f"Generating audio for {voice} (mapped to {mapped_voice})")
        
        response = self.client.audio.speech.create(
            model="tts-1",
            voice=mapped_voice,
            input=text
        )

        output_path = Path(output_path)
        response.stream_to_file(output_path)
        
        console.print(f"Generated: {output_path.name}")