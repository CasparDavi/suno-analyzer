# Suno Audio Analyzer

Browser-Tool zur Analyse von Suno-Songs — Spektrogramme, BPM, Tonart, Dynamik, Instrument-Erkennung und Stem-Trennung.

---

## Schnellstart (ohne Stem-Trennung)

`suno_analyzer.html` direkt im Browser öffnen — keine Installation nötig.

Oder über GitHub Pages (eingeschränkte Funktionalität, siehe unten):
```
https://caspardavi.github.io/suno-analyzer/suno_analyzer.html
```

---

## Stem-Trennung (Demucs)

### Einmalige Installation

```bash
python3 -m venv ~/demucs-env
source ~/demucs-env/bin/activate
pip install demucs flask
```

### Server starten

**Empfohlen — mit Watchdog:**
```bash
bash ~/demucs_watchdog.sh
```

**Alternativ — direkt:**
```bash
source ~/demucs-env/bin/activate
python3 ~/demucs_server.py
```

### Konfiguration im Analyzer

| Einstellung | Optionen | Bedeutung |
|---|---|---|
| **Modell** | `htdemucs` | 4 Stems, schnell (Standard) |
| | `htdemucs_ft` | 4 Stems, bessere Qualität |
| | `htdemucs_6s` | 6 Stems (+ Gitarre, Klavier) |
| | `mdx_extra` | 4 Stems, bessere Vocals |
| **Shifts** | 0 / 5 / 10 | Qualität, kostet Zeit |
| **Overlap** | 0.25 / 0.5 / 0.75 | Weniger Artefakte bei höherem Wert |

Nach Änderungen → **↺ Neu starten** klicken. Der Watchdog bemerkt den Shutdown und startet mit neuer Konfiguration.

> Beim ersten Start eines neuen Modells lädt Demucs die Gewichte herunter (80–300MB).

### Watchdog und Config-File

Der Watchdog liest `~/demucs_config.json`:
```json
{"model":"htdemucs","shifts":0,"overlap":0.25,"port":5001}
```
Der Analyzer schreibt diese Datei beim Klick auf **↺ Neu starten**.

---

## Einschränkungen bei GitHub Pages

| Feature | Lokal | GitHub Pages |
|---|---|---|
| Song-Analyse, Spektrogramm, BPM | ✓ | ✓ |
| Instrument-Erkennung (Essentia) | ✓ | ✓ |
| Suno-Metadaten (Plays, Likes) | ✓ | ✗ |
| Lyrics-Extraktion | ✓ | ✗ |
| Stem-Trennung (Demucs) | ✓ | ✗ |

---

## Features

**Analyse:** Spektrogramm, Stereo-Spektrogramm, BPM-Kurve, Tonart/Modus, Dynamik, Stimmanalyse, Pitch, Harmonische Dichte, Inharmonizität, Spektraler Tilt, Onset-Erkennung

**Instrument-Erkennung:** Essentia MTG Jamendo (40 Klassen, Top-10, ONNX im Browser)

**Stem-Trennung:** 4 oder 6 Stems, synchrone Wellenformen mit Zoom und Playhead, Mute pro Stem, Download als MP3

**UI:** Zoom, synchroner Playhead, Kommentar-Generator, Suno-Metadaten (lokal)

---

## Modell-Dateien (`models/`)

- `discogs-effnet-bsdynamic-1.onnx` — Embedding-Modell (~18MB)
- `mtg_jamendo_instrument-discogs-effnet-1.onnx` — Instrument-Klassifikator (~2.6MB)
- `mtg_jamendo_instrument-discogs-effnet-1.json` — Labels

Quelle: [essentia.upf.edu](https://essentia.upf.edu/models/) — Music Technology Group, UPF Barcelona

---

## Technologie

Web Audio API · Canvas 2D · Web Worker · ONNX Runtime Web · Demucs · Flask · Bash-Watchdog
