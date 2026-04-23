#!/usr/bin/env python3
"""
Demucs Stem Separation Server
Wird normalerweise vom Watchdog gestartet — nicht direkt aufrufen.
Direkt starten: source ~/demucs-env/bin/activate && python3 demucs_server.py [Optionen]
"""

import argparse, base64, json, os, signal, subprocess, sys, tempfile
from flask import Flask, request, jsonify

parser = argparse.ArgumentParser()
parser.add_argument('--model', default='htdemucs',
    choices=['htdemucs','htdemucs_ft','htdemucs_6s','mdx_extra','mdx_extra_q'])
parser.add_argument('--shifts', type=int, default=0)
parser.add_argument('--overlap', type=float, default=0.25)
parser.add_argument('--port', type=int, default=5001)
args = parser.parse_args()

STEMS_4 = ['vocals','drums','bass','other']
STEMS_6 = ['vocals','drums','bass','guitar','piano','other']

app = Flask(__name__)

@app.after_request
def add_cors(r):
    r.headers['Access-Control-Allow-Origin'] = '*'
    r.headers['Access-Control-Allow-Methods'] = 'POST, GET, OPTIONS'
    r.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return r

@app.route('/status', methods=['GET'])
def status():
    stem_names = STEMS_6 if args.model == 'htdemucs_6s' else STEMS_4
    return jsonify({
        'status': 'ok',
        'model': args.model,
        'stems': stem_names,
        'shifts': args.shifts,
        'overlap': args.overlap
    })

@app.route('/config', methods=['POST'])
def set_config():
    """Config in ~/demucs_config.json schreiben."""
    try:
        data = request.get_json()
        config_path = os.path.expanduser('~/demucs_config.json')
        with open(config_path, 'w') as f:
            json.dump(data, f, indent=2)
        return jsonify({'status': 'ok', 'config': data})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/proxy', methods=['GET'])
def proxy():
    """Holt externe URLs für den Browser — umgeht CORS."""
    import urllib.request
    url = request.args.get('url','')
    if not url:
        return jsonify({'error': 'Keine URL'}), 400
    # Nur Suno erlauben
    if 'suno.com' not in url:
        return jsonify({'error': 'Nur suno.com erlaubt'}), 403
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        })
        with urllib.request.urlopen(req, timeout=15) as r:
            content_type = r.headers.get('Content-Type', 'text/html')
            body = r.read().decode('utf-8', errors='replace')
        from flask import Response
        return Response(body, content_type=content_type)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/shutdown', methods=['POST', 'GET'])
def shutdown():
    """Watchdog bemerkt den Ausfall und startet mit neuer Config neu."""
    os.kill(os.getpid(), signal.SIGTERM)
    return jsonify({'status': 'shutting down'})

@app.route('/separate', methods=['POST', 'OPTIONS'])
def separate():
    if request.method == 'OPTIONS':
        return '', 204
    if 'audio' not in request.files:
        return jsonify({'error': 'Keine Audio-Datei'}), 400

    audio_file = request.files['audio']
    suffix = '.mp3' if audio_file.filename.endswith('.mp3') else '.wav'

    with tempfile.TemporaryDirectory() as tmpdir:
        input_path = os.path.join(tmpdir, 'input' + suffix)
        audio_file.save(input_path)

        cmd = [
            sys.executable, '-m', 'demucs',
            '--name', args.model,
            '--out', tmpdir,
            '--mp3',
            '--overlap', str(args.overlap),
        ]
        if args.shifts > 0:
            cmd += ['--shifts', str(args.shifts)]
        cmd.append(input_path)

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
            if result.returncode != 0:
                return jsonify({'error': result.stderr[-500:]}), 500
        except subprocess.TimeoutExpired:
            return jsonify({'error': 'Timeout'}), 500

        stems_dir = os.path.join(tmpdir, args.model, 'input')
        if not os.path.exists(stems_dir):
            for root, dirs, files in os.walk(tmpdir):
                if any(f.endswith('.mp3') for f in files):
                    stems_dir = root
                    break

        stem_names = STEMS_6 if args.model == 'htdemucs_6s' else STEMS_4
        stems = {}
        for name in stem_names:
            path = os.path.join(stems_dir, name + '.mp3')
            if os.path.exists(path):
                with open(path, 'rb') as f:
                    stems[name] = base64.b64encode(f.read()).decode('utf-8')

        if not stems:
            return jsonify({'error': 'Keine Stems gefunden', 'debug': result.stderr[-300:]}), 500

        return jsonify({'stems': stems, 'model': args.model, 'stem_names': stem_names})

if __name__ == '__main__':
    stem_names = STEMS_6 if args.model == 'htdemucs_6s' else STEMS_4
    print(f"Demucs Server · {args.model} · {stem_names}")
    print(f"http://localhost:{args.port}")
    app.run(host='127.0.0.1', port=args.port, debug=False)
