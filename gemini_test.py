# Import the os module to access environment variables
import os
# Import load_dotenv from python-dotenv to load variables from the .env file
from dotenv import load_dotenv
# Import the genai module from the google-genai library
from google import genai
# Load environment variables from the local .env file into the environment
load_dotenv()
# Fetch the GEMINI_API_KEY from the loaded environment variables
api_key = os.getenv("GEMINI_API_KEY")
# Initialize the Google GenAI client using the retrieved API key
client = genai.Client(api_key=api_key)
# Send the prompt to the Gemini 2.5 Flash model and receive the response
response = client.models.generate_content(model="gemini-3.7-flash", contents="Say hello in one sentence")
# Print the text response from the model to the console
print(response.text)
