"""
Module for compiling generated audio files into a single podcast.

This module implements the 'compile' command, which takes individual audio files
generated from the SSML script and combines them into a single, cohesive podcast
audio file. It handles the sequencing of audio segments and ensures proper
timing between utterances.
"""

from pathlib import Path
import typer
from rich.console import Console
from podcastic.utils.audio_utils import stitch_audio_files

app = typer.Typer()
console = Console()

@app.command()
def run(input: Path = typer.Option(..., "--input", help="Path to the input SSML file")):
    """
    Compile the generated audio files into a single podcast.
    """
    try:
        input_file = Path(input).resolve()
        output_dir = Path.cwd() / "generated" / input_file.stem
        
        audio_files = [
            ("audio", file) for file in sorted(output_dir.glob("*.mp3"))
        ]
        
        if not audio_files:
            console.print(f"[bold red]Error:[/bold red] No audio files found in {output_dir}")
            raise typer.Exit(code=1)
        
        full_podcast_path = output_dir / f"{input_file.stem}_full_podcast.mp3"
        full_podcast = stitch_audio_files(audio_files, full_podcast_path)
        console.print(f"[bold green]Full podcast compiled:[/bold green] {full_podcast}")
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        raise typer.Exit(code=1)