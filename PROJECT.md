# SoundSlate

Accessibility tool for visually impaired students.
Input: a photo of a chart, diagram, or handwritten notes.
Output: a structured JSON description, read aloud in the browser.

## Stack
- Backend: Python FastAPI (main.py)
- AI: Gemini API via the google-genai package
- Frontend: plain HTML/JS with the Web Speech API (later)

## Rules
- Keep code simple, with comments explaining each part.
- Load secrets from .env using python-dotenv. Never hardcode keys.
- Do not modify .env or .gitignore.
- Do not guess model names or library syntax. Check the current official docs.
- Tell me which files you changed and why.