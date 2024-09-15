"""
Module for ElevenLabs Text-to-Speech service.

This module provides a class to interact with ElevenLabs' TTS API.
"""

import yaml
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs
from pathlib import Path
from rich.console import Console

console = Console()

class ElevenLabsTTS:
    """
    A class to handle Text-to-Speech conversion using ElevenLabs' API.
    """

    def __init__(self, api_key):
        """
        Initialize the ElevenLabsTTS instance.

        :param api_key: ElevenLabs API key
        :type api_key: str
        """
        self.client = ElevenLabs(api_key=api_key)
        self.voice_mapping = self.load_voice_mapping()

    def load_voice_mapping(self):
        """
        Load voice mapping from the configuration file.

        :return: Dictionary of voice mappings
        :rtype: dict
        """
        with open("podcastic/config.yaml", "r") as f:
            config = yaml.safe_load(f)
        return {name: data['voice_id'] for name, data in config['elevenlabs'].items()}

    def generate_audio(self, text, output_path, voice):
        """
        Generate audio from text using ElevenLabs' TTS API.

        :param text: Text to convert to speech
        :type text: str
        :param output_path: Path to save the generated audio
        :type output_path: str or Path
        :param voice: Name of the voice to use for TTS
        :type voice: str
        """
        voice_id = self.voice_mapping.get(voice.lower())
        if not voice_id:
            raise ValueError(f"Voice '{voice}' not found in configuration")

        console.print(f"Generating audio for {voice} (voice_id: {voice_id})")

        audio_stream = self.client.text_to_speech.convert(
            voice_id=voice_id,
            text=text,
            voice_settings=VoiceSettings(stability=0.5, similarity_boost=0.5)
        )
        
        output_path = Path(output_path)
        with open(output_path, 'wb') as file_out:
            for chunk in audio_stream:
                if chunk:
                    file_out.write(chunk)
        
        console.print(f"Generated: {output_path.name}")