import os
import tempfile
import logging
from pathlib import Path  # Add this import
from typer.testing import CliRunner
from podcastic.podcastic import app
from unittest.mock import patch, MagicMock
import io

runner = CliRunner()

@patch('podcastic.commands.generate.process_ssml')
@patch('podcastic.commands.generate.compile_run')
def test_generate_command(mock_compile_run, mock_process_ssml):
    mock_process_ssml.return_value = ["mocked_audio_file.mp3"]
    mock_compile_run.return_value = None

    with tempfile.NamedTemporaryFile(mode='w', suffix='.ssml', delete=False) as temp_file:
        temp_file.write("<speak><p>Hello World</p></speak>")
        temp_file_path = temp_file.name

    try:
        result = runner.invoke(app, ["generate", "--input", temp_file_path, "--service", "openai"])
        print(f"Generate command output: {result.output}")
        print(f"Generate command exit code: {result.exit_code}")
        assert result.exit_code == 0
        assert "Audio files and pauses generated" in result.output
    finally:
        os.unlink(temp_file_path)

@patch('podcastic.commands.compile.stitch_audio_files')
def test_compile_command(mock_stitch_audio_files):
    mock_stitch_audio_files.return_value = "mocked_full_podcast.mp3"
    
    # Set up logging capture
    log_capture = io.StringIO()
    handler = logging.StreamHandler(log_capture)
    logging.getLogger().addHandler(handler)
    logging.getLogger().setLevel(logging.DEBUG)
    
    # Create a temporary directory to simulate the project root
    with tempfile.TemporaryDirectory() as temp_project_root:
        # Create the expected directory structure
        input_file_name = "test_input"
        generated_dir = Path(temp_project_root) / "generated" / input_file_name
        generated_dir.mkdir(parents=True, exist_ok=True)

        # Create some mock audio files in the correct location
        (generated_dir / "file1.mp3").touch()
        (generated_dir / "file2.mp3").touch()

        # Create a temporary input file
        input_file = Path(temp_project_root) / f"{input_file_name}.ssml"
        input_file.write_text("<speak><p>Hello World</p></speak>")

        try:
            # Patch the cwd() method to return our temp project root
            with patch('pathlib.Path.cwd', return_value=Path(temp_project_root)):
                result = runner.invoke(app, ["compile", "--input", str(input_file)])

            print(f"Compile command output: {result.output}")
            print(f"Compile command exit code: {result.exit_code}")
            print(f"Captured logs:\n{log_capture.getvalue()}")
            assert result.exit_code == 0
            assert "Full podcast compiled:" in result.output
        finally:
            logging.getLogger().removeHandler(handler)

@patch('podcastic.commands.write.generate_outline')
@patch('podcastic.commands.write.generate_utterance')
def test_write_command(mock_generate_utterance, mock_generate_outline):
    mock_generate_outline.return_value = "1. Introduction\n2. Main Topic\n3. Conclusion"
    mock_generate_utterance.return_value = "This is a mocked utterance."

    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as temp_file:
        temp_file.write("Sample topic content")
        temp_file_path = temp_file.name

    try:
        output_file = tempfile.NamedTemporaryFile(mode='w', suffix='.ssml', delete=False).name
        result = runner.invoke(app, ["write", "--topic", temp_file_path, "--output", output_file])
        print(f"Write command output: {result.output}")
        print(f"Write command exit code: {result.exit_code}")
        assert result.exit_code == 0
        assert "Generated Podcast Outline:" in result.output
        assert "Generated Script:" in result.output
        assert "<speak voice=\"Ava\">This is a mocked utterance.</speak>" in result.output
        assert "<speak voice=\"Marvin\">This is a mocked utterance.</speak>" in result.output
    finally:
        os.unlink(temp_file_path)
        if os.path.exists(output_file):
            os.unlink(output_file)