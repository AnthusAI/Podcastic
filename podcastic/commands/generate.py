"""
Module for generating audio files from SSML input using specified TTS service.
"""

from pathlib import Path
import typer
from rich.console import Console
from podcastic.utils.tts_services import get_tts_service
from podcastic.utils.audio_utils import process_ssml
from podcastic.commands.compile import run as compile_run
import logging

app = typer.Typer()
console = Console()

# Set up logging
logging.basicConfig(level=logging.DEBUG, filename='generate_reasoning.log', filemode='w',
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@app.callback()
def run(
    input: Path = typer.Option(..., "--input", help="Path to the input SSML file"),
    service: str = typer.Option("openai", help="TTS service to use (elevenlabs or openai)")
):
    """Generate audio files from an SSML file using the specified TTS service."""
    logger.info(f"Starting generation process with input file: {input} and service: {service}")
    
    input_file = Path(input).resolve()

    if not input_file.exists() or input_file.suffix != '.ssml':
        error_msg = f"File {input_file} not found or not an SSML file."
        logger.error(error_msg)
        console.print(f"[bold red]Error:[/bold red] {error_msg}")
        raise typer.Exit(code=1)
    
    output_dir = Path.cwd() / "generated" / input_file.stem
    output_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"Created output directory: {output_dir}")
    
    with open(input_file, "r") as file:
        content = file.read()
    logger.debug(f"Read content from input file: {input_file}")
    
    try:
        tts_service = get_tts_service(service)
        logger.info(f"Using {service} TTS service")
        console.print(f"[bold green]Using {service} TTS service[/bold green]")
        
        logger.debug("Starting SSML processing")
        audio_files = process_ssml(content, tts_service, output_dir)
        logger.info(f"Audio files and pauses generated in: {output_dir}")
        console.print(f"[bold green]Audio files and pauses generated in:[/bold green] {output_dir}")
        
        logger.debug("Starting compilation process")
        compile_run(input=input_file)
        logger.info("Compilation process completed")
    except Exception as e:
        error_msg = f"Error during generation process: {str(e)}"
        logger.error(error_msg, exc_info=True)
        console.print(f"[bold red]Error:[/bold red] {error_msg}")
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app()