import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any

# Backend directory
BACKEND_DIR = Path(__file__).parent.parent
CONFIG_PATH = BACKEND_DIR / "channels.json"
OUTPUT_DIR = BACKEND_DIR / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

DEFAULT_CONFIG = {
    "frontline_files": {"engine": "chatterbox", "voice": "narrator_ref.wav"},
    "trivia": {"engine": "kokoro", "voice": "af_heart"},
    "kcaleb": {"engine": "chatterbox", "voice": "archivist_ref.wav"},
    "_default": {"engine": "kokoro", "voice": "af_heart"},
}

def load_config() -> Dict[str, Any]:
    if not CONFIG_PATH.exists():
        CONFIG_PATH.write_text(json.dumps(DEFAULT_CONFIG, indent=2))
    return json.loads(CONFIG_PATH.read_text())

def ensure_model_files():
    import subprocess as _sp
    model_dir = Path.home() / ".cache" / "kokoro"
    model_path = model_dir / "kokoro-v1.0.onnx"
    voices_path = model_dir / "voices-v1.0.bin"
    needs_download = (
        not model_path.exists() or model_path.stat().st_size < 1000000
        or not voices_path.exists() or voices_path.stat().st_size < 100000
    )
    if needs_download:
        model_dir.mkdir(parents=True, exist_ok=True)
        script = BACKEND_DIR / "setup_model.sh"
        if script.exists():
            _sp.run(["bash", str(script)], check=True, timeout=600)
        else:
            raise FileNotFoundError(f"Model files missing and setup script not found at {script}")
    return model_dir

async def run_kokoro(text: str, voice: str, out_path: Path):
    from kokoro_onnx import Kokoro
    import soundfile as sf
    
    model_dir = ensure_model_files()
    model_path = model_dir / "kokoro-v1.0.onnx"
    voices_path = model_dir / "voices-v1.0.bin"

    kokoro = Kokoro(str(model_path), str(voices_path))
    # Kokoro-onnx's create is synchronous, but we can wrap it or just run it
    samples, sample_rate = kokoro.create(text, voice=voice, speed=1.0, lang="en-us")
    sf.write(str(out_path), samples, sample_rate)
    return out_path

async def run_edge(text: str, voice: str, out_path: Path):
    import edge_tts
    communicate = edge_tts.Communicate(text, voice or "en-US-GuyNeural")
    await communicate.save(str(out_path))
    return out_path

async def run_chatterbox(text: str, ref_audio: str, out_path: Path):
    try:
        import torchaudio as ta
        from chatterbox.tts import ChatterboxTTS
    except ImportError:
        raise ImportError("Chatterbox not installed. Requires GPU and manual setup.")

    if not ref_audio or not Path(ref_audio).exists():
        raise FileNotFoundError(f"Chatterbox needs a reference audio file: {ref_audio}")

    model = ChatterboxTTS.from_pretrained(device="cuda")
    wav = model.generate(text, audio_prompt_path=ref_audio)
    ta.save(str(out_path), wav, model.sr)
    return out_path

async def synthesize(
    text: str, 
    engine: str, 
    voice: Optional[str] = None, 
    channel: Optional[str] = None,
    ref_audio: Optional[str] = None
) -> str:
    config = load_config()
    
    if channel:
        preset = config.get(channel, config["_default"])
        engine = engine or preset["engine"]
        voice = voice or preset["voice"]
    
    if not engine:
        engine = "kokoro" # fallback
        
    if engine == "kokoro":
        voice = voice or "af_heart"
    elif engine == "edge":
        voice = voice or "en-US-GuyNeural"
    
    # Generate unique filename
    import hashlib
    file_hash = hashlib.md5(f"{text}{engine}{voice}{channel}".encode()).hexdigest()
    out_filename = f"{file_hash}.wav"
    out_path = OUTPUT_DIR / out_filename
    
    # If already exists, just return it (caching)
    # if out_path.exists():
    #     return str(out_path)

    if engine == "kokoro":
        await run_kokoro(text, voice, out_path)
    elif engine == "edge":
        await run_edge(text, voice, out_path)
    elif engine == "chatterbox":
        await run_chatterbox(text, ref_audio or voice, out_path)
    else:
        raise ValueError(f"Unknown engine: {engine}")
        
    return str(out_path)
