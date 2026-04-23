# Suno Audio Analyzer

Ein lokales Browser-Tool zur Analyse von Suno-Songs — Spektrogramme, BPM, Tonart, Dynamik, Instrument-Erkennung und Stem-Trennung.

## Nutzung

### Einfach (ohne Stem-Trennung)

Die Datei `suno_analyzer.html` direkt im Browser öffnen — keine Installation nötig.

```
Datei → Öffnen → suno_analyzer.html
```

Oder über GitHub Pages (eingeschränkte Funktionalität, siehe unten):
```
https://caspardavi.github.io/suno-analyzer/suno_analyzer.html
```

### Mit Stem-Trennung (Demucs)

Stem-Trennung läuft lokal auf deinem Rechner und benötigt Python.

**Einmalige Installation:**

```bash
python3 -m venv ~/demucs-env
source ~/demucs-env/bin/activate
pip install demucs flask
```

**Server starten** (vor jeder Nutzung):

```bash
source ~/demucs-env/bin/activate
python3 demucs_server.py
```

Der Server läuft dann auf `http://localhost:5001`. Der Analyzer erkennt ihn automatisch und schaltet den "Stems trennen"-Button frei.

**Stems trennen:**

1. Song analysieren (URL eingeben → Analysieren)
2. "Stems trennen" klicken
3. Warten (~1–3 Minuten je nach Song-Länge und Rechner)
4. Vier Audio-Player erscheinen: Gesang, Drums, Bass, Rest

---

## Einschränkungen bei GitHub Pages

Wenn der Analyzer über GitHub Pages aufgerufen wird (nicht lokal), funktionieren folgende Features **nicht**:

| Feature | Lokal | GitHub Pages |
|---|---|---|
| Song-Analyse (FFT, BPM, Spektrogramm) | ✓ | ✓ |
| Instrument-Erkennung (Essentia) | ✓ | ✓ |
| Suno-Metadaten (Plays, Likes, Kommentare) | ✓ | ✗ |
| Lyrics-Extraktion | ✓ | ✗ |
| Stem-Trennung (Demucs) | ✓ | ✗ |

Die Metadaten und Lyrics funktionieren nur lokal weil der Browser beim Öffnen einer lokalen Datei keine CORS-Beschränkungen hat. GitHub Pages hat eine eigene Origin (`caspardavi.github.io`) und Suno blockt Cross-Origin-Requests.

---

## Features

- Spektrogramm (logarithmisch, Perzentil-Skalierung)
- Stereo-Spektrogramm (L/R Kanalbalance)
- BPM-Kurve über Zeit
- Tonart und Modus
- Dynamikumfang (Crestfaktor)
- Lautheit (RMS/LUFS)
- Stimmanalyse (männlich/weiblich)
- Pitch und Noten-Stabilität
- Harmonische Dichte und Inharmonizität
- Spektraler Tilt und Centroid
- Instrument-Erkennung (Essentia MTG Jamendo-Modell, 40 Klassen)
- Stem-Trennung (Demucs htdemucs, 4 Stems)
- Kommentar-Generator (Prompt für LLM)
- Zoom und Playhead-Synchronisation

---

## Modell-Dateien

Im Ordner `models/` liegen die Essentia-Modelle für die Instrument-Erkennung:

- `discogs-effnet-bsdynamic-1.onnx` — Embedding-Modell (Discogs, ~18MB)
- `mtg_jamendo_instrument-discogs-effnet-1.onnx` — Instrument-Klassifikator (~2.6MB)
- `mtg_jamendo_instrument-discogs-effnet-1.json` — Klassen-Labels

Quelle: [essentia.upf.edu](https://essentia.upf.edu/models/) (Music Technology Group, UPF Barcelona)

---

## Technologie

- Web Audio API + OfflineAudioContext
- Canvas 2D für alle Visualisierungen
- Web Worker für FFT-Analyse
- ONNX Runtime Web für ML-Inferenz
- Demucs (Meta) für Stem-Trennung
- Flask für lokalen Demucs-Server
