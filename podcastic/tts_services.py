from abc import ABC, abstractmethod
from pathlib import Path
import yaml
from dotenv import load_dotenv

load_dotenv()

with open('podcastic/config.yaml', 'r') as config_file:
    CONFIG = yaml.safe_load(config_file)

class TTSService(ABC):
    @abstractmethod
    def generate_audio(self, text: str, output_filename: str, speaker: str) -> Path:
        pass

from openai_tts import OpenAITTS
from elevenlabs_tts import ElevenLabsTTS