#!/usr/bin/env python3
"""
tts_router.py — Unified TTS engine for YouTube automation pipeline.

Connects three engines behind one interface:
  - kokoro     : self-hosted, CPU-friendly, default for high-volume narration
  - edge       : free API, zero setup, fallback / secondary voice
  - chatterbox : self-hosted voice cloning, GPU required (use RunPod on-demand)

Usage:
    python tts_router.py --engine kokoro --text "Hello world" --out audio.wav
    python tts_router.py --engine edge --voice en-US-GuyNeural --text-file script.txt --out audio.mp3
    python tts_router.py --engine chatterbox --text-file script.txt --ref-audio my_voice.wav --out audio.wav

Config:
    Per-channel defaults live in channels.json (created on first run if missing).
    Each channel maps to an engine + voice, so your pipeline just passes
    --channel frontline_files instead of remembering engine/voice each time.

Install notes (do these once, separately, based on which engines you use):
    pip install kokoro-onnx soundfile          # Kokoro
    pip install edge-tts                        # Edge TTS
    # Chatterbox: follow https://github.com/resemble-ai/chatterbox
    # (needs GPU — run via RunPod pod if no local GPU)
"""

import argparse
import asyncio
import json
import sys
from pathlib import Path

CONFIG_PATH = Path(__file__).parent / "channels.json"

DEFAULT_CONFIG = {
    "frontline_files": {"engine": "chatterbox", "voice": "narrator_ref.wav"},
    "trivia": {"engine": "kokoro", "voice": "af_heart"},
    "kcaleb": {"engine": "chatterbox", "voice": "archivist_ref.wav"},
    "_default": {"engine": "kokoro", "voice": "af_heart"},
}


def load_config():
    if not CONFIG_PATH.exists():
        CONFIG_PATH.write_text(json.dumps(DEFAULT_CONFIG, indent=2))
        print(f"Created default config at {CONFIG_PATH} — edit it to map your channels.")
    return json.loads(CONFIG_PATH.read_text())


def get_text(args):
    if args.text:
        return args.text
    if args.text_file:
        return Path(args.text_file).read_text().strip()
    raise ValueError("Provide --text or --text-file")


# ---------------------------------------------------------------------------
# Engine 1: Kokoro — fast, CPU, no cloning. Default for bulk narration.
# ---------------------------------------------------------------------------
def run_kokoro(text: str, voice: str, out: str):
    try:
        from kokoro_onnx import Kokoro
        import soundfile as sf
    except ImportError:
        sys.exit("Kokoro not installed. Run: pip install kokoro-onnx soundfile")

    # Models live in a persistent cache (~/.cache/kokoro) — run setup_kokoro.sh
    # once and this never re-downloads.
    model_dir = Path.home() / ".cache" / "kokoro"
    model_path = model_dir / "kokoro-v1.0.onnx"
    voices_path = model_dir / "voices-v1.0.bin"

    if not model_path.exists() or not voices_path.exists():
        sys.exit(
            f"Kokoro model files not found in {model_dir}.\n"
            f"Run setup_kokoro.sh once to download them, then this will be instant every time after."
        )

    kokoro = Kokoro(str(model_path), str(voices_path))
    samples, sample_rate = kokoro.create(text, voice=voice, speed=1.0, lang="en-us")
    sf.write(out, samples, sample_rate)
    print(f"[kokoro] wrote {out}")


# ---------------------------------------------------------------------------
# Engine 2: Edge TTS — free API, zero setup. Fallback / variety voice.
# ---------------------------------------------------------------------------
def run_edge(text: str, voice: str, out: str):
    try:
        import edge_tts
    except ImportError:
        sys.exit("edge-tts not installed. Run: pip install edge-tts")

    async def _speak():
        communicate = edge_tts.Communicate(text, voice or "en-US-GuyNeural")
        await communicate.save(out)

    asyncio.run(_speak())
    print(f"[edge] wrote {out}")


# ---------------------------------------------------------------------------
# Engine 3: Chatterbox — self-hosted voice cloning. GPU required.
# Run locally if you have a GPU, or on a RunPod instance and call this
# script remotely / via SSH from your GitHub Actions job.
# ---------------------------------------------------------------------------
def run_chatterbox(text: str, ref_audio: str, out: str):
    try:
        import torchaudio as ta
        from chatterbox.tts import ChatterboxTTS
    except ImportError:
        sys.exit(
            "Chatterbox not installed. Follow setup at "
            "https://github.com/resemble-ai/chatterbox (requires GPU)."
        )

    if not ref_audio or not Path(ref_audio).exists():
        sys.exit("Chatterbox needs a --ref-audio file (a few seconds of the target voice).")

    model = ChatterboxTTS.from_pretrained(device="cuda")
    wav = model.generate(text, audio_prompt_path=ref_audio)
    ta.save(out, wav, model.sr)
    print(f"[chatterbox] wrote {out}")


# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Unified TTS router")
    parser.add_argument("--engine", choices=["kokoro", "edge", "chatterbox"])
    parser.add_argument("--channel", help="Use channel preset from channels.json instead of --engine")
    parser.add_argument("--text")
    parser.add_argument("--text-file")
    parser.add_argument("--voice", help="Voice name (kokoro/edge) — overrides channel config")
    parser.add_argument("--ref-audio", help="Reference audio for chatterbox cloning")
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    config = load_config()
    engine = args.engine
    voice = args.voice

    if args.channel:
        preset = config.get(args.channel, config["_default"])
        engine = engine or preset["engine"]
        voice = voice or preset["voice"]

    if not engine:
        sys.exit("Specify --engine or --channel.")

    text = get_text(args)

    if engine == "kokoro":
        run_kokoro(text, voice or "af_heart", args.out)
    elif engine == "edge":
        run_edge(text, voice, args.out)
    elif engine == "chatterbox":
        run_chatterbox(text, args.ref_audio or voice, args.out)


if __name__ == "__main__":
    main()
