from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from describer import describe_image, AllModelsBusy

app = FastAPI(title="SoundSlate")

# Let web pages from other addresses call this server (explained below)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

ALLOWED_TYPES = {"image/png", "image/jpeg", "image/webp"}
MAX_BYTES = 8 * 1024 * 1024  # 8 MB


@app.get("/")
def home():
    return {"message": "SoundSlate is running"}


@app.post("/describe")
def describe(file: UploadFile = File(...)):
    # 1. Check the file type
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400, detail="Please upload a PNG, JPEG or WebP image."
        )

    # 2. Read the file and check its size
    image_bytes = file.file.read()
    if not image_bytes:
        raise HTTPException(status_code=400, detail="The uploaded file is empty.")
    if len(image_bytes) > MAX_BYTES:
        raise HTTPException(status_code=413, detail="Image is too large (max 8 MB).")

    # 3. Ask Gemini, and turn failures into friendly errors
    try:
        model_used, result = describe_image(image_bytes, file.content_type)
    except AllModelsBusy:
        raise HTTPException(
            status_code=503,
            detail="The AI service is busy right now. Please try again in a minute.",
        )

    # 4. Send the structured description back as JSON
    return {"model_used": model_used, "result": result}