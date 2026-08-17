#!/usr/bin/env bash
# setup_kokoro.sh — run this ONCE. Downloads Kokoro model files to a
# persistent cache folder so tts_router.py never has to fetch them again.

set -e

MODEL_DIR="$HOME/.cache/kokoro"
mkdir -p "$MODEL_DIR"

echo "Downloading Kokoro model files to $MODEL_DIR (one-time, ~300MB total)..."

if [ ! -f "$MODEL_DIR/kokoro-v0_19.onnx" ]; then
    curl -L --progress-bar -o "$MODEL_DIR/kokoro-v1.0.onnx" \
        https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx
else
    echo "kokoro-v0_19.onnx already cached, skipping."
fi

if [ ! -f "$MODEL_DIR/voices-v1.0.bin" ]; then
    curl -L --progress-bar -o "$MODEL_DIR/voices-v1.0.bin" \
        https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin
else
    echo "voices-v1.0.bin already cached, skipping."
fi

echo ""
echo "Done. Models cached at $MODEL_DIR"
echo "tts_router.py will now find them automatically — no more downloads."
