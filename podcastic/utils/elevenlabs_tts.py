"""
Module for ElevenLabs Text-to-Speech service.

This module provides a class to interact with ElevenLabs' TTS API.
"""

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
        self.api_key = api_key
        self.client = ElevenLabs(api_key=self.api_key)

    def generate_audio(self, text, output_path, voice_id):
        """
        Generate audio from text using ElevenLabs' TTS API.

        :param text: Text to convert to speech
        :type text: str
        :param output_path: Path to save the generated audio
        :type output_path: str or Path
        :param voice_id: ID of the voice to use for TTS
        :type voice_id: str
        """
        audio = self.client.text_to_speech.convert(
            voice_id=voice_id,
            text=text,
        )
        with open(output_path, 'wb') as file_out:
            file_out.write(audio)