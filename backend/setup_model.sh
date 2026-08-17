#!/bin/bash
# Download Kokoro model files (~300MB) for Railway or local setup
set -e
MODEL_DIR="$HOME/.cache/kokoro"
mkdir -p "$MODEL_DIR"
cd "$MODEL_DIR"

if [ ! -f "kokoro-v1.0.onnx" ]; then
  echo "Downloading kokoro-v1.0.onnx..."
  curl -L -o kokoro-v1.0.onnx "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files/kokoro-v1.0.onnx"
fi

if [ ! -f "voices-v1.0.bin" ]; then
  echo "Downloading voices-v1.0.bin..."
  curl -L -o voices-v1.0.bin "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files/voices-v1.0.bin"
fi

echo "Model files ready in $MODEL_DIR"
