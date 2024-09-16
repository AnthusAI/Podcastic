# Podcastic

Podcastic is a Python-based tool that generates AI-driven podcast scripts and audio files using OpenAI or Eleven Labs text-to-speech services.

## Setup

* Clone this repository.
* Install the required dependencies:
```
pip install -r requirements.txt
```
* Create a .env file in the root directory with your API keys:
```
ELEVEN_LABS_API_KEY=your_eleven_labs_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
```

## Configuration

Configure voices and other settings in the config.yaml file.

## Usage
Podcastic offers several commands:

### Write a podcast script

Generate a podcast script based on a topic:
```
python podcastic/podcastic.py write --topic path/to/topic.md --output output.ssml
```
This command generates an SSML-inspired script file.

### Generate audio from a script

Convert an SSML script to audio files:
```
python podcastic/podcastic.py generate --input script.ssml --service openai
```
By default, the generate command uses OpenAI for text-to-speech. To use Eleven Labs instead, specify the service:
```
python podcastic/podcastic.py generate --input script.ssml --service elevenlabs
```
This will create individual audio files for each speech segment and compile them into a single podcast file.

### Re-compile the podcast
If you want to re-compile the final podcast without regenerating the individual speech audio files:
```
python podcastic/podcastic.py compile --input script.ssml
```

### SSML-Inspired Script Format
The write command generates scripts in an SSML-inspired format, which is then used by the generate command. Here's an example of this format:
```
<speak voice="ava">
Hello, this is Ava speaking.
</speak>
<break strength="1s"/>
<speak voice="marvin">
And this is Marvin. How are you, Ava?
</speak>
<break strength="1300ms"/>
<speak voice="ava">
I'm doing well, thank you for asking!
</speak>
```
Key features of this format:

* `<speak voice="...">` tags indicate different speakers.
* `<break strength="..."/>` tags add pauses. You can specify the duration in seconds (e.g., "1s") or milliseconds (e.g., "1300ms").
This format allows for precise control over speaker changes and timing in the generated audio.

### Output
Generated files are saved in the `generated/<input_file_name>/` directory.
