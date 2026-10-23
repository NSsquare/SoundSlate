import os
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from schema import ImageDescription

# Load the key and preferred model from .env
load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Models to try in order. dict.fromkeys removes duplicates but keeps the order.
MODELS = list(dict.fromkeys(m for m in [
    os.getenv("GEMINI_MODEL"),
    "gemini-3.6-flash",
    "gemini-3.5-flash",
    "gemini-3.5-flash-lite",
    "gemini-3.1-flash-lite",
] if m))

PROMPT = (
    "You are helping a visually impaired student understand an image. "
    "Fill in every field of the requested structure. "
    "Never rely on color alone: refer to things by name, label or position, "
    "and mention a color only as an extra hint. "
    "Only report numbers and text you can actually read. "
    "If you must estimate a value from a chart, write 'about' before it "
    "and say in confidence_notes that values are estimates. "
    "For charts with many parts, use key_values for the largest or most "
    "important parts, for example label 'P006, Moraxella catarrhalis', "
    "value 'about 0.93'. "
    "In key_values, include notable exceptions as well as the common pattern. "
    "Never write vague phrases like 'a higher level'; always name exactly what is high or low. "
    "When you identify parts of a chart by matching colors to a legend, and several "
    "colors look similar, say in confidence_notes which identifications may be mistaken. "
    "In trend, describe the general pattern AND any notable exceptions. "
    "Never guess or invent values; if something is unclear, say so in confidence_notes."
)

QA_PROMPT = (
    "You are SoundSlate, an assistant for a visually impaired student. "
    "The student is asking a question about the attached image. "
    "Answer in 1 to 3 short sentences that sound natural when read aloud, "
    "unless the student asks for more detail. "
    "Use only what is actually visible in the image. If you cannot tell, say so plainly. "
    "Never invent numbers or text. If you estimate a value, say 'about'. "
    "Never rely on color alone: refer to things by name, label or position. "
    "If the student asks to be quizzed, ask ONE question about the image and wait; "
    "when they answer, say whether it is right and explain briefly. "
    "Do not use bullet points, asterisks, markdown or emojis, because the answer is read aloud."
)

HINDI_NOTE = (
    " Write simple, clear Hindi using Devanagari script. "
    "Write estimates with the Hindi word for 'about' (लगभग). "
    "Keep numbers, IDs and scientific or technical names exactly as shown in the image."
)

VOICE_NOTE = (
    " The student's question is in the attached audio recording. "
    "First write exactly what the student asked in question_heard, in the language they spoke. "
    "If you cannot hear clear speech, set question_heard to an empty string and "
    "answer to a short polite request to try again. "
    "Otherwise put your answer to the question in answer."
)


class VoiceAnswer(BaseModel):
    # What Gemini returns when the question arrives as audio
    question_heard: str = Field(
        description="The student's question transcribed exactly; empty string if no clear speech"
    )
    answer: str = Field(description="The answer to the question, written to be read aloud")


class AllModelsBusy(Exception):
    # Our own error type, raised when every model fails
    pass


def build_prompt(language):
    # English uses the base prompt; Hindi adds extra instructions
    if language == "en":
        return PROMPT
    return PROMPT + HINDI_NOTE + " Keep image_type as one of the English codes listed."


def history_text(history):
    # Turn earlier questions and answers into plain text for the prompt
    lines = []
    if history:
        lines.append("Earlier in this conversation:")
        for turn in history:
            lines.append("Student: " + turn["q"])
            lines.append("You: " + turn["a"])
    return lines


def build_question_prompt(question, language, history):
    parts = [QA_PROMPT + (HINDI_NOTE if language == "hi" else "")]
    parts += history_text(history)
    parts.append("Student's question: " + question)
    return "\n".join(parts)


def build_voice_prompt(language, history):
    parts = [QA_PROMPT + (HINDI_NOTE if language == "hi" else "") + VOICE_NOTE]
    parts += history_text(history)
    return "\n".join(parts)


def ask(model_name, image_bytes, mime_type, prompt):
    # Send one image to one model and return the parsed description (or None)
    response = client.models.generate_content(
        model=model_name,
        contents=[
            types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
            prompt,
        ],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=ImageDescription,
        ),
    )
    return response.parsed


def describe_image(image_bytes, mime_type, language="en"):
    # Try each model up to 2 times; return (model name, description)
    prompt = build_prompt(language)
    for name in MODELS:
        for attempt in range(1, 3):
            try:
                result = ask(name, image_bytes, mime_type, prompt)
                if result is None:
                    print(f"{name} replied in the wrong format, trying the next model")
                    break
                print("Used model:", name)
                return name, result
            except Exception as e:
                print(f"{name}, attempt {attempt} failed: {str(e)[:100]}")
                time.sleep(attempt * 2)
    raise AllModelsBusy("All models failed")


def answer_question(image_bytes, mime_type, question, language="en", history=None):
    # Answer one typed question about the image; return (model name, answer text)
    prompt = build_question_prompt(question, language, history or [])
    for name in MODELS:
        for attempt in range(1, 3):
            try:
                response = client.models.generate_content(
                    model=name,
                    contents=[
                        types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
                        prompt,
                    ],
                )
                text = (response.text or "").strip()
                if not text:
                    print(f"{name} returned an empty answer, trying the next model")
                    break
                print("Answered with:", name)
                return name, text
            except Exception as e:
                print(f"{name}, attempt {attempt} failed: {str(e)[:100]}")
                time.sleep(attempt * 2)
    raise AllModelsBusy("All models failed")


def answer_voice(image_bytes, mime_type, audio_bytes, audio_mime, language="en", history=None):
    # Answer a spoken question: Gemini hears the audio and sees the image
    prompt = build_voice_prompt(language, history or [])
    for name in MODELS:
        for attempt in range(1, 3):
            try:
                response = client.models.generate_content(
                    model=name,
                    contents=[
                        types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
                        types.Part.from_bytes(data=audio_bytes, mime_type=audio_mime),
                        prompt,
                    ],
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=VoiceAnswer,
                    ),
                )
                result = response.parsed
                if result is None:
                    print(f"{name} replied in the wrong format, trying the next model")
                    break
                print("Voice question answered with:", name)
                return name, result
            except Exception as e:
                print(f"{name}, attempt {attempt} failed: {str(e)[:100]}")
                time.sleep(attempt * 2)
    raise AllModelsBusy("All models failed")