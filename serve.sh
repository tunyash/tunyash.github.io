#!/bin/bash
# Simple script to serve the website locally for development

PORT=${1:-800}

echo "Starting local server on port $PORT..."
echo "Open http://localhost:$PORT in your browser"
echo "Press Ctrl+C to stop"
echo ""

cd "$(dirname "$0")"
python3 -m http.server "$PORT"

