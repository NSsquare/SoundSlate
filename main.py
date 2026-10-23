import json
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from describer import describe_image, answer_question, answer_voice, AllModelsBusy

app = FastAPI(title="SoundSlate")

# Let web pages from other addresses call this server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

ALLOWED_TYPES = {"image/png", "image/jpeg", "image/webp"}
ALLOWED_LANGUAGES = {"en", "hi"}
MAX_BYTES = 8 * 1024 * 1024    # 8 MB for images
MAX_AUDIO = 3 * 1024 * 1024    # 3 MB for spoken questions
MAX_QUESTION = 500             # characters

BUSY_MESSAGE = "The AI service is busy right now. Please try again in a minute."


def read_image(file: UploadFile):
    # Check the upload and return its bytes
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400, detail="Please upload a PNG, JPEG or WebP image."
        )
    image_bytes = file.file.read()
    if not image_bytes:
        raise HTTPException(status_code=400, detail="The uploaded file is empty.")
    if len(image_bytes) > MAX_BYTES:
        raise HTTPException(status_code=413, detail="Image is too large (max 8 MB).")
    return image_bytes


def clean_history(raw):
    # Turn the history text from the page into a safe, short list
    try:
        items = json.loads(raw)
    except ValueError:
        return []
    if not isinstance(items, list):
        return []
    cleaned = []
    for item in items[-3:]:
        if (
            isinstance(item, dict)
            and isinstance(item.get("q"), str)
            and isinstance(item.get("a"), str)
        ):
            cleaned.append({"q": item["q"][:MAX_QUESTION], "a": item["a"][:800]})
    return cleaned


@app.get("/")
def home():
    return {"message": "SoundSlate is running"}


@app.get("/app")
def web_page():
    # Serve the student-facing page
    return FileResponse("index.html")


@app.post("/describe")
def describe(file: UploadFile = File(...), language: str = Form("en")):
    if language not in ALLOWED_LANGUAGES:
        raise HTTPException(status_code=400, detail="Unsupported language.")
    image_bytes = read_image(file)
    try:
        model_used, result = describe_image(image_bytes, file.content_type, language)
    except AllModelsBusy:
        raise HTTPException(status_code=503, detail=BUSY_MESSAGE)
    return {"model_used": model_used, "result": result}


@app.post("/ask")
def ask_question(
    file: UploadFile = File(...),
    question: str = Form(""),
    language: str = Form("en"),
    history: str = Form("[]"),
    audio: UploadFile | None = File(None),
):
    if language not in ALLOWED_LANGUAGES:
        raise HTTPException(status_code=400, detail="Unsupported language.")
    image_bytes = read_image(file)
    past = clean_history(history)

    # Spoken question: the audio recording comes with the image
    if audio is not None:
        if not (audio.content_type or "").startswith("audio/"):
            raise HTTPException(status_code=400, detail="Please send the question as audio.")
        audio_bytes = audio.file.read()
        if not audio_bytes:
            raise HTTPException(status_code=400, detail="The recording is empty.")
        if len(audio_bytes) > MAX_AUDIO:
            raise HTTPException(status_code=413, detail="The recording is too long.")
        try:
            model_used, result = answer_voice(
                image_bytes, file.content_type, audio_bytes, audio.content_type, language, past
            )
        except AllModelsBusy:
            raise HTTPException(status_code=503, detail=BUSY_MESSAGE)
        return {
            "model_used": model_used,
            "question": result.question_heard.strip(),
            "answer": result.answer.strip(),
        }

    # Typed question
    question = question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Please ask a question.")
    if len(question) > MAX_QUESTION:
        raise HTTPException(
            status_code=400, detail="Question is too long (max 500 characters)."
        )
    try:
        model_used, answer = answer_question(
            image_bytes, file.content_type, question, language, past
        )
    except AllModelsBusy:
        raise HTTPException(status_code=503, detail=BUSY_MESSAGE)
    return {"model_used": model_used, "question": question, "answer": answer}