import os
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types
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


class AllModelsBusy(Exception):
    # Our own error type, raised when every model fails
    pass


def ask(model_name, image_bytes, mime_type):
    # Send one image to one model and return the parsed description (or None)
    response = client.models.generate_content(
        model=model_name,
        contents=[
            types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
            PROMPT,
        ],
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=ImageDescription,
        ),
    )
    return response.parsed


def describe_image(image_bytes, mime_type):
    # Try each model up to 2 times; return (model name, description)
    for name in MODELS:
        for attempt in range(1, 3):
            try:
                result = ask(name, image_bytes, mime_type)
                if result is None:
                    print(f"{name} replied in the wrong format, trying the next model")
                    break
                print("Used model:", name)
                return name, result
            except Exception as e:
                print(f"{name}, attempt {attempt} failed: {str(e)[:100]}")
                time.sleep(attempt * 2)
    raise AllModelsBusy("All models failed")