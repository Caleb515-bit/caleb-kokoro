from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, Dict, Any
from pathlib import Path
import os
import subprocess

from services.tts_service import synthesize, load_config, OUTPUT_DIR

app = FastAPI(title="Kokoro TTS API")

FRONTEND_URL = os.environ.get("FRONTEND_URL", "*")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL] if FRONTEND_URL != "*" else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/outputs", StaticFiles(directory=str(OUTPUT_DIR)), name="outputs")

@app.on_event("startup")
async def ensure_model():
    model_dir = Path.home() / ".cache" / "kokoro"
    model_path = model_dir / "kokoro-v1.0.onnx"
    voices_path = model_dir / "voices-v1.0.bin"
    if not model_path.exists() or not voices_path.exists():
        print("Model files missing, downloading...")
        subprocess.run(["bash", str(Path(__file__).parent / "setup_model.sh")], check=True)
        print("Model download complete.")

class SynthesisRequest(BaseModel):
    text: str
    engine: Optional[str] = None
    voice: Optional[str] = None
    channel: Optional[str] = None
    ref_audio: Optional[str] = None

@app.get("/config")
async def get_config():
    try:
        return load_config()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/voices")
async def get_voices():
    try:
        from kokoro_onnx import Kokoro
        from pathlib import Path
        
        model_dir = Path.home() / ".cache" / "kokoro"
        kokoro = Kokoro(str(model_dir / "kokoro-v1.0.onnx"), str(model_dir / "voices-v1.0.bin"))
        
        return {
            "kokoro": kokoro.voices,
            "edge": [
                "en-US-GuyNeural", "en-US-JennyNeural", "en-GB-SoniaNeural",
                "en-AU-NatashaNeural", "en-CA-ClaraNeural", "en-IN-NeerjaNeural"
            ],
            "chatterbox": ["Custom reference audio required"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/synthesize")
async def post_synthesize(req: SynthesisRequest):
    if not req.text:
        raise HTTPException(status_code=400, detail="Text is required")
    
    try:
        file_path = await synthesize(
            text=req.text,
            engine=req.engine,
            voice=req.voice,
            channel=req.channel,
            ref_audio=req.ref_audio
        )
        
        # Return the URL to the audio file
        filename = Path(file_path).name
        return {"url": f"/outputs/{filename}"}
        
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
