from pathlib import Path
import typer
from utils.tts_services import get_tts_service as get_tts_service_util
import re
from pydub import AudioSegment
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
import logging

console = Console()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Suppress debug logs from external libraries
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("openai").setLevel(logging.WARNING)

app = typer.Typer()

def get_tts_service(service: str):
    return get_tts_service_util(service)

def process_ssml(content: str, service, output_dir: Path):
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

@app.command()
def generate(
    input_file: Path,
    tts_service: str = typer.Option("openai", help="TTS service to use (elevenlabs or openai)")
):
    """
    Generate audio files from an SSML file using the specified TTS service.
    """
    if not input_file.exists() or input_file.suffix != '.ssml':
        console.print(f"[bold red]Error:[/bold red] File {input_file} not found or not an SSML file.")
        raise typer.Exit(code=1)
    
    output_dir = Path("generated") / input_file.stem
    output_dir.mkdir(parents=True, exist_ok=True)
    
    with open(input_file, "r") as file:
        content = file.read()
    
    try:
        service = get_tts_service(tts_service)
        console.print(f"[bold green]Using {tts_service} TTS service[/bold green]")
        audio_files = process_ssml(content, service, output_dir)
        console.print(f"[bold green]Audio files and pauses generated in:[/bold green] {output_dir}")
        
        # Automatically run the compile command
        compile(input_file, audio_files)
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        raise typer.Exit(code=1)

@app.command()
def compile(input_file: Path, audio_files=None):
    """
    Compile the generated audio files into a single podcast.
    """
    try:
        output_dir = Path("generated") / input_file.stem
        
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

if __name__ == "__main__":
    logger.debug("Starting Podcastic CLI")
    app()