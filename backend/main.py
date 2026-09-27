from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import os
import uuid

app = FastAPI(title="Free Voice Clone API")

# Allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create folders
os.makedirs("outputs", exist_ok=True)
os.makedirs("uploads", exist_ok=True)

app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")


@app.get("/")
def home():
    return {
        "status": "ok",
        "message": "Voice Clone API is running"
    }


@app.post("/generate")
async def generate(
    voice: UploadFile = File(...),
    text: str = Form(...)
):
    # Save uploaded voice sample
    voice_id = str(uuid.uuid4())

    voice_ext = os.path.splitext(voice.filename or ".wav")[1]
    voice_path = f"uploads/{voice_id}{voice_ext}"

    with open(voice_path, "wb") as f:
        f.write(await voice.read())

    # Temporary placeholder
    # Real voice cloning model will be connected here next.
    audio_name = f"{voice_id}.wav"
    audio_path = f"outputs/{audio_name}"

    # Create empty placeholder file for now
    with open(audio_path, "wb") as f:
        f.write(b"")

    # Create SRT
    srt_name = f"{voice_id}.srt"
    srt_path = f"outputs/{srt_name}"

    srt_content = f"""1
00:00:00,000 --> 00:00:05,000
{text}
"""

    with open(srt_path, "w", encoding="utf-8") as f:
        f.write(srt_content)

    return JSONResponse({
        "audio": f"http://localhost:8000/outputs/{audio_name}",
        "srt": f"http://localhost:8000/outputs/{srt_name}"
    })