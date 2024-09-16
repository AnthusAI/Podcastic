"""
Module for compiling generated audio files into a single podcast.

This module implements the 'compile' command, which takes individual audio files
generated from the SSML script and combines them into a single, cohesive podcast
audio file. It handles the sequencing of audio segments and ensures proper
timing between utterances.
"""

import logging
from pathlib import Path
import typer
from rich.console import Console
from podcastic.utils.audio_utils import stitch_audio_files

app = typer.Typer()
console = Console()

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@app.command()
def run(input: Path = typer.Option(..., "--input", help="Path to the input SSML file")):
    """
    Compile the generated audio files into a single podcast.
    """
    try:
        input_file = Path(input).resolve()
        output_dir = Path.cwd() / "generated" / input_file.stem
        
        logger.debug(f"Input file: {input_file}")
        logger.debug(f"Output directory: {output_dir}")
        logger.debug(f"Output directory exists: {output_dir.exists()}")
        logger.debug(f"Output directory is dir: {output_dir.is_dir()}")
        
        audio_files = list(output_dir.glob("*.mp3"))
        logger.debug(f"Found audio files: {[file.name for file in audio_files]}")
        
        if not audio_files:
            logger.error(f"No audio files found in {output_dir}")
            console.print(f"[bold red]Error:[/bold red] No audio files found in {output_dir}")
            raise typer.Exit(code=1)
        
        # Sort the audio files by name
        audio_files.sort(key=lambda x: x.name)
        
        audio_files_with_type = [("audio", file) for file in audio_files]
        
        full_podcast_path = output_dir / f"{input_file.stem}_full_podcast.mp3"
        full_podcast = stitch_audio_files(audio_files_with_type, full_podcast_path)
        logger.info(f"Full podcast compiled: {full_podcast}")
        console.print(f"[bold green]Full podcast compiled:[/bold green] {full_podcast}")
    except Exception as e:
        logger.exception(f"Error in compile command: {str(e)}")
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        raise typer.Exit(code=1)