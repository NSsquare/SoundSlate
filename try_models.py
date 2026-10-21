import os
import time
from dotenv import load_dotenv
from google import genai

# Load the key from .env
load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Models to try, in order. The first one that answers wins.
MODELS = [
    "gemini-3.7-flash",
    "gemini-3.6-flash",
    "gemini-3.5-flash",
    "gemini-3.5-flash-lite",
    "gemini-3.1-flash-lite",
    "gemini-flash-latest",
    "gemini-flash-lite-latest",
    "gemini-2.5-flash-lite",
]

for name in MODELS:
    try:
        # Ask this model for a short reply
        response = client.models.generate_content(
            model=name, contents="Say hello in one sentence"
        )
        print("Worked with:", name)
        print(response.text)
        break  # stop at the first model that works
    except Exception as e:
        # Print a short version of the error, then try the next model
        print("Failed with", name, "->", str(e)[:120])
        time.sleep(2)