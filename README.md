# TestSuite System

Ein umfassendes Bewertungssystem für verschiedene Arten von KI-Modellen, das OpenAI-kompatible APIs für alle Interaktionen verwendet.

## Übersicht

Das TestSuite System evaluiert vier Haupttypen von KI-Modellen:

1. **Allgemeine LLMs** - Textgenerierung, Wissen und logisches Denken
2. **Coding Models** - Codegenerierung und Debugging-Fähigkeiten
3. **Audio Models** - Transkription, Übersetzung und Zusammenfassung
4. **Vision Language Models (VLM)** - Multimodale Verarbeitung von Text, Audio und Bildern

## Installation

### Voraussetzungen

- Python 3.8 oder höher
- OpenAI-kompatible API-Schlüssel
- Stabile Internetverbindung

### Abhängigkeiten installieren

```bash
pip install openai python-dotenv requests pydub SpeechRecognition nltk scikit-learn numpy Pillow opencv-python
```

### Konfiguration

1. Kopiere die Beispielkonfigurationsdatei:
```bash
cp config.env.example config.env
```

2. Bearbeite `config.env` und trage deine API-Schlüssel ein:
```bash
LLM_API_KEY=dein_llm_api_hier
WHISPER_API_KEY=dein_whisper_api_hier
VISION_API_KEY=dein_vision_api_hier
VOXTRAL_API_KEY=dein_voxtral_api_hier
EVALUATION_API_KEY=dein_evaluation_api_hier
```

## Verwendung

### Grundlegende Ausführung

Führe alle Test Suiten aus:
```bash
python main.py
```

### Spezifische Test Suite ausführen

```bash
python main.py --suite general_llm
python main.py --suite coding_model
python main.py --suite audio_model
python main.py --suite vlm
```

### Benutzerdefinierte Ausführungsreihenfolge

```bash
python main.py --order general_llm coding_model audio_model vlm
```

### Optionen

```bash
python main.py --suite all --verbose --save-results --output results.json
```

#### Optionen im Detail:

- `--suite, -s`: Welche Test Suite ausführen
  - `general_llm`: Allgemeine LLM Tests
  - `coding_model`: Coding Model Tests
  - `audio_model`: Audio Model Tests
  - `vlm`: Vision Language Model Tests
  - `all`: Alle Test Suiten (Standard)

- `--order, -o`: Ausführungsreihenfolge der Test Suiten

- `--config, -c`: Konfigurationsdatei laden

- `--results-dir, -r`: Verzeichnis für Ergebnisse

- `--verbose, -v`: Ausführliche Ausgabe

- `--save-results`: Ergebnisse automatisch speichern

- `--output, -o`: Ausgabedatei für Ergebnisse

## Test Suiten

### 1. Allgemeine LLM Tests

Evaluieren Textgenerierung, Wissen und logisches Denken:

- **Wirtschaftswissen**: Bewertung von Energiepolitik-Kenntnissen
- **Biologiekenntnisse**: Evolutionäre Biologie und Genetik
- **Logisches Denken**: Mathematische Probleme
- **Kreativität**: Theaterstück-Entwicklung
- **Ethik**: Ausgewogene Argumentation
- **Sicherheit**: Refusal gefährlicher Anfragen

### 2. Coding Model Tests

Bewerten Codegenerierung und Debugging:

- **Python arithmetisches Mittel**: Funktion zur Mittelwertberechnung
- **JavaScript Debugging**: Analyse von "Endlosschleife"
- **Python String Operationen**: Wortzählfunktion
- **Python List Operationen**: Maximum-Funktion

### 3. Audio Model Tests

Evaluieren Audioverarbeitung mit Voxtral API:

- **Transkription**: Audio/1.wav → Textvergleich mit 1.txt
- **Übersetzung**: Audio/2.wav → Deutsch → Vergleich mit 2.txt
- **Zusammenfassung**: Audio/3.mp3 → Zusammenfassung → Vergleich mit 3.txt
- **Multimodale Analyse**: Kombinierte Audioanalyse
- **Qualitätsrobustheit**: Test mit verschiedenen Audioformaten

### 4. Vision Language Model Tests

Umfassende multimodale Tests:

- **Dokumentenanalyse**: Bild/1.png → Chemieanalyse
- **Datenextraktion**: Bild/2.JPG → Technische Daten
- **Kreative Geschichtenerstellung**: Bild/3.png → Geschichte
- **Multimodale Integration**: Kombinierte Text/Audio/Bild-Analyse
- **Umfassende VLM Bewertung**: Finale Integration aller Aufgaben

## Bewertungssystem

### Primäre Bewertung

- **Textähnlichkeit**: Cosine Similarity, BLEU, ROUGE
- **Code-Funktionalität**: Ausführung und Testfall-Validierung
- **Audioqualität**: Transkriptions- und Übersetzungsgenauigkeit

### Sekundäre Bewertung

Jede Bewertung wird durch ein anderes LLM validiert, um Objektivität zu gewährleisten:

- **Primäre Bewertung**: Automatische Metriken
- **Sekundäre Bewertung**: Manuelle Bewertung durch LLM
- **Kombiniertes Ergebnis**: Gewichtete Durchschnittsbewertung

## Ergebnisse

### Speicherort

Alle Ergebnisse werden im `data/results/` Verzeichnis gespeichert:

- **Detaillierte Ergebnisse**: `testsuite_results_YYYYMMDD_HHMMSS.json`
- **Gesamtergebnis**: `overall_testsuite_results_YYYYMMDD_HHMMSS.json`
- **Bericht**: `report_testsuite_results_YYYYMMDD_HHMMSS.txt`

### Ergebnisformat

```json
{
  "execution_info": {
    "start_time": "2024-01-01T10:00:00",
    "end_time": "2024-01-01T10:30:00",
    "overall_duration": 1800.0,
    "total_suites": 4,
    "completed_suites": 4
  },
  "overall_summary": {
    "total_tests": 20,
    "total_passed": 15,
    "total_failed": 3,
    "total_errors": 2,
    "success_rate": 75.0,
    "average_score": 0.82
  },
  "suite_results": {
    "general_llm": {
      "summary": {
        "total_tests": 6,
        "passed": 5,
        "failed": 1,
        "errors": 0,
        "average_score": 0.85
      }
    }
  }
}
```

## API-Integration

### Unterstützte Dienste

- **LLM API**: Textgenerierung (GPT-3.5, GPT-4, kompatible)
- **Whisper API**: Audioverarbeitung (Whisper, kompatible)
- **Vision API**: Bildverarbeitung (GPT-4-Vision, kompatible)
- **Voxtral API**: Spezialisierte Audioverarbeitung

### Fehlerbehandlung

- Automatische Wiederholung bei API-Fehlern
- Graceful Degradation bei Dienstunverfügbarkeit
- Detaillierte Fehlerprotokollierung
- Timeout-Handhabung

## Entwicklung

### Projektstruktur

```
TestSuite/
├── config/                 # Konfiguration
│   ├── __init__.py
│   ├── settings.py        # Systemeinstellungen
│   └── api_keys.py        # API-Schlüsselverwaltung
├── core/                  # Kernkomponenten
│   ├── __init__.py
│   ├── orchestrator.py    # Hauptorchestrator
│   ├── logger.py          # Logging-System
│   └── evaluator.py       # Bewertungsmaschine
├── test_suites/           # Test Suiten
│   ├── __init__.py
│   ├── base_suite.py      # Basisklasse
│   ├── general_llm.py     # Allgemeine LLM Tests
│   ├── coding_model.py    # Coding Model Tests
│   ├── audio_model.py     # Audio Model Tests
│   └── vlm_suite.py       # VLM Tests
├── data/                  # Testdaten
│   ├── Audio/             # Audiodateien
│   └── Bild/              # Bilddateien
├── main.py                # Haupt-Einstiegspunkt
├── config.env.example     # Konfigurationsvorlage
└── README.md              # Diese Datei
```

### Erweitern des Systems

#### Neue Test Suite hinzufügen

1. Erbe von `BaseTestSuite`
2. Implementiere `run_all_tests()` und `get_test_description()`
3. Füge die Suite zum Orchestrator hinzu

#### Neue Bewertungsmetriken hinzufügen

1. Erweitere `TextComparator` in `evaluator.py`
2. Implementiere neue Vergleichsmethoden
3. Integriere die Metriken in die Bewertungsfunktionen

## Troubleshooting

### Häufige Probleme

1. **API-Schlüssel ungültig**
   - Überprüfe die Konfigurationsdatei
   - Stelle sicher, dass die API-Schlüssel gültig sind

2. **Netzwerkprobleme**
   - Überprüfe die Internetverbindung
   - Teste die API-Endpunkte manuell

3. **Audio/Dateifehler**
   - Stelle sicher, dass die Testdateien existieren
   - Überprüfe Dateiformate und Berechtigungen

4. **Python-Abhängigkeiten**
   - Installiere alle erforderlichen Pakete
   - Überprüfe Python-Version (3.8+)

### Debug-Modus

Aktiviere ausführliche Protokollierung:
```bash
python main.py --verbose
```

## Lizenz

Dieses Projekt ist Teil des TestSuite Systems.

## Support

Für Fragen und Unterstützung:
- Überprüfe die Dokumentation
- Prüfe die Fehlerprotokolle
- Kontaktiere das Entwicklungsteam