import re
import logging
from pathlib import Path
from rich.console import Console

logger = logging.getLogger(__name__)
console = Console()

def extract_text_from_ssml(ssml_content):
    text_segments = re.findall(r'<voice[^>]*>(.*?)</voice>', ssml_content, re.DOTALL)
    return [re.sub(r'<[^>]+>', '', segment).strip() for segment in text_segments]

def process_ssml(ssml_content, tts_service, output_dir):
    audio_files = []
    ssml_parts = re.findall(r'(<voice[^>]*>.*?</voice>|<break[^>]*/>)', ssml_content, re.DOTALL)

    for i, part in enumerate(ssml_parts):
        if part.startswith('<voice'):
            voice_name_match = re.search(r'name="([^"]+)"', part)
            voice_name = voice_name_match.group(1) if voice_name_match else 'default'
            text_match = re.search(r'<voice[^>]*>(.*?)</voice>', part, re.DOTALL)
            text = text_match.group(1).strip() if text_match else ''

            # Log the voice name and text
            console.print(f"\n[bold cyan]Processing segment {i+1}[/bold cyan]")
            console.print(f"Voice: [bold]{voice_name}[/bold]")
            console.print(f"Text: {text}")

            file_name = f"{i:03d}_{voice_name.lower()}.mp3"
            output_path = output_dir / file_name
            tts_service.generate_audio(text, output_path, voice_name)
            audio_files.append(output_path)
            console.print(f"Generated: {file_name}")
        elif part.startswith('<break'):
            time_match = re.search(r'time="([^"]+)"', part)
            time_str = time_match.group(1) if time_match else '1s'
            pause_duration = parse_time(time_str)
            audio_files.append(pause_duration)
            console.print(f"Added pause: {pause_duration} seconds", style="blue")

    return audio_files