"""
Module for generating audio files from SSML input using specified TTS service.
"""

from pathlib import Path
import typer
from rich.console import Console
from utils.tts_services import get_tts_service
from utils.audio_utils import process_ssml, stitch_audio_files
from .compile import run as compile_run

app = typer.Typer()
console = Console()

@app.command()
def run(
    input_file: Path = typer.Argument(..., help="Path to the input SSML file"),
    tts_service: str = typer.Option("openai", help="TTS service to use (elevenlabs or openai)")
):
    """
    Generate audio files from an SSML file using the specified TTS service.

    :param input_file: Path to the input SSML file
    :type input_file: Path
    :param tts_service: TTS service to use (elevenlabs or openai)
    :type tts_service: str
    :raises typer.Exit: If the input file is not found or is not an SSML file
    """
    # Convert input_file to absolute path
    input_file = Path(input_file).resolve()

    if not input_file.exists() or input_file.suffix != '.ssml':
        console.print(f"[bold red]Error:[/bold red] File {input_file} not found or not an SSML file.")
        raise typer.Exit(code=1)
    
    # Use absolute path for output directory
    output_dir = Path.cwd() / "generated" / input_file.stem
    output_dir.mkdir(parents=True, exist_ok=True)
    
    with open(input_file, "r") as file:
        content = file.read()
    
    try:
        service = get_tts_service(tts_service)
        console.print(f"[bold green]Using {tts_service} TTS service[/bold green]")
        audio_files = process_ssml(content, service, output_dir)
        console.print(f"[bold green]Audio files and pauses generated in:[/bold green] {output_dir}")
        
        # Automatically run the compile command
        compile_run(input_file, audio_files)
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app()