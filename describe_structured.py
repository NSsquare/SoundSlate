import os
import sys
import time
import mimetypes
from dotenv import load_dotenv
from google import genai
from google.genai import types
from schema import ImageDescription

# Load the key and preferred model from .env
load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Models to try in order. Your .env model goes first.
MODELS = [
    os.getenv("GEMINI_MODEL"),
    "gemini-3.6-flash",
    "gemini-3.5-flash",
    "gemini-3.5-flash-lite",
    "gemini-3.1-flash-lite",
]
MODELS = [m for m in MODELS if m]

# Use the image path typed after the script name, or a default
image_path = sys.argv[1] if len(sys.argv) > 1 else "samples/chart1.png"

# Work out the image type (png, jpeg...) from the file name
mime_type = mimetypes.guess_type(image_path)[0] or "image/png"

# Read the image as raw bytes
with open(image_path, "rb") as f:
    image_bytes = f.read()

prompt = (
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
    "In trend, describe the general pattern AND any notable exceptions. "
    "In key_values, include notable exceptions as well as the common pattern. "
    "Never write vague phrases like 'a higher level'; always name exactly what is high or low. "
    "When you identify parts of a chart by matching colors to a legend, and several "
    "colors look similar, say in confidence_notes which identifications may be mistaken. "
    "Never guess or invent values; if something is unclear, say so in confidence_notes."
)


def ask(model_name):
    # Send the image and prompt, asking for JSON that matches our schema
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
    # response.parsed is already an ImageDescription object
    return response.parsed


result = None
for name in MODELS:
    for attempt in range(1, 4):
        try:
            result = ask(name)
            if result is None:
                # The model answered, but not in the shape we asked for
                print(f"{name} replied in the wrong format, trying the next model")
                break
            print("Used model:", name)
            break
        except Exception as e:
            print(f"{name}, attempt {attempt} failed: {str(e)[:100]}")
            time.sleep(attempt * 3)
    if result:
        break
if result:
    # Show the full structured result
    print(result.model_dump_json(indent=2))
    # Show how it would be spoken: summary first, details later
    print("\n--- What the student would hear first ---")
    print(result.summary)
else:
    print("All models are busy right now. Try again in a few minutes.")