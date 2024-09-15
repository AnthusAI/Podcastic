"""
Module for compiling generated audio files into a single podcast.
"""

from pathlib import Path
import typer
from rich.console import Console
from utils.audio_utils import stitch_audio_files

app = typer.Typer()
console = Console()

@app.command()
def run(input_file: Path, audio_files=None):
    """
    Compile the generated audio files into a single podcast.

    :param input_file: Path to the original input SSML file
    :type input_file: Path
    :param audio_files: List of audio files to compile, defaults to None
    :type audio_files: list, optional
    :raises typer.Exit: If there's an error during compilation
    """
    try:
        # Convert input_file to absolute path
        input_file = Path(input_file).resolve()
        
        # Use absolute path for output directory
        output_dir = Path.cwd() / "generated" / input_file.stem
        
        if audio_files is None:
            # If audio_files is not provided, we need to regenerate this information
            audio_files = []
            for file in sorted(output_dir.glob("*.mp3")):
                audio_files.append(("audio", file))
        
        full_podcast_path = output_dir / f"{input_file.stem}_full_podcast.mp3"
        full_podcast = stitch_audio_files(audio_files, full_podcast_path)
        console.print(f"[bold green]Full podcast compiled:[/bold green] {full_podcast}")
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        raise typer.Exit(code=1)