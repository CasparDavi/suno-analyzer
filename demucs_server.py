#!/usr/bin/env python3
"""
Demucs Stem Separation Server
Startet mit: source ~/demucs-env/bin/activate && python3 demucs_server.py
Läuft auf: http://localhost:5001
"""

from flask import Flask, request, jsonify, send_file
import tempfile, os, subprocess, io, json
import numpy as np

app = Flask(__name__)

# CORS für lokalen Analyzer erlauben
@app.after_request
def add_cors(r):
    r.headers['Access-Control-Allow-Origin'] = '*'
    r.headers['Access-Control-Allow-Methods'] = 'POST, GET, OPTIONS'
    r.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return r

@app.route('/status', methods=['GET'])
def status():
    return jsonify({'status': 'ok', 'model': 'htdemucs'})

@app.route('/separate', methods=['POST', 'OPTIONS'])
def separate():
    if request.method == 'OPTIONS':
        return '', 204

    if 'audio' not in request.files:
        return jsonify({'error': 'Keine Audio-Datei'}), 400

    audio_file = request.files['audio']
    suffix = '.mp3' if audio_file.filename.endswith('.mp3') else '.wav'

    with tempfile.TemporaryDirectory() as tmpdir:
        # Audio speichern
        input_path = os.path.join(tmpdir, 'input' + suffix)
        audio_file.save(input_path)

        # Demucs ausführen
        try:
            result = subprocess.run([
                'python3', '-m', 'demucs',
                '--name', 'htdemucs',
                '--out', tmpdir,
                '--mp3',
                input_path
            ], capture_output=True, text=True, timeout=300)

            if result.returncode != 0:
                return jsonify({'error': result.stderr[-500:]}), 500

        except subprocess.TimeoutExpired:
            return jsonify({'error': 'Timeout — Song zu lang'}), 500

        # Stems einlesen
        stems_dir = os.path.join(tmpdir, 'htdemucs', 'input')
        if not os.path.exists(stems_dir):
            # Fallback: Ordner suchen
            for root, dirs, files in os.walk(tmpdir):
                if any(f.endswith('.mp3') for f in files):
                    stems_dir = root
                    break

        stems = {}
        for stem_name in ['vocals', 'drums', 'bass', 'other']:
            stem_path = os.path.join(stems_dir, stem_name + '.mp3')
            if os.path.exists(stem_path):
                with open(stem_path, 'rb') as f:
                    import base64
                    stems[stem_name] = base64.b64encode(f.read()).decode('utf-8')

        if not stems:
            return jsonify({'error': 'Keine Stems gefunden', 'stderr': result.stderr[-200:]}), 500

        return jsonify({'stems': stems, 'format': 'mp3'})

if __name__ == '__main__':
    print("Demucs Server läuft auf http://localhost:5001")
    print("Stoppen mit Ctrl+C")
    app.run(host='127.0.0.1', port=5001, debug=False)
