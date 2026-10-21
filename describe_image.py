import os
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types

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
    "gemini-flash-latest",
]
# Remove any empty entry (in case GEMINI_MODEL is missing)
MODELS = [m for m in MODELS if m]

# Read the image file as raw bytes
with open("samples/chart1.png", "rb") as f:
    image_bytes = f.read()

# Our instruction for the model
prompt = (
    "You are helping a visually impaired student. "
    "Describe this image: first say what type of image it is, "
    "then give a one-sentence summary, then list the key details "
    "such as labels, axes, and values. Say so if anything is unclear."
)


def ask(model_name):
    # Send the image and the instruction to one model and return its text
    response = client.models.generate_content(
        model=model_name,
        contents=[
            types.Part.from_bytes(data=image_bytes, mime_type="image/png"),
            prompt,
        ],
    )
    return response.text


result = None
for name in MODELS:
    # Try each model up to 3 times
    for attempt in range(1, 4):
        try:
            result = ask(name)
            print("Used model:", name)
            break  # success, leave the attempts loop
        except Exception as e:
            # Print a short error, wait a little longer each time, then retry
            print(f"{name}, attempt {attempt} failed: {str(e)[:100]}")
            time.sleep(attempt * 3)
    if result:
        break  # success, stop trying other models

if result:
    print(result)
else:
    print("All models are busy right now. Try again in a few minutes.")