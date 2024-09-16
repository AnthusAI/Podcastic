"""
Module for generating podcast scripts using available knowledge bases.

This module implements a command to generate podcast scripts in a custom markup language
based loosely on SSML, using logic to create an outline and orchestrate two different
tools for writing the script.
"""

import typer
from pathlib import Path
import yaml
from rich.console import Console
from langchain_core.runnables import RunnableSequence
import re
import logging
import random
import difflib

# Set up logging
logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Add a StreamHandler to output logs to the console
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
logger.addHandler(console_handler)

app = typer.Typer()
console = Console()

@app.command()
def run(
    topic: Path = typer.Option(..., help="Path to the topic markdown file"),
    output: Path = typer.Option("output.ssml", help="Path to save the podcast script")
):
    logger.debug(f"Starting script generation for topic: {topic}")
    topic_content = topic.read_text()
    logger.debug("Topic content loaded")
    logger.debug(f"Topic content:\n{topic_content}")

    with open('config.yaml', 'r') as config_file:
        config = yaml.safe_load(config_file)
    logger.debug("Configuration loaded")
    logger.debug(f"Configuration:\n{config}")

    editorial_guidelines = config.get('editorial_guidelines', '')
    editorial_outline_model = config.get('editorial_outline_model', 'gpt-4o-mini')

    logger.debug("Generating outline")
    outline = generate_outline(topic_content, editorial_guidelines, editorial_outline_model)
    console.print("[bold]Generated Podcast Outline:[/bold]")
    console.print(outline)

    sections = split_outline_into_sections(outline)
    logger.debug(f"Number of sections: {len(sections)}")
    for i, section in enumerate(sections, 1):
        logger.debug(f"Section {i}:\n{section}")

    if len(sections) == 0:
        logger.error("No sections found in the outline. Script generation cannot proceed.")
        return

    total_utterances = len(sections) * 2  # Two utterances per section
    logger.debug(f"Total expected utterances: {total_utterances}")

    script = ""
    global_conversation_history = ""
    name_usage_count = {"ava": 0, "marvin": 0}
    utterance_count = {"ava": 0, "marvin": 0}

    for i, section in enumerate(sections, 1):
        logger.debug(f"Processing section {i}/{len(sections)}")
        logger.debug(f"Section content:\n{section}")

        utterances_per_section = 4  # Adjust this value as needed
        for utterance_index in range(utterances_per_section):
            speaker = 'ava' if utterance_index % 2 == 0 else 'marvin'
            other_speaker = 'marvin' if speaker == 'ava' else 'ava'
            
            is_last_section = i == len(sections)
            is_last_utterance = is_last_section and utterance_index == utterances_per_section - 1

            logger.debug(f"Generating utterance for {speaker}")
            utterance = generate_utterance(
                speaker, 
                other_speaker, 
                global_conversation_history,
                section, 
                config, 
                name_usage_count,
                utterance_count,
                total_utterances,
                is_last_utterance,
                topic_content,
                retry_count=0
            )
            logger.debug(f"Generated utterance for {speaker}: {utterance}")

            # Update global conversation history
            global_conversation_history += f"{speaker.capitalize()}: {utterance}\n\n"

            # Append utterance in SSML format
            script += f'<speak voice="{speaker.capitalize()}">{utterance}</speak>\n\n'
            logger.debug(f"Current script length: {len(script)} characters")

            # Generate pause if it's not the last utterance
            if not is_last_utterance:
                next_speaker = 'marvin' if speaker == 'ava' else 'ava'
                next_section = section if utterance_index < utterances_per_section - 1 else (sections[i] if i < len(sections) else "")
                pause = generate_pause(utterance, next_speaker, next_section)
                script += pause + "\n\n"
                logger.debug(f"Added pause: {pause}")

            utterance_count[speaker.lower()] += 1
            logger.debug(f"Current utterance count: {utterance_count}")

    if not script:
        logger.error("No script content generated.")
    else:
        logger.debug(f"Saving script to {output}")
        output.write_text(script)
        logger.debug("Script generation complete")
        logger.debug(f"Final script:\n{script}")

    console.print("\n[bold]Generated Script:[/bold]")
    console.print(script)
    logger.debug("Script output to console complete")

def generate_outline(
    topic_content: str,
    editorial_guidelines: str,
    editorial_outline_model: str
) -> str:
    logger.debug("Starting outline generation")
    from langchain_openai import ChatOpenAI
    from langchain.prompts import PromptTemplate
    from langchain_core.runnables import RunnableSequence

    chat_model = ChatOpenAI(temperature=0, model=editorial_outline_model)
    prompt_template = PromptTemplate(
        template=(
            "Given the following topic information:\n{topic_content}\n\n"
            "And the editorial guidelines:\n{editorial_guidelines}\n\n"
            "Generate a detailed outline for a podcast episode, with the individual sub-topics as separate items in the list. "
            "Please format the outline as follows:\n"
            "1. Main Topic 1\n"
            "   - Subtopic 1a\n"
            "   - Subtopic 1b\n"
            "2. Main Topic 2\n"
            "   - Subtopic 2a\n"
            "   - Subtopic 2b\n"
            "... and so on.\n"
            "Ensure each main topic is numbered and on its own line."
        ),
        input_variables=["topic_content", "editorial_guidelines"]
    )

    outline_chain = RunnableSequence(
        prompt_template | chat_model
    )

    result = outline_chain.invoke({
        "topic_content": topic_content,
        "editorial_guidelines": editorial_guidelines
    })

    return result.content

def generate_utterance(
    speaker: str, 
    other_speaker: str, 
    full_conversation_history: str, 
    section: str, 
    config: dict,
    name_usage_count: dict,
    utterance_count: dict,
    total_utterances: int,
    is_final_utterance: bool,
    topic_content: str,
    retry_count: int = 0
) -> str:
    logger.debug(f"Generating utterance for {speaker}")
    from langchain_openai import ChatOpenAI
    from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
    from langchain_community.callbacks.manager import get_openai_callback

    editorial_guidelines = config.get('editorial_guidelines', '')
    utterance_generation_model = config.get('utterance_generation_model', 'gpt-4o-mini')

    logger.debug(f"Using model: {utterance_generation_model}")

    system_prompt = AVA_SYSTEM_PROMPT if speaker.lower() == 'ava' else MARVIN_SYSTEM_PROMPT

    chat_model = ChatOpenAI(model=utterance_generation_model, temperature=0)

    should_use_name = (
        (speaker.lower() == 'ava' and utterance_count['ava'] == 1) or
        (speaker.lower() == 'marvin' and utterance_count['marvin'] == 0)
    )

    if is_final_utterance:
        if speaker.lower() == 'ava':
            name_usage_instruction = "This is your final response. Thank the listeners and conclude the podcast."
        else:
            name_usage_instruction = "This is your final response. Thank the listeners and say a brief, positive goodbye."
    elif should_use_name:
        name_usage_instruction = f"IMPORTANT: Use {other_speaker}'s name in your response. This is crucial for the conversation flow."
    else:
        name_usage_instruction = f"IMPORTANT: Do not use {other_speaker}'s name in your response."

    logger.debug(f"Name usage instruction: {name_usage_instruction}")

    if speaker.lower() == 'ava' and utterance_count['ava'] > 1 and not is_final_utterance:
        extended_response_instruction = (
            "As Ava, you may provide a more detailed response if you have additional relevant information. "
            "Your response can be up to twice as long as usual, but only if it adds significant value to the discussion. "
            "If you don't have much to add, keep your response brief as before."
        )
    else:
        extended_response_instruction = (
            "Keep your response brief, ideally one or two sentences at most."
        )

    prompt = ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(system_prompt),
        HumanMessagePromptTemplate.from_template(
            "Overall Podcast Topic:\n{topic_content}\n\n"
            "Full Conversation History:\n{full_conversation_history}\n\n"
            "Current Podcast Section:\n{section}\n\n"
            "Editorial Guidelines:\n{editorial_guidelines}\n\n"
            "{name_usage_instruction}\n\n"
            "{speaker}, please provide your next response.\n"
            "Ensure your response maintains continuity with the recent conversation and relates to the overall podcast topic.\n"
            "Do not include your name at the beginning of your response.\n"
            "Provide your response as plain text without any markdown or formatting.\n"
            "{extended_response_instruction}\n"
            "Advance the conversation with new information or a unique perspective related to the current section.\n"
            "If you're Marvin, ask a question that hasn't been asked before or provide a unique insight.\n"
            "If you're Ava, provide a concise explanation or introduce a new aspect of the topic that hasn't been discussed.\n"
            "Be creative and try to approach the topic from a different angle than what has been discussed so far.\n"
            "If you're struggling to add new information, try to summarize or conclude the current subtopic and transition to the next one."
        )
    ])

    formatted_prompt = prompt.format_prompt(
        topic_content=topic_content,  # Add this line
        full_conversation_history=full_conversation_history,
        section=section,
        editorial_guidelines=editorial_guidelines,
        name_usage_instruction=name_usage_instruction,
        extended_response_instruction=extended_response_instruction,
        speaker=speaker.capitalize(),
        other_speaker=other_speaker.capitalize(),
    ).to_messages()

    logger.debug(f"Formatted prompt for {speaker}:\n{formatted_prompt}")

    logger.debug(f"Invoking ChatOpenAI for {speaker}")
    with get_openai_callback() as cb:
        response = chat_model.invoke(formatted_prompt)
        logger.debug(f"Received response for {speaker}")
        logger.debug(f"OpenAI API usage: {cb}")

    utterance = response.content.strip()
    logger.debug(f"Generated utterance: {utterance}")

    # Log reasoning trace
    logger.debug(f"Reasoning trace for {speaker}:")
    logger.debug(f"Input context: {section}")
    logger.debug(f"Name usage instruction: {name_usage_instruction}")
    logger.debug(f"Is final utterance: {is_final_utterance}")
    logger.debug(f"Current utterance count: {utterance_count}")
    logger.debug(f"Total utterances: {total_utterances}")

    # Update name usage count and utterance count
    if other_speaker.lower() in utterance.lower():
        name_usage_count[other_speaker.lower()] += 1
    utterance_count[speaker.lower()] += 1

    logger.debug(f"Updated name usage count: {name_usage_count}")
    logger.debug(f"Updated utterance count: {utterance_count}")

    # Check for repetition
    if is_too_similar(utterance, full_conversation_history):
        logger.warning("Detected similarity. Attempting to regenerate utterance.")
        if retry_count < 3:  # Limit the number of retries
            return generate_utterance(
                speaker, other_speaker, full_conversation_history, section, config,
                name_usage_count, utterance_count, total_utterances, is_final_utterance, topic_content,
                retry_count + 1
            )
        else:
            logger.warning("Max retries reached. Generating a transition to the next topic.")
            return generate_transition(speaker, section)

    return utterance

def is_too_similar(new_utterance: str, conversation_history: str, threshold: float = 0.8) -> bool:
    for utterance in conversation_history.split('\n'):
        similarity = difflib.SequenceMatcher(None, new_utterance.lower(), utterance.lower()).ratio()
        if similarity > threshold:
            return True
    return False

def generate_transition(speaker: str, section: str) -> str:
    transitions = [
        f"Let's move on to another aspect of this topic.",
        f"Shifting gears a bit, what about {extract_next_subtopic(section)}?",
        f"That's an interesting point. Now, let's consider another angle.",
        f"Building on that idea, we should also discuss {extract_next_subtopic(section)}.",
        f"That's a good summary of what we've covered. Shall we explore the next part of our topic?",
    ]
    return random.choice(transitions)

def extract_next_subtopic(section: str) -> str:
    lines = section.split('\n')
    for line in lines[1:]:  # Skip the first line (main topic)
        if line.strip().startswith('-'):
            return line.strip()[1:].strip()
    return "the next point"

def split_outline_into_sections(outline: str) -> list:
    logger.debug("Splitting outline into sections")
    logger.debug(f"Outline content:\n{outline}")
    
    # Split the outline into lines
    lines = outline.split('\n')
    sections = []
    current_section = ""
    
    for line in lines:
        # Check if the line starts with a number followed by a dot
        if re.match(r'^\d+\.', line.strip()):
            if current_section:
                sections.append(current_section.strip())
            current_section = line
        else:
            current_section += "\n" + line
    
    # Add the last section
    if current_section:
        sections.append(current_section.strip())
    
    logger.debug(f"Found {len(sections)} sections")
    
    if len(sections) == 0:
        logger.warning("No sections found in the outline.")
    else:
        for i, section in enumerate(sections, 1):
            logger.debug(f"Section {i}:\n{section}\n")
    
    return sections

# Define system prompts for Ava and Marvin
AVA_SYSTEM_PROMPT = """
You are Ava, an experienced, confident, and knowledgeable AI solutions architect.
- You are patient, empathetic, kind, non-judgmental, non-patronizing, and non-condescending.
- You guide the conversation and are aware of the plan.
- You try to explain things in a way that is easy to understand and not technical.
- When instructed, you must use Marvin's name in your second response to establish rapport.
- Keep your responses brief, ideally one or two sentences at most.
- Pause frequently to allow Marvin to respond or ask questions.
"""

MARVIN_SYSTEM_PROMPT = """
You are Marvin, a business user who is not tech-savvy.
- You are the 'straight man' who asks questions to push Ava to explain things clearly.
- You insert humor when possible and are prone to dad jokes.
- You are not aware of the plan and are just along for the ride.
- Keep your responses brief, ideally one or two sentences at most.
- Ask short, focused questions to encourage Ava to explain further.
"""

def generate_pause(current_utterance, next_speaker, next_section):
    # Analyze the relationship between utterances
    engagement_level = analyze_engagement(current_utterance, next_speaker, next_section)
    topic_change = detect_topic_change(current_utterance, next_section)
    is_answering_question = is_question(current_utterance)

    logger.debug(f"Generating pause for {next_speaker}")
    logger.debug(f"Engagement level: {engagement_level}, Topic change: {topic_change}, Answering question: {is_answering_question}")

    if is_answering_question:
        return f'<break time="{random.uniform(0.3, 0.6):.1f}s"/>'
    elif topic_change:
        return f'<break time="{random.uniform(1.8, 2.5):.1f}s"/>'
    elif engagement_level == 'high':
        return f'<break time="{random.uniform(0.5, 0.8):.1f}s"/>'
    elif engagement_level == 'low':
        return f'<break time="{random.uniform(1.5, 2.0):.1f}s"/>'
    else:  # normal engagement
        return f'<break time="{random.uniform(0.9, 1.5):.1f}s"/>'

def is_question(utterance):
    # Simple check for question marks at the end of the utterance
    return bool(re.search(r'\?\s*$', utterance))

def analyze_engagement(current_utterance, next_speaker, next_section):
    # Implement logic to determine engagement level
    # This could involve analyzing sentiment, question marks, exclamation points, etc.
    # For now, let's return a random engagement level
    return random.choice(['high', 'normal', 'low'])

def detect_topic_change(current_utterance, next_section):
    # Implement logic to detect if there's a significant topic change
    # This could involve comparing key words or using more advanced NLP techniques
    # For now, let's return a random boolean
    return random.choice([True, False])