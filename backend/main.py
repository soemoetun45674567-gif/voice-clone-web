from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse

import os
import uuid
import soundfile as sf

from voxcpm import VoxCPM


app = FastAPI(title="Free Myanmar Voice Clone API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("outputs", exist_ok=True)
os.makedirs("uploads", exist_ok=True)

app.mount(
    "/outputs",
    StaticFiles(directory="outputs"),
    name="outputs"
)


# Load VoxCPM2 model
model = VoxCPM.from_pretrained(
    "openbmb/VoxCPM2",
    load_denoiser=False
)


@app.get("/")
def home():
    return {
        "status": "ok",
        "model": "VoxCPM2",
        "message": "Myanmar Voice Clone API is running"
    }


@app.post("/generate")
async def generate(
    voice: UploadFile = File(...),
    text: str = Form(...)
):
    voice_id = str(uuid.uuid4())

    # Save reference voice
    voice_ext = os.path.splitext(
        voice.filename or ".wav"
    )[1]

    voice_path = f"uploads/{voice_id}{voice_ext}"

    with open(voice_path, "wb") as f:
        f.write(await voice.read())

    # Generate cloned voice
    audio = model.generate(
        text=text,
        reference_wav_path=voice_path,
        cfg_value=2.0,
        inference_timesteps=10
    )

    # Save audio
    audio_name = f"{voice_id}.wav"
    audio_path = f"outputs/{audio_name}"

    sf.write(
        audio_path,
        audio,
        model.tts_model.sample_rate
    )

    # Simple SRT
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