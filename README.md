# Anthus Podcaster

Anthus Podcaster is a Python-based tool that generates audio podcasts from SSML (Speech Synthesis Markup Language) files using either OpenAI or Eleven Labs text-to-speech services.

## Setup

1. Clone this repository.
2. Install the required dependencies:
   ```
   pip install -r podcastic/requirements.txt
   ```
3. Create a `.env` file in the `podcastic` directory with your API keys:
   ```
   ELEVEN_LABS_API_KEY=your_eleven_labs_api_key_here
   OPENAI_API_KEY=your_openai_api_key_here
   ```

## SSML File Format

The input file should be in SSML format. Here's an example:

```
xml
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

- Use `<speak voice="...">` tags to indicate different speakers.
- Use `<break strength="..."/>` tags to add pauses. You can specify the duration in seconds (e.g., "1s") or milliseconds (e.g., "1300ms").

## Configuration

You can configure the voices used for each speaker in the `podcastic/config.yaml` file.

## Output

The generated audio files and the final podcast will be saved in the `generated/<input_file_name>/` directory.

## Usage

### Generating a podcast

To generate a podcast using OpenAI:

```
python podcastic/podcastic.py generate test.ssml --tts-service openai
```

To generate a podcast using Eleven Labs:

```
python podcastic/podcastic.py generate test.ssml --tts-service elevenlabs
```

This will create individual audio files for each speech segment and compile them into a single podcast file.

### Re-compiling the podcast

If you want to re-compile the final podcast without regenerating the individual speech audio files:

```
python podcastic/podcastic.py compile test.ssml
```# Podcastic
