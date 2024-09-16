"""
Module for OpenAI Text-to-Speech service.

This module provides a class to interact with OpenAI's TTS API.
"""

import yaml
from openai import OpenAI
from pathlib import Path
from rich.console import Console

console = Console()

class OpenAITTS:
    """
    A class to handle Text-to-Speech conversion using OpenAI's API.
    """

    def __init__(self, api_key):
        """
        Initialize the OpenAITTS instance.

        :param api_key: OpenAI API key
        :type api_key: str
        """
        self.client = OpenAI(api_key=api_key)
        self.voice_mapping = self.load_voice_mapping()

    def load_voice_mapping(self):
        """
        Load voice mapping from the configuration file.

        :return: Dictionary of voice mappings
        :rtype: dict
        """
        with open("config.yaml", "r") as f:
            config = yaml.safe_load(f)
        return {name: data['voice'] for name, data in config['openai'].items()}

    def generate_audio(self, text, output_path, voice):
        """
        Generate audio from text using OpenAI's TTS API.

        :param text: Text to convert to speech
        :type text: str
        :param output_path: Path to save the generated audio
        :type output_path: str or Path
        :param voice: Voice to use for TTS
        :type voice: str
        """
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