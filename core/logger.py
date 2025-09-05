"""
Umfassendes Ergebnisdokumentationssystem
"""
import json
import yaml
import logging
import os
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path
import threading
from dataclasses import dataclass, asdict

# Importiere die Konfiguration
from config import config

@dataclass
class TestResult:
    """Datenklasse für Testergebnisse"""
    test_name: str
    test_type: str
    status: str  # "success", "failed", "error"
    start_time: datetime
    end_time: Optional[datetime] = None
    duration: Optional[float] = None
    input_data: Optional[Dict[str, Any]] = None
    output_data: Optional[Dict[str, Any]] = None
    expected_data: Optional[Dict[str, Any]] = None
    score: Optional[float] = None
    details: Optional[str] = None
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class TestSuiteLogger:
    """Umfassendes Logging System für Testergebnisse"""
    
    def _sanitize_text(self, text: str) -> str:
        """Sanitize text for console output while preserving Unicode characters"""
        if not isinstance(text, str):
            return text
        
        # Ersetze nur schmale Leerzeichen, behalte alle anderen Unicode-Zeichen
        import re
        # Ersetze schmale Leerzeichen durch normale Leerzeichen
        text = re.sub(r'[\u202f\u2009\u200a\u200b\u200c\u200d\u2060]', ' ', text)
        return text.strip()
    
    """Umfassendes Logging System für Testergebnisse"""
    
    def __init__(self, log_dir: str = "data/results", model_type: str = None):
        self.log_dir = Path(log_dir)
        self.model_type = model_type or "general_llm"
        # Create model-specific directory
        self.model_log_dir = self.log_dir / self.model_type
        self.model_log_dir.mkdir(parents=True, exist_ok=True)
        
        # Thread-sichere Ergebnisliste
        self._results = []
        self._lock = threading.Lock()
        
        # Setup Standard Logger
        self._setup_logger()
    
    def _setup_logger(self):
        """Setup des Standard Logging Systems"""
        # Erstelle einen einzigartigen Logger-Namen für diese Suite
        logger_name = f"core.logger.{self.model_type}"
        
        # Konfiguriere den Logger speziell für diese Suite
        self.logger = logging.getLogger(logger_name)
        self.logger.setLevel(getattr(logging, config.test_config.log_level))
        
        # Formatiere die Log-Nachrichten
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        # File Handler für diese Suite
        file_handler = logging.FileHandler(self.model_log_dir / "test_suite.log")
        file_handler.setFormatter(formatter)
        
        # Stream Handler für die Konsole
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        
        # Füge Handler zum Logger hinzu
        self.logger.addHandler(file_handler)
        self.logger.addHandler(stream_handler)
        
        # Verhindere, dass der Logger an den Root-Logger weiterleitet
        self.logger.propagate = False
    
    def log_test_start(self, test_name: str, test_type: str, input_data: Dict[str, Any] = None) -> TestResult:
        """Logge den Start eines Tests"""
        result = TestResult(
            test_name=test_name,
            test_type=test_type,
            status="running",
            start_time=datetime.now(),
            input_data=input_data or {}
        )
        
        with self._lock:
            self._results.append(result)
        
        sanitized_name = self._sanitize_text(test_name)
        sanitized_type = self._sanitize_text(test_type)
        self.logger.info(f"Test gestartet: {sanitized_name} ({sanitized_type})")
        return result
    
    def log_test_result(self, result: TestResult, output_data: Dict[str, Any] = None,
                       score: float = None, details: str = None, error_message: str = None,
                       input_data: Dict[str, Any] = None):
        """Logge das Ergebnis eines Tests"""
        result.end_time = datetime.now()
        result.duration = (result.end_time - result.start_time).total_seconds()
        result.output_data = output_data
        result.score = score
        result.details = details
        result.error_message = error_message
        result.input_data = input_data or {}
        
        # Only override status if it's still "running" or if there's an error
        if result.status == "running" or error_message:
            if error_message:
                result.status = "error"
                self.logger.error(f"Test fehlgeschlagen: {result.test_name} - {error_message}")
            else:
                # For coding tests, if score is 1.0, it should always be successful
                # regardless of the similarity threshold
                if score == 1.0:
                    result.status = "success"
                    self.logger.info(f"Test erfolgreich: {result.test_name} - Score: {score}")
                else:
                    # Bestimme den passenden Schwellenwert basierend auf dem Testtyp
                    threshold = self._get_threshold_for_test(result.test_name, score)
                    
                    # DEBUG: Log threshold information
                    self.logger.info(f"DEBUG: Test {result.test_name} - Score: {score}, Threshold: {threshold}")
                    
                    if score and score >= threshold:
                        result.status = "success"
                        self.logger.info(f"Test erfolgreich: {result.test_name} - Score: {score}")
                    else:
                        result.status = "failed"
                        self.logger.warning(f"Test nicht bestanden: {result.test_name} - Score: {score} (Schwellenwert: {threshold})")
        
        # Speichere Ergebnis in Datei
        self._save_result_to_file(result)
    
    def _get_threshold_for_test(self, test_name: str, score: float) -> float:
        """Bestimme den passenden Schwellenwert basierend auf dem Testtyp"""
        # Standard-Schwelle
        threshold = config.test_config.similarity_threshold
        
        # Passe die Schwelle an den Testtyp an
        if "summarization" in test_name.lower():
            # Für Zusammenfassungen ist ROUGE typischerweise viel niedriger
            # 0.3 ist eine realistischere Schwelle für ROUGE-L Scores
            threshold = 0.3
        elif "translation" in test_name.lower():
            # Für Übersetzungen ist BLEU typischerweise im mittleren Bereich
            # 0.5 ist eine realistischere Schwelle für BLEU Scores
            threshold = 0.5
        elif "transcription" in test_name.lower():
            # Für Transkriptionen ist Cosine similarity angemessen
            threshold = config.test_config.similarity_threshold
        
        return threshold
    
    def _save_result_to_file(self, result: TestResult, format: str = "json"):
        """Speichere einzelnes Ergebnis in Datei"""
        timestamp = result.start_time.strftime("%Y%m%d_%H%M%S")
        filename = f"{result.test_name}_{timestamp}.{format}"
        filepath = self.model_log_dir / filename
        
        # Convert result to dict and sanitize problematic Unicode characters
        result_dict = asdict(result)
        sanitized_dict = self._sanitize_dict_for_encoding(result_dict)
        
        if format == "json":
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(sanitized_dict, f, ensure_ascii=False, indent=2, default=str)
        elif format == "yaml":
            with open(filepath, 'w', encoding='utf-8') as f:
                yaml.dump(sanitized_dict, f, default_flow_style=False, allow_unicode=True)
    
    def _sanitize_dict_for_encoding(self, obj):
        """Recursively sanitize a dictionary for encoding"""
        if isinstance(obj, dict):
            return {key: self._sanitize_dict_for_encoding(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._sanitize_dict_for_encoding(item) for item in obj]
        elif isinstance(obj, str):
            return self._sanitize_text(obj)
        else:
            return obj
    
    def get_results(self) -> list[TestResult]:
        """Hole alle gespeicherten Ergebnisse"""
        with self._lock:
            return self._results.copy()
    
    def get_results_by_status(self, status: str) -> list[TestResult]:
        """Filtere Ergebnisse nach Status"""
        return [r for r in self.get_results() if r.status == status]
    
    def get_summary(self) -> Dict[str, Any]:
        """Erstelle eine Zusammenfassung aller Ergebnisse"""
        results = self.get_results()
        
        if not results:
            return {"total": 0, "success": 0, "failed": 0, "error": 0}
        
        summary = {
            "total": len(results),
            "success": len([r for r in results if r.status == "success"]),
            "failed": len([r for r in results if r.status == "failed"]),
            "error": len([r for r in results if r.status == "error"]),
            "average_score": sum(r.score for r in results if r.score is not None) / len([r for r in results if r.score is not None]) if any(r.score is not None for r in results) else 0,
            "total_duration": sum(r.duration for r in results if r.duration is not None)
        }
        
        return summary
    
    def generate_comprehensive_report(self) -> str:
        """Generiere einen umfassenden Testbericht"""
        results = self.get_results()
        summary = self.get_summary()
        
        report = []
        report.append("=" * 60)
        report.append("TESTSUITE KOMPREHENSIVER BERICHT")
        report.append("=" * 60)
        report.append(f"Generiert am: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Zusammenfassung
        report.append("ZUSAMMENFASSUNG")
        report.append("-" * 30)
        report.append(f"Gesamttests: {summary['total']}")
        report.append(f"Erfolgreich: {summary['success']}")
        report.append(f"Fehlgeschlagen: {summary['failed']}")
        report.append(f"Fehler: {summary['error']}")
        report.append(f"Durchschnittlicher Score: {summary['average_score']:.2f}")
        report.append(f"Gesamtdauer: {summary['total_duration']:.2f} Sekunden")
        report.append("")
        
        # Detaillierte Ergebnisse
        report.append("DETAILLIERTE ERGEBNISSE")
        report.append("-" * 30)
        
        for result in results:
            report.append(f"Test: {result.test_name}")
            report.append(f"Typ: {result.test_type}")
            report.append(f"Status: {result.status.upper()}")
            report.append(f"Dauer: {result.duration:.2f} Sekunden")
            if result.score is not None:
                report.append(f"Score: {result.score:.2f}")
            if result.error_message:
                report.append(f"Fehler: {result.error_message}")
            report.append("")
        
        return "\n".join(report)
    
    def save_report(self, filename: str = None, format: str = "json"):
        """Speichere den umfassenden Bericht in einer Datei"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"test_report_{timestamp}.{format}"
        
        filepath = self.model_log_dir / filename
        
        if format == "json":
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump({
                    "report": self.generate_comprehensive_report(),
                    "summary": self.get_summary(),
                    "results": [asdict(r) for r in self.get_results()]
                }, f, ensure_ascii=False, indent=2, default=str)
        elif format == "yaml":
            with open(filepath, 'w', encoding='utf-8') as f:
                yaml.dump({
                    "report": self.generate_comprehensive_report(),
                    "summary": self.get_summary(),
                    "results": [asdict(r) for r in self.get_results()]
                }, f, default_flow_style=False, allow_unicode=True)
        elif format == "txt":
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(self.generate_comprehensive_report())
        
        self.logger.info(f"Bericht gespeichert: {filepath}")

# Funktion zum Abrufen des globalen Loggers für eine bestimmte Test Suite
def get_suite_logger(suite_name: str) -> TestSuiteLogger:
    """Hole oder erstelle einen Logger für eine bestimmte Test Suite"""
    # Erstelle einen speziellen Logger für diese Suite
    suite_logger = TestSuiteLogger(log_dir="data/results", model_type=suite_name)
    return suite_logger

# Entferne den globalen Logger komplett - er wird nicht mehr verwendet
# Jede Test Suite verwendet ihren eigenen Logger über get_suite_logger()