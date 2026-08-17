from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from pathlib import Path
import os
import subprocess

from services.tts_service import synthesize, load_config, OUTPUT_DIR, run_kokoro

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
        try:
            subprocess.run(["bash", str(Path(__file__).parent / "setup_model.sh")], check=True, timeout=600)
            print("Model download complete.")
        except Exception as e:
            print(f"WARNING: Model download failed: {e}. Server will start but kokoro engine may not work.")
    else:
        print("Model files already present.")

VOICE_LIST: List[Dict[str, str]] = [
    {"id": "af_alloy", "name": "Alloy", "lang": "English (US)", "gender": "Female"},
    {"id": "af_aoede", "name": "Aoede", "lang": "English (US)", "gender": "Female"},
    {"id": "af_bella", "name": "Bella", "lang": "English (US)", "gender": "Female"},
    {"id": "af_heart", "name": "Heart", "lang": "English (US)", "gender": "Female"},
    {"id": "af_jessica", "name": "Jessica", "lang": "English (US)", "gender": "Female"},
    {"id": "af_kore", "name": "Kore", "lang": "English (US)", "gender": "Female"},
    {"id": "af_nicole", "name": "Nicole", "lang": "English (US)", "gender": "Female"},
    {"id": "af_nova", "name": "Nova", "lang": "English (US)", "gender": "Female"},
    {"id": "af_river", "name": "River", "lang": "English (US)", "gender": "Female"},
    {"id": "af_sarah", "name": "Sarah", "lang": "English (US)", "gender": "Female"},
    {"id": "af_sky", "name": "Sky", "lang": "English (US)", "gender": "Female"},
    {"id": "am_adam", "name": "Adam", "lang": "English (US)", "gender": "Male"},
    {"id": "am_echo", "name": "Echo", "lang": "English (US)", "gender": "Male"},
    {"id": "am_eric", "name": "Eric", "lang": "English (US)", "gender": "Male"},
    {"id": "am_fenrir", "name": "Fenrir", "lang": "English (US)", "gender": "Male"},
    {"id": "am_liam", "name": "Liam", "lang": "English (US)", "gender": "Male"},
    {"id": "am_michael", "name": "Michael", "lang": "English (US)", "gender": "Male"},
    {"id": "am_onyx", "name": "Onyx", "lang": "English (US)", "gender": "Male"},
    {"id": "am_puck", "name": "Puck", "lang": "English (US)", "gender": "Male"},
    {"id": "am_santa", "name": "Santa", "lang": "English (US)", "gender": "Male"},
    {"id": "bf_alice", "name": "Alice", "lang": "English (UK)", "gender": "Female"},
    {"id": "bf_emma", "name": "Emma", "lang": "English (UK)", "gender": "Female"},
    {"id": "bf_isabella", "name": "Isabella", "lang": "English (UK)", "gender": "Female"},
    {"id": "bf_lily", "name": "Lily", "lang": "English (UK)", "gender": "Female"},
    {"id": "bm_daniel", "name": "Daniel", "lang": "English (UK)", "gender": "Male"},
    {"id": "bm_fable", "name": "Fable", "lang": "English (UK)", "gender": "Male"},
    {"id": "bm_george", "name": "George", "lang": "English (UK)", "gender": "Male"},
    {"id": "bm_lewis", "name": "Lewis", "lang": "English (UK)", "gender": "Male"},
    {"id": "ef_dora", "name": "Dora", "lang": "Spanish", "gender": "Female"},
    {"id": "em_alex", "name": "Alex", "lang": "Spanish", "gender": "Male"},
    {"id": "em_santa", "name": "Santa", "lang": "Spanish", "gender": "Male"},
    {"id": "ff_siwis", "name": "Siwis", "lang": "French", "gender": "Female"},
    {"id": "hf_alpha", "name": "Alpha", "lang": "Hindi", "gender": "Female"},
    {"id": "hf_beta", "name": "Beta", "lang": "Hindi", "gender": "Female"},
    {"id": "hm_omega", "name": "Omega", "lang": "Hindi", "gender": "Male"},
    {"id": "hm_psi", "name": "Psi", "lang": "Hindi", "gender": "Male"},
    {"id": "if_sara", "name": "Sara", "lang": "Italian", "gender": "Female"},
    {"id": "im_nicola", "name": "Nicola", "lang": "Italian", "gender": "Male"},
    {"id": "jf_alpha", "name": "Alpha", "lang": "Japanese", "gender": "Female"},
    {"id": "jf_gongitsune", "name": "Gongitsune", "lang": "Japanese", "gender": "Female"},
    {"id": "jf_nezumi", "name": "Nezumi", "lang": "Japanese", "gender": "Female"},
    {"id": "jf_tebukuro", "name": "Tebukuro", "lang": "Japanese", "gender": "Female"},
    {"id": "jm_kumo", "name": "Kumo", "lang": "Japanese", "gender": "Male"},
    {"id": "pf_dora", "name": "Dora", "lang": "Portuguese (BR)", "gender": "Female"},
    {"id": "pm_alex", "name": "Alex", "lang": "Portuguese (BR)", "gender": "Male"},
    {"id": "pm_santa", "name": "Santa", "lang": "Portuguese (BR)", "gender": "Male"},
    {"id": "zf_xiaobei", "name": "Xiaobei", "lang": "Chinese (Mandarin)", "gender": "Female"},
    {"id": "zf_xiaoni", "name": "Xiaoni", "lang": "Chinese (Mandarin)", "gender": "Female"},
    {"id": "zf_xiaoxiao", "name": "Xiaoxiao", "lang": "Chinese (Mandarin)", "gender": "Female"},
    {"id": "zf_xiaoyi", "name": "Xiaoyi", "lang": "Chinese (Mandarin)", "gender": "Female"},
    {"id": "zm_yunjian", "name": "Yunjian", "lang": "Chinese (Mandarin)", "gender": "Male"},
    {"id": "zm_yunxi", "name": "Yunxi", "lang": "Chinese (Mandarin)", "gender": "Male"},
    {"id": "zm_yunxia", "name": "Yunxia", "lang": "Chinese (Mandarin)", "gender": "Male"},
    {"id": "zm_yunyang", "name": "Yunyang", "lang": "Chinese (Mandarin)", "gender": "Male"},
]

class SynthesisRequest(BaseModel):
    text: str
    engine: Optional[str] = None
    voice: Optional[str] = None
    channel: Optional[str] = None
    ref_audio: Optional[str] = None

class PreviewRequest(BaseModel):
    voice: str

@app.get("/config")
async def get_config():
    try:
        return load_config()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/voices")
async def get_voices():
    return {"voices": VOICE_LIST}

@app.post("/preview")
async def preview_voice(req: PreviewRequest):
    voice_name = req.voice.split("_", 1)[1].capitalize() if "_" in req.voice else req.voice
    text = f"Hi, I'm {voice_name}. Nice to meet you!"
    try:
        import hashlib
        file_hash = hashlib.md5(f"preview_{req.voice}".encode()).hexdigest()
        out_filename = f"preview_{file_hash}.wav"
        out_path = OUTPUT_DIR / out_filename

        await run_kokoro(text, req.voice, out_path)

        return {"url": f"/outputs/{out_filename}"}
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

        filename = Path(file_path).name
        return {"url": f"/outputs/{filename}"}

    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
