#!/usr/bin/env bash

# start.sh — Starts both the FastAPI backend and the Vite frontend.

# Root directory
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 1. Start Backend
echo "Starting Backend..."
cd "$ROOT_DIR/backend"
source venv/bin/activate
# Run uvicorn in the background
uvicorn main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# 2. Start Frontend
echo "Starting Frontend..."
cd "$ROOT_DIR/frontend"
# Run vite preview (serves built files) instead of dev server
    npm run preview -- --host 0.0.0.0 &
FRONTEND_PID=$!

echo ""
echo "Kokoro Web UI is starting up!"
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop both."

# Handle cleanup on exit
trap "kill $BACKEND_PID $FRONTEND_PID; exit" SIGINT SIGTERM

# Keep script running
wait
