import os
from dotenv import load_dotenv
from google import genai

# Load the key from the .env file
load_dotenv()

# Create the client that talks to Gemini
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# Ask Google for every model this key can use and print the names
for m in client.models.list():
    print(m.name)