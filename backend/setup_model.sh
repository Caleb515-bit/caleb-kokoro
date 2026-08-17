#!/bin/bash
# Download Kokoro model files (~300MB) for Railway or local setup
set -e
MODEL_DIR="$HOME/.cache/kokoro"
mkdir -p "$MODEL_DIR"
cd "$MODEL_DIR"

if [ ! -f "kokoro-v1.0.onnx" ] || [ $(stat -c%s "kokoro-v1.0.onnx" 2>/dev/null || echo 0) -lt 1000000 ]; then
  rm -f kokoro-v1.0.onnx
  echo "Downloading kokoro-v1.0.onnx..."
  curl -L -o kokoro-v1.0.onnx "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files/kokoro-v1.0.onnx"
  SIZE=$(stat -c%s kokoro-v1.0.onnx)
  echo "Downloaded $SIZE bytes"
  if [ "$SIZE" -lt 1000000 ]; then
    echo "ERROR: File too small ($SIZE bytes), download likely failed"
    rm -f kokoro-v1.0.onnx
    exit 1
  fi
fi

if [ ! -f "voices-v1.0.bin" ] || [ $(stat -c%s "voices-v1.0.bin" 2>/dev/null || echo 0) -lt 100000 ]; then
  rm -f voices-v1.0.bin
  echo "Downloading voices-v1.0.bin..."
  curl -L -o voices-v1.0.bin "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files/voices-v1.0.bin"
  SIZE=$(stat -c%s voices-v1.0.bin)
  echo "Downloaded $SIZE bytes"
  if [ "$SIZE" -lt 100000 ]; then
    echo "ERROR: File too small ($SIZE bytes), download likely failed"
    rm -f voices-v1.0.bin
    exit 1
  fi
fi

echo "Model files ready in $MODEL_DIR"
