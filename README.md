# SoundSlate

**Hear any chart, diagram or handwritten note, then ask questions about it.**

SoundSlate is a web app for visually impaired students. A student uploads or photographs a chart, diagram or handwritten page, and SoundSlate describes it as structured, spoken information: a short summary first, then more detail on request. The student can interrupt the reading at any point and ask a question about the image by typing or by voice.

Built for the CodeTitans hackathon on Unstop.

**Team:** NSsquare (Navya Shukla , Nandani Kumari)
**Demo video:** under progress

---

## The problem

Screen readers handle text well, but a lot of learning material is visual: a bar chart in a textbook, a circuit diagram on a slide, a classmate's handwritten notes. For a visually impaired student these are often a blank gap, and someone has to describe them by hand, which rarely happens.

A generic image caption such as "a graph with blue bars" does not help a student who needs the actual numbers and the trend. SoundSlate focuses on educational content and returns a description that follows the logic of the image: what it is, what it shows, the key takeaway, then the details, with an honest note about anything uncertain.

---

## Features

**Describing images**
- Upload PNG, JPEG or WebP images (up to 8 MB), or take a photo with a live camera view (Take photo, Switch camera, optional spoken 3-2-1 countdown).
- Structured description: image type, one-sentence summary, ordered details, key values with labels, the main trend, and confidence notes about anything blurry or uncertain.
- English and Hindi (Devanagari) output. Numbers, IDs and technical names are kept as they appear in the image.
- A rough photo check warns when an image looks very dark, washed out or possibly blurry, so the student can retake it.

**Listening**
- The summary is read aloud first. Repeat, More detail (one extra detail per press), Read everything and Stop controls.
- Adjustable speaking speed. Hindi speech depends on a Hindi voice being installed on the device.
- Hear the chart as sound: when the key values contain at least three numbers, they can be played as tones (low pitch is a small value, high pitch a large value). This covers only the key values in the order listed, not the whole image.

**Asking questions**
- Type a question or use suggested questions (Explain simply, Biggest and smallest, Describe the layout, What might be wrong, Quiz me).
- Voice questions with a clear status bar showing whether the microphone is on, whether a voice is being heard, and what was understood. A level meter and a live transcript are shown while speaking.
- Interrupt and ask: pressing Alt+Q stops the reading, listens for a question and reads the answer. Continue reading resumes from the sentence where the reading stopped.
- Follow-up questions remember the last few questions and answers.
- Two voice recognition methods: the browser's speech recognizer (Chrome or Edge, live text) and a backup that records the audio and lets Gemini listen to it. Automatic mode tries the browser first and switches if it fails. A Test microphone button in the settings shows what the browser heard.
- The question is read back ("I heard: ...") before the answer, so a misheard question is easy to notice. This can be turned off.

**Accessibility and usability**
- Multiple colour themes, including bright and high-contrast options, a soft low-glare theme, text size buttons and an easy-read text style. Settings are remembered between visits.
- Keyboard shortcuts and a skip link, visible focus outlines, buttons that always have text labels, live regions for status messages, and focus moved to the results when they arrive.
- Copy the description, or save study notes (description plus your questions and answers) as a text file.

**Reliability**
- Server-side checks on file type, size and emptiness before any AI call.
- Automatic retries and fallback across several Gemini models when one is busy, with a friendly error message if all of them fail.

---

## How it works

```
Browser (index.html)
   |  image (+ language, + question or audio)
   v
FastAPI server (main.py)  -- validates the upload
   |
   v
describer.py  -- builds the prompt, tries models in order, retries on failure
   |
   v
Google Gemini API  -- returns JSON that must match the schema in schema.py
   |
   v
Browser shows the result and reads it aloud with the Web Speech API
```

The response format is defined with Pydantic in `schema.py`, and Gemini is asked to return JSON in exactly that shape:

```json
{
  "image_type": "bar_chart",
  "summary": "One short sentence saying what the image shows",
  "details": ["Important details in a sensible reading order"],
  "key_values": [{"label": "P006, Moraxella catarrhalis", "value": "about 0.93"}],
  "trend": "The main pattern and any notable exceptions",
  "confidence_notes": "Anything blurry, cut off or uncertain"
}
```

---

## Tech stack

| Layer | Tools |
|---|---|
| Backend | Python, FastAPI, Uvicorn, Pydantic |
| AI | Google Gemini API (`google-genai` package), Flash and Flash-Lite models |
| Frontend | Plain HTML, CSS and JavaScript (no framework) |
| Speech output | Browser Web Speech API (`speechSynthesis`) |
| Speech input | Browser Web Speech API (`SpeechRecognition`) with a Gemini audio backup |
| Camera and audio | `getUserMedia`, `MediaRecorder`, Web Audio API |

---

## Project structure

```
SoundSlate/
├── main.py              FastAPI app: routes, validation, error handling
├── describer.py         Prompts, Gemini calls, model fallback and retries
├── schema.py            Pydantic model for the structured description
├── index.html           The whole student-facing page (HTML, CSS, JS)
├── requirements.txt     Python dependencies
├── PROJECT.md           Short project context file used with the coding agent
├── results.md           Test log: what was checked, what was right and wrong
├── samples/             Test images
├── describe_structured.py, describe_image.py,
│   try_models.py, list_models.py, gemini_test.py
│                        Command-line scripts used during development
└── .env                 Your private settings (never committed, see below)
```

---

## Getting started

### Requirements
- Python 3.10 or newer
- Git
- A free Gemini API key from [Google AI Studio](https://aistudio.google.com)
- Chrome or Edge recommended (best support for voice input and speech)

### 1. Clone the repository
```
git clone https://github.com/NSsquare/SoundSlate.git
cd SoundSlate
```
Keep the folder outside cloud-synced folders such as OneDrive, because the virtual environment contains thousands of small files.

### 2. Create and activate a virtual environment

Windows (PowerShell):
```
python -m venv venv
venv\Scripts\Activate.ps1
```
If PowerShell blocks the script, run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once and try again.

macOS or Linux:
```
python3 -m venv venv
source venv/bin/activate
```
Your prompt should now start with `(venv)`.

### 3. Install the dependencies
```
pip install -r requirements.txt
```

### 4. Add your settings
The `.env` file holds your private key and is listed in `.gitignore`, so it is never uploaded to GitHub. Every person running the project needs their own `.env`.

Create a file named `.env` in the project folder with these two lines (no spaces around `=`, no quotes):
```
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-3.6-flash
```
Gemini model names change often. To see which models your key can use, run `python list_models.py` and pick a Flash model from the list.

### 5. Run the server
```
uvicorn main:app --reload
```
Wait for `Uvicorn running on http://127.0.0.1:8000`, then open:

- **http://127.0.0.1:8000/app** for the SoundSlate page
- **http://127.0.0.1:8000/docs** for the automatic API documentation, where you can also test the endpoints

---

## Using the app

1. Add an image: choose a file, or press **Open camera** and **Take photo**.
2. Choose the language, then press **Describe image**. It can take up to a minute when the models are busy.
3. Listen to the summary, then use **More detail**, **Read everything** or **Hear the chart as sound**.
4. Ask a question by typing it, using a suggested question, or pressing **Ask by voice** (or Alt+Q) and speaking. Watch the status bar at the bottom of the screen to see whether your voice is being heard.
5. Use **Copy description** or **Save study notes** to keep the results.

### Keyboard shortcuts

| Keys | Action |
|---|---|
| Alt+R | Repeat |
| Alt+M | More detail |
| Alt+A | Read everything |
| Alt+H | Hear the chart as sound |
| Alt+Q | Interrupt and ask by voice (press again when you finish speaking) |
| Alt+C | Continue reading |
| Alt+S | Stop |
| Alt+T | Change theme |
| Escape | Stop everything and cancel listening |

The page's own Keyboard Shortcuts section is the source of truth if it differs from this table.

---

## API

### `POST /describe`
Multipart form fields:
- `file`: PNG, JPEG or WebP image, up to 8 MB
- `language`: `en` or `hi` (default `en`)

Response: `{"model_used": "...", "result": { ...structured description... }}`

```
curl.exe -X POST http://127.0.0.1:8000/describe -F "file=@samples/chart1.png" -F "language=en"
```
(On macOS or Linux, use `curl` instead of `curl.exe`.)

### `POST /ask`
Multipart form fields:
- `file`: the same image
- `question`: text, up to 500 characters (or send `audio` instead)
- `audio`: optional audio recording of the question, up to 3 MB
- `language`: `en` or `hi`
- `history`: optional JSON list of earlier `{"q": "...", "a": "..."}` pairs (the last three are used)

Response: `{"model_used": "...", "question": "...", "answer": "..."}`

### Errors
| Code | Meaning |
|---|---|
| 400 | Wrong file type, empty file, empty or too long question, unsupported language |
| 413 | Image or recording too large |
| 503 | All AI models are busy; try again in a minute |

---

## Configuration

| Variable | Purpose |
|---|---|
| `GEMINI_API_KEY` | Your Gemini API key (required) |
| `GEMINI_MODEL` | The first model to try; the others in `describer.py` are fallbacks |

---

## Testing and results

The aim is to report what was actually checked. The full log is in [`results.md`](results.md).

Findings so far on a dense stacked bar chart (14 patients, 15 legend entries):
- Chart type, axes, the two patient groups, patient IDs and the legend entries were described correctly in most runs.
- Most key values matched the chart when checked by hand, for example the height of the tallest bars. Estimated values were marked as "about".
- One category (a teal segment) was repeatedly mistaken for a similar green one, so one key value had the wrong name. This is a limit of telling similar colours apart.
- One run counted the legend entries incorrectly (16 instead of 15).
- Answers vary from run to run, even for the same image. Some runs left out an exception that other runs mentioned.
- Prompt changes improved the trend summary and the uncertainty notes, but did not fix the colour mix-up.

More image types (simple charts, diagrams, handwriting, blurry photos) are being added to `results.md`. Hindi output is generated by the model and has not been formally reviewed by a native speaker.

---

## Known limitations

- **AI descriptions can be wrong.** Values read from charts are estimates, and similar colours can be confused. The page tells the student to check important numbers against the original.
- **Interruption uses a key or button** (Alt+Q), not hands-free speech. Detecting a voice over the page's own audio is unreliable on laptop speakers.
- **Voice input** works best in Chrome or Edge, needs microphone permission and, for the browser recognizer, an internet connection.
- **Hindi speech** needs a Hindi voice installed on the device. If none is found, the text is still shown.
- **Free-tier limits.** The free Gemini tier has rate limits and models can be temporarily busy (503 errors). Fallback models and retries reduce this but cannot remove it.
- **The sound chart** plays only the key values, in order, and needs at least three numeric ones.
- **CORS is open** (`allow_origins=["*"]` in `main.py`) for development. Restrict it to your own address before any public deployment.
- **Not formally audited.** The page was built with accessibility in mind and tested with the keyboard, but it has not had a formal accessibility audit or a full screen reader test.

---

## Privacy

- Images and questions are sent to Google's Gemini service to be described. On the free tier, Google may use submitted content to improve its products, so do not upload private or personal documents.
- With the browser voice recognizer in Chrome or Edge, speech is processed by the browser vendor's speech service.
- Settings (theme, text size, speed, language) are stored only in your own browser.
- The server does not store uploaded images.
- Your `.env` file and API key are never committed to the repository.

---

## Troubleshooting

| Problem | What to do |
|---|---|
| `503 UNAVAILABLE` from Gemini | The model is busy. SoundSlate retries and tries other models; wait a minute and try again |
| `404 NOT_FOUND` for a model | The model name is retired or unavailable to your key. Run `python list_models.py` and update `GEMINI_MODEL` in `.env` |
| `429` quota error | You reached a free-tier rate limit. Wait a few minutes |
| `{"detail":"Not Found"}` at `/app` | An old server is still running. Stop all terminals running uvicorn (Ctrl+C) and start one again |
| `uvicorn` is not recognized | The virtual environment is not active. Run the activate command again |
| Page shows old content | Hard refresh with Ctrl+Shift+R |
| No sound in Hindi | Install a Hindi voice (Windows: Settings, Time and language, Speech) |
| Voice input not working | Use Chrome or Edge, allow the microphone, and press **Test microphone** in the settings. Try the "Gemini listens" method if the browser recognizer fails |
| Camera does not open | Allow camera permission in the address bar. On a phone without a secure address, the phone's camera app opens instead |

---

## Roadmap

- Deploy to a public host (the page is served by the same FastAPI app, so one service is enough)
- More test images across charts, diagrams and handwriting, with measured results
- Hands-free interruption, probably headphones only
- Review of the Hindi output with native speakers
- Testing with visually impaired students and a screen reader such as NVDA

---

## Working as a team

- Run `git pull` before you start and before you push.
- Split files between people where possible to avoid conflicts, for example backend (`main.py`, `describer.py`) and frontend (`index.html`).
- Commit small and often, and check `git status` before committing to make sure `.env` is not listed.
- Each person creates their own Gemini API key and their own `.env`.

---

## License

No license has been chosen yet. Until one is added, all rights are reserved by the authors.

---

## Acknowledgements

Powered by the Google Gemini API. Built with FastAPI, Pydantic and the browser's Web Speech, Web Audio and MediaRecorder APIs.
