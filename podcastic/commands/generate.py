import logging
from pathlib import Path
import typer
from rich.console import Console
from utils.tts_services import get_tts_service
from utils.audio_utils import process_ssml
from .compile import compile

console = Console()

def generate(
    input_file: Path,
    tts_service: str = typer.Option("openai", help="TTS service to use (elevenlabs or openai)")
):
    if not input_file.exists() or input_file.suffix != '.ssml':
        console.print(f"[bold red]Error:[/bold red] File {input_file} not found or not an SSML file.")
        raise typer.Exit(code=1)
    
    output_dir = Path("generated") / input_file.stem
    output_dir.mkdir(parents=True, exist_ok=True)
    
    with open(input_file, "r") as file:
        content = file.read()
    
    try:
        service = get_tts_service(tts_service)
        console.print(f"Using {tts_service} TTS service")

        # Call process_ssml without a progress bar
        audio_files = process_ssml(content, service, output_dir)
        
        console.print(f"Audio files and pauses generated in: {output_dir}")
        
        compile(input_file, audio_files)
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        raise typer.Exit(code=1)