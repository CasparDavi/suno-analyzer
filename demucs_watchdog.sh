#!/bin/bash
# Demucs Watchdog
# Hält den Demucs-Server am Leben und startet ihn mit neuer Konfiguration neu.
# Starten: bash ~/demucs_watchdog.sh
# Stoppen: Ctrl+C

VENV="$HOME/demucs-env"
SERVER="$HOME/demucs_server.py"
CONFIG="$HOME/demucs_config.json"
PORT=5001
PING_INTERVAL=3  # Sekunden zwischen Pings

# Default-Config anlegen falls nicht vorhanden
if [ ! -f "$CONFIG" ]; then
  echo '{"model":"htdemucs","shifts":0,"overlap":0.25,"port":5001}' > "$CONFIG"
  echo "Config angelegt: $CONFIG"
fi

SERVER_PID=""

start_server() {
  # Config lesen
  MODEL=$(python3 -c "import json,sys; d=json.load(open('$CONFIG')); print(d.get('model','htdemucs'))")
  SHIFTS=$(python3 -c "import json,sys; d=json.load(open('$CONFIG')); print(d.get('shifts',0))")
  OVERLAP=$(python3 -c "import json,sys; d=json.load(open('$CONFIG')); print(d.get('overlap',0.25))")
  PORT=$(python3 -c "import json,sys; d=json.load(open('$CONFIG')); print(d.get('port',5001))")

  echo "[Watchdog] Starte Server: model=$MODEL shifts=$SHIFTS overlap=$OVERLAP port=$PORT"

  source "$VENV/bin/activate"
  python3 "$SERVER" --model "$MODEL" --shifts "$SHIFTS" --overlap "$OVERLAP" --port "$PORT" &
  SERVER_PID=$!
  echo "[Watchdog] Server PID: $SERVER_PID"
}

stop_server() {
  if [ -n "$SERVER_PID" ]; then
    kill "$SERVER_PID" 2>/dev/null
    wait "$SERVER_PID" 2>/dev/null
    SERVER_PID=""
  fi
}

cleanup() {
  echo ""
  echo "[Watchdog] Beende..."
  stop_server
  exit 0
}

trap cleanup SIGINT SIGTERM

# Ersten Start
start_server
sleep 2

# Watchdog-Schleife
while true; do
  # Server pingen
  STATUS=$(curl -s --max-time 2 "http://localhost:$PORT/status" 2>/dev/null)

  if [ -z "$STATUS" ]; then
    echo "[Watchdog] Server nicht erreichbar — starte neu..."
    stop_server
    sleep 1
    start_server
    sleep 3  # Startzeit abwarten
  fi

  sleep "$PING_INTERVAL"
done
