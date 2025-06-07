#!/bin/bash
set -e

echo "🔄 Starting Flask app behind Gunicorn..."
sudo systemctl start mariadb
# Determine project directory (directory of this script)
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR" || {
  echo "❌ Project folder not found!"
  exit 1
}

# Activate virtual environment
if [ -f "$PROJECT_DIR/flaskenv/bin/activate" ]; then
  source "$PROJECT_DIR/flaskenv/bin/activate"
else
  echo "❌ Virtual environment not found at $PROJECT_DIR/flaskenv"
  exit 1
fi

# Kill anything already running on port 8000
PORT=8000
PID=$(lsof -t -i:$PORT)
if [ -n "$PID" ]; then
  echo "⚠️ Port $PORT is in use by PID(s): $PID"
  fuser -k ${PORT}/tcp
fi

# Start Gunicorn in the background
echo "🚀 Launching Gunicorn..."
nohup gunicorn -w 4 -b 127.0.0.1:$PORT main:app > gunicorn.log 2>&1 &

# Restart nginx
echo "🔄 Restarting NGINX..."
sudo systemctl restart nginx

echo "✅ Site is now live at: https://novari.duckdns.org"

