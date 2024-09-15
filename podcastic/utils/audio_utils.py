"""
Module for audio processing utilities.

This module provides functions for processing SSML content and stitching audio files.
"""

import re
from pathlib import Path
from pydub import AudioSegment
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()

def process_ssml(content: str, service, output_dir: Path):
    """
    Process SSML content and generate audio files.

    :param content: SSML content to process
    :type content: str
    :param service: TTS service to use for audio generation
    :type service: OpenAITTS or ElevenLabsTTS
    :param output_dir: Directory to save generated audio files
    :type output_dir: Path
    :return: List of generated audio files and pauses
    :rtype: list
    """
    pattern = r'<speak\s+voice="(\w+)">(.*?)</speak>|<break\s+strength="([\d.]+)(m?s)"\s*/>'
    matches = re.findall(pattern, content, re.DOTALL)
    
    audio_files = []
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Generating audio files...", total=len(matches))
        for i, match in enumerate(matches):
            if match[0]:  # Speaker content
                speaker, text = match[0], match[1]
                output_filename = f"{i+1:03d}_{speaker}.mp3"
                output_path = output_dir / output_filename
                service.generate_audio(text.strip(), output_path, speaker)
                audio_files.append(("audio", output_path))
                console.print(f"Generated: {output_filename}")
            else:  # Break
                duration = float(match[2])
                if match[3] == "ms":
                    duration /= 1000  # Convert milliseconds to seconds
                audio_files.append(("pause", duration))
                console.print(f"Added pause: {duration} seconds")
            progress.advance(task)
    
    return audio_files

def stitch_audio_files(audio_files, output_path: Path):
    """
    Stitch multiple audio files and pauses into a single audio file.

    :param audio_files: List of audio files and pauses to stitch
    :type audio_files: list
    :param output_path: Path to save the stitched audio file
    :type output_path: Path
    :return: Path of the stitched audio file
    :rtype: Path
    """
    combined = AudioSegment.empty()
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Stitching audio files...", total=len(audio_files))
        for file_type, file_info in audio_files:
            if file_type == "audio":
                segment = AudioSegment.from_mp3(file_info)
                combined += segment
            elif file_type == "pause":
                pause_duration = int(file_info * 1000)  # Convert to milliseconds
                silence = AudioSegment.silent(duration=pause_duration)
                combined += silence
            progress.advance(task)
    
    combined.export(output_path, format="mp3")
    return output_path