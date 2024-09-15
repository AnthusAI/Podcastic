import os
from dotenv import load_dotenv
from .openai_tts import OpenAITTS
from .elevenlabs_tts import ElevenLabsTTS

load_dotenv()

def get_tts_service(service_name):
    if service_name == 'openai':
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OpenAI API key not found in .env file")
        return OpenAITTS(api_key=api_key)
    elif service_name == 'elevenlabs':
        api_key = os.getenv('ELEVENLABS_API_KEY')
        if not api_key:
            raise ValueError("ElevenLabs API key not found in .env file")
        return ElevenLabsTTS(api_key=api_key)
    else:
        raise ValueError(f"Unknown TTS service: {service_name}")