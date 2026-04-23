# Suno Audio Analyzer

Ein Browser-Tool zur detaillierten Analyse von Suno-Songs. Keine Installation nötig für die Grundfunktionen — einfach die HTML-Datei öffnen.

---

## Was der Analyzer kann

### Analyse-Charts

Alle Charts zoomen synchron und haben einen laufenden Playhead der mit dem Player synchronisiert ist.

**Lautheit & Dynamik**
- LUFS-Kurve — subjektive Lautheit über Zeit (EBU R128-ähnlich)
- Energie-Hüllkurve — RMS-Amplitude über Zeit
- Crestfaktor — Verhältnis Peak zu RMS, zeigt Kompression
- Dynamikumfang — wie viel Spielraum zwischen leise und laut

**Rhythmus & Struktur**
- Onset-Erkennung — Einsätze/Anschläge über Zeit (gut für Drums, Gitarre)
- BPM-Kurve — Tempo über Zeit, erkennt Tempowechsel
- Song-Struktur — automatische Segmentierung in Sektionen (Intro, Verse, Chorus...)

**Klang & Harmonie**
- Spektrogramm — Frequenzverteilung über Zeit (logarithmisch)
- Stereo-Spektrogramm — L/R Kanalbalance über Zeit
- Chroma — harmonische Energie pro Tonklasse (C, D, E...)
- Spektraler Tilt — Verhältnis Bass zu Höhen
- Spektral-Centroid — "Helligkeit" des Klangs in Hz
- Harmonische Dichte — wie viel harmonisches Material vorhanden ist
- Inharmonizität — wie stark Obertöne von idealen Verhältnissen abweichen
- Spektrale Entropie — Komplexität des Frequenzspektrums
- Pitch-Kurve — dominante Tonhöhe über Zeit

**Stimme**
- Stimmcharakter — automatische Einschätzung männlich/weiblich
- Vokal-Aktivität — wann wird gesungen

### Metadaten (nur lokal oder mit laufendem Demucs-Server)
Plays, Likes, Kommentare, Alter, Plays/Tag, Modell, Artwork, Lyrics, Style-Tags

### Instrument-Erkennung (Essentia MTG)
KI-basierte Erkennung von bis zu 40 Instrument-Klassen aus dem Jamendo-Datensatz. Zeigt die 10 dominantesten Instrumente als Zeitleiste. Läuft direkt im Browser.

### Kommentar-Generator
Erstellt einen Prompt für ein LLM (ChatGPT, Claude etc.) der alle Analyse-Daten enthält — zum Schreiben eines informierten Suno-Community-Kommentars.

---

## Stem-Trennung (Demucs)

Trennt den Song in einzelne Spuren: Gesang, Drums, Bass, Rest (optional + Gitarre und Klavier).

### Einmalige Installation

```bash
python3 -m venv ~/demucs-env
source ~/demucs-env/bin/activate
pip install demucs flask
```

### Server starten

**Empfohlen — mit Watchdog** (startet automatisch neu bei Konfigurationsänderung):
```bash
bash ~/demucs_watchdog.sh
```

**Alternativ — direkt:**
```bash
source ~/demucs-env/bin/activate
python3 ~/demucs_server.py
```

Server läuft auf `http://localhost:5001`. Der Analyzer erkennt ihn automatisch.

### Qualitäts-Einstellungen

| Einstellung | Optionen | Bedeutung |
|---|---|---|
| **Modell** | `htdemucs` | 4 Stems, schnell (Standard) |
| | `htdemucs_ft` | 4 Stems, bessere Qualität |
| | `htdemucs_6s` | 6 Stems (+ Gitarre, Klavier) |
| | `mdx_extra` | 4 Stems, bessere Vocals |
| **Shifts** | 0 / 5 / 10 | Höher = besser, aber deutlich langsamer |
| **Overlap** | 0.25 / 0.5 / 0.75 | Höher = weniger Artefakte an Übergängen |

Nach Änderung → **↺ Neu starten**. Der Watchdog liest die neue Konfiguration und startet automatisch.

> Beim ersten Start eines neuen Modells lädt Demucs die Gewichte herunter (80–300MB je nach Modell).

### Stem-Player
- Alle Stems laufen synchron
- Klick auf Wellenform → Sprung zu Position
- Mute-Button pro Stem (Beschriftung durchgestrichen = stumm)
- Download pro Stem als MP3
- Haupt-Player und Stem-Player pausieren sich gegenseitig

---

## Einschränkungen je nach Nutzungsart

| Feature | Lokal (Datei öffnen) | GitHub Pages | GitHub Pages + Server |
|---|---|---|---|
| Alle Analyse-Charts | ✓ | ✓ | ✓ |
| Instrument-Erkennung | ✓ | ✓ | ✓ |
| Suno-Metadaten & Lyrics | ✓ | ✗ | ✓ |
| Stem-Trennung | ✓ | ✗ | ✓ |

**Lokal** = `suno_analyzer.html` direkt im Browser öffnen (Datei → Öffnen)  
**GitHub Pages** = `https://caspardavi.github.io/suno-analyzer/suno_analyzer.html`  
**+ Server** = Demucs-Server läuft lokal, Analyzer läuft über GitHub Pages

---

## Modell-Dateien (`models/`)

- `discogs-effnet-bsdynamic-1.onnx` — Discogs Effnet Embedding-Modell (~18MB)
- `mtg_jamendo_instrument-discogs-effnet-1.onnx` — Instrument-Klassifikator (~2.6MB)
- `mtg_jamendo_instrument-discogs-effnet-1.json` — Klassen-Labels

Quelle: [essentia.upf.edu](https://essentia.upf.edu/models/) — Music Technology Group, UPF Barcelona, MIT-Lizenz

---

## Technologie

Web Audio API · Canvas 2D · Web Worker · ONNX Runtime Web · Demucs (Meta) · Flask · Bash-Watchdog
