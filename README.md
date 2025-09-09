# TestSuite System

Ein umfassendes Bewertungssystem für verschiedene Arten von KI-Modellen, das OpenAI-kompatible APIs für alle Interaktionen verwendet. Das System ist speziell für den Einsatz in Unternehmensumgebungen konzipiert und stellt sicher, dass alle API-Anwendungen intern bleiben.

## Übersicht

Das TestSuite System evaluiert vier Haupttypen von KI-Modellen:

1. **Allgemeine LLMs** - Textgenerierung, Wissen und logisches Denken
2. **Coding Models** - Codegenerierung und Debugging-Fähigkeiten
3. **Audio Models** - Transkription, Übersetzung und Zusammenfassung
4. **Vision Language Models (VLM)** - Multimodale Verarbeitung von Text, Audio und Bildern

## Installation

### Voraussetzungen

- **Python**: 3.9 oder höher (empfohlen)
- **OpenAI-kompatible APIs**: Lokal betriebene On-Prem APIs
- **Betriebssystem**: Windows 10/11, Linux oder macOS
- **Hardware**:
  - CPU: Mehrkernprozessor empfohlen
  - RAM: Minimum 8GB, 16GB+ für Audioverarbeitung
  - Speicher: Minimum 1GB freier Speicher

### Abhängigkeiten installieren

Das System verwendet moderne Python-Abhängigkeiten und kann mit `pip` oder `uv` installiert werden:

**Mit pip:**
```bash
pip install -e .
```

**Mit uv (empfohlen):**
```bash
uv sync
```

### Konfiguration

1. Kopiere die Beispielkonfigurationsdatei:
```bash
cp config.env.example config.env
```

2. Bearbeite `config.env` und trage deine API-Schlüssel und Endpunkte ein:
```bash
# Multi-LLM Konfiguration (JSON Format)
LLM_MODELS="{\"local-gpt-3.5\": \"http://localhost:8001/v1\", \"local-gpt-4\": \"http://localhost:8001/v1\"}"

# Coding-spezifische LLM Konfiguration
CODING_LLM_MODELS="{\"local-coder\": \"http://localhost:8004/v1\"}"

# VLM-spezifische LLM Konfiguration
VLM_LLM_MODELS="{\"local-vision\": \"http://localhost:8005/v1\"}"

# Whisper API Konfiguration
WHISPER_API_KEY=dein_whisper_api_hier
WHISPER_API_BASE_URL=http://localhost:8002/v1

# Voxtral API Konfiguration
VOXTRAL_API_KEY=dein_voxtral_api_hier
VOXTRAL_API_BASE_URL=http://localhost:8110/v1

# Vision API Konfiguration
VISION_API_KEY=dein_vision_api_hier
VISION_API_BASE_URL=http://localhost:8003/v1

# Bewertung LLM Konfiguration
EVALUATION_API_KEY=dein_evaluation_api_hier
EVALUATION_API_BASE_URL=http://localhost:8001/v1

# System Konfiguration
LOG_LEVEL=INFO
RESULTS_DIR=data/results
MAX_TEST_DURATION=300
SIMILARITY_THRESHOLD=0.7
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

### Erweiterte Optionen

```bash
python main.py --suite all --verbose --save-results --output results.json --format json
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

- `--format, -f`: Ausgabeformat der Ergebnisse
  - `json`: JSON Format (Standard)
  - `yaml`: YAML Format

### Umgebungsvariablen

Das System unterstützt folgende Umgebungsvariablen:

```bash
# Logging
LOG_LEVEL=DEBUG

# Ergebnisse
RESULTS_DIR=custom_results
MAX_TEST_DURATION=600

# Bewertung
SIMILARITY_THRESHOLD=0.75
```

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

### Test Suite Konfiguration

Jede Test Suite kann individuell konfiguriert werden:

```python
# Beispiel für die Konfiguration einer Test Suite
from test_suites import GeneralLLMTestSuite

suite = GeneralLLMTestSuite()
suite.setup_suite()  # Voraussetzungen prüfen
results = suite.run_all_tests()  # Tests ausführen
summary = suite.get_suite_summary()  # Ergebnisse zusammenfassen
```

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

### Bewertungsmetriken im Detail

#### Textvergleich
- **Cosine Similarity**: Messung der semantischen Ähnlichkeit
- **BLEU Score**: Bewertung von Übersetzungsqualität
- **ROUGE Score**: Bewertung von Zusammenfassungsqualität

#### Code-Bewertung
- **Funktionalitätstests**: Automatische Testfall-Validierung
- **Code-Analyse**: Syntax- und Logikprüfung
- **Sicherheit**: Sandboxed Code-Ausführung

#### Audio-Bewertung
- **Transkriptionsgenauigkeit**: Wort-für-Wort Vergleich
- **Übersetzungsqualität**: Kontextbezogene Bewertung
- **Zusammenfassungsrelevanz**: Schlüsselpunkterkennung

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

### Ergebnisinterpretation

- **Erfolgsrate**: Prozentsatz der bestandenen Tests
- **Durchschnittlicher Score**: Gesamtbewertung aller Tests (0.0 - 1.0)
- **Status**:
  - `completed`: Suite erfolgreich ausgeführt
  - `failed`: Suite mit Fehlern abgeschlossen
  - `error`: Suite aufgrund von Fehlern nicht ausgeführt

### Berichterstattung

Das System generiert automatisch verschiedene Berichte:

- **JSON-Berichte**: Strukturierte Daten für weitere Verarbeitung
- **Text-Berichte**: Menschlich lesbare Zusammenfassungen
- **PDF-Berichte**: Formatierte Berichte für die Präsentation

## API-Integration

### Unterstützte Dienste

- **LLM API**: Textgenerierung (GPT-3.5, GPT-4, kompatible)
- **Whisper API**: Audioverarbeitung (Whisper, kompatible)
- **Vision API**: Bildverarbeitung (GPT-4-Vision, kompatible)
- **Voxtral API**: Spezialisierte Audioverarbeitung

### On-Prem API-Unterstützung

Das System ist speziell für den Einsatz mit lokal betriebenen APIs konzipiert:

- **Alle Anwendungen bleiben intern** im Unternehmen
- **Keine Datenexternung** an externe Dienste wie OpenAI
- **Unternehmensspezifische Endpunkte** werden unterstützt
- **Multi-Model Konfiguration** für verschiedene lokale Modelle

### Fehlerbehandlung

- **Automatische Wiederholung**: Bis zu 3 Versuche bei API-Fehlern
- **Graceful Degradation**: System bleibt bei Dienstunverfügbarkeit stabil
- **Detaillierte Protokollierung**: Vollständige Fehleraufzeichnung
- **Timeout-Handhabung**: Konfigurierbare Timeouts für alle API-Aufrufe
- **Rate Limiting**: Automatische Anpassung bei API-Limits

### API-Konfiguration

```python
# Beispiel für die API-Konfiguration
from config import key_manager

# Hole API-Details für einen Dienst
api_key = key_manager.get_key("llm", "local-gpt-4")
base_url = key_manager.get_base_url("llm", "local-gpt-4")
model = key_manager.get_model("llm", "local-gpt-4")

# Verfügbare Modelle auflisten
available_models = key_manager.get_available_models("llm")
```

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
├── pyproject.toml         # Projektmetadaten und Abhängigkeiten
├── requirements.md        # Technische Anforderungen
└── README.md              # Diese Datei
```

### Entwicklungsumgebung einrichten

```bash
# Entwicklungsumgebung mit uv
uv sync --dev

# Oder mit pip
pip install -e ".[dev]"

# Pre-commit Hooks einrichten
pre-commit install
```

### Erweitern des Systems

#### Neue Test Suite hinzufügen

1. Erbe von [`BaseTestSuite`](test_suites/base_suite.py:12)
2. Implementiere [`run_all_tests()`](test_suites/base_suite.py:24) und [`get_test_description()`](test_suites/base_suite.py:29)
3. Füge die Suite zum Orchestrator hinzu

```python
from test_suites.base_suite import BaseTestSuite

class MyCustomTestSuite(BaseTestSuite):
    def __init__(self):
        super().__init__("my_custom_suite")
    
    def run_all_tests(self):
        # Implementiere deine Tests hier
        pass
    
    def get_test_description(self):
        return "Meine benutzerdefinierte Test Suite"
```

#### Neue Bewertungsmetriken hinzufügen

1. Erweitere [`TextComparator`](core/evaluator.py:101) in [`evaluator.py`](core/evaluator.py:1)
2. Implementiere neue Vergleichsmethoden
3. Integriere die Metriken in die Bewertungsfunktionen

```python
class TextComparator:
    @staticmethod
    def my_custom_metric(text1: str, text2: str) -> float:
        # Implementiere deine benutzerdefinierte Metrik
        return 0.0
```

### Code-Qualität

Das Projekt verwendet moderne Entwicklungstools:

- **Black**: Code-Formatierung
- **Flake8**: Code-Linting
- **MyPy**: Typ-Prüfung
- **Pytest**: Unit-Tests
- **Ruff**: Performanter Linter und Formatter

### Testing

```bash
# Alle Tests ausführen
pytest

# Tests mit Coverage
pytest --cov=testsuite

# Spezifische Test Suite testen
pytest test_suites/test_general_llm.py
```

## Troubleshooting

### Häufige Probleme

1. **API-Schlüssel ungültig**
   - Überprüfe die Konfigurationsdatei [`config.env`](config.env.example:1)
   - Stelle sicher, dass die API-Schlüssel gültig sind
   - Prüfe die Netzwerkverbindung zu den lokalen Endpunkten

2. **Netzwerkprobleme**
   - Überprüfe die Internetverbindung zu den lokalen APIs
   - Teste die API-Endpunkte manuell
   - Prüfe Firewall-Einstellungen

3. **Audio/Dateifehler**
   - Stelle sicher, dass die Testdateien existieren
   - Überprüfe Dateiformate und Berechtigungen
   - Prüfe Audio-Treiber unter Windows

4. **Python-Abhängigkeiten**
   - Installiere alle erforderlichen Pakete mit `uv sync`
   - Überprüfe Python-Version (3.9+)
   - Aktualisiere pip: `pip install --upgrade pip`

5. **Modellverfügbarkeit**
   - Stelle sicher, dass die lokalen Modelle laufen
   - Prüfe die Basis-URLs in der Konfiguration
   - Überprüfe Modellverfügbarkeit mit API-Tools

### Debug-Modus

Aktiviere ausführliche Protokollierung:
```bash
python main.py --verbose
```

### Diagnose-Tools

```bash
# Umgebung validieren
python -c "from config import config; print('Konfiguration geladen')"

# Test Suite Voraussetzungen prüfen
python -c "from core.orchestrator import orchestrator; print(orchestrator.validate_environment())"

# Einzelne Test Suite debuggen
python main.py --suite general_llm --verbose
```

### Logging

Das System generiert detaillierte Log-Dateien:

- **System-Logs**: `data/results/logs/`
- **Test-Suite-Logs**: Pro Suite separate Log-Dateien
- **API-Logs**: Alle API-Aufrufe werden protokolliert

Log-Level können konfiguriert werden:
```bash
LOG_LEVEL=DEBUG python main.py
```

## Lizenz

Dieses Projekt ist unter der MIT-Lizenz lizenziert. Siehe [`LICENSE`](LICENSE:1) für weitere Details.

## Support

Für Fragen und Unterstützung:

- **Dokumentation**: Lesen Sie diese README und die technischen Anforderungen in [`requirements.md`](requirements.md:1)
- **Fehlerprotokolle**: Prüfen Sie die Log-Dateien im `data/results/` Verzeichnis

## Changelog

### Version 1.0.0
- Initial release mit vollständiger Test Suite Unterstützung
- Multi-Model API Konfiguration
- On-Prem API Unterstützung
- Verbesserte Fehlerbehandlung und Logging
- Automatische Berichterstattung