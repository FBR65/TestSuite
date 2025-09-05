"""
Haupt Test Orchestrator für das TestSuite System
"""
import time
import threading
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import yaml
from pathlib import Path

from config import config
from core.logger import get_suite_logger
from test_suites import (
    GeneralLLMTestSuite,
    CodingModelTestSuite, 
    AudioModelTestSuite,
    VLMTestSuite
)

class TestSuiteOrchestrator:
    """Haupt Orchestrator für die Test Suite Ausführung"""
    
    def __init__(self):
        self.test_suites = {
            "general_llm": GeneralLLMTestSuite(),
            "coding_model": CodingModelTestSuite(),
            "audio_model": AudioModelTestSuite(),
            "vlm": VLMTestSuite()
        }
        self.execution_results = {}
        self._lock = threading.Lock()
        self._stop_execution = False
    
    def validate_environment(self, suites_to_validate: List[str] = None) -> Dict[str, bool]:
        """Validiere die Testumgebung für spezifische Suiten"""
        validation_results = {}
        
        if suites_to_validate is None:
            suites_to_validate = list(self.test_suites.keys())
        
        print("Validiere Testumgebung...")
        
        for suite_name in suites_to_validate:
            if suite_name not in self.test_suites:
                continue
                
            suite = self.test_suites[suite_name]
            try:
                validation_results[suite_name] = suite.validate_prerequisites()
                status = "OK" if validation_results[suite_name] else "FAIL"
                print(f"  {suite_name}: {status}")
            except Exception as e:
                validation_results[suite_name] = False
                print(f"  {suite_name}: FAIL - Fehler: {e}")
        
        all_valid = all(validation_results.values())
        print(f"\nGesamtstatus: {'OK Alle Voraussetzungen erfüllt' if all_valid else 'FAIL Einige Voraussetzungen nicht erfüllt'}")
        
        return validation_results
    
    def setup_environment(self) -> None:
        """Richte die Testumgebung ein"""
        print("Richte Testumgebung ein...")
        
        # Erstelle Ergebnisse Verzeichnis
        results_dir = Path(config.test_config.results_dir)
        results_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup aller Test Suiten
        for suite_name, suite in self.test_suites.items():
            try:
                suite.setup_suite()
                print(f"  {suite_name}: SETUP ERFOLGREICH")
            except Exception as e:
                print(f"  {suite_name}: SETUP FEHLGESCHLAGEN - {e}")
    
    def run_single_suite(self, suite_name: str) -> Dict[str, Any]:
        """Führe eine einzelne Test Suite aus"""
        if suite_name not in self.test_suites:
            raise ValueError(f"Unbekannte Test Suite: {suite_name}")
        
        suite = self.test_suites[suite_name]
        
        print(f"\n{'='*60}")
        print(f"Starte Test Suite: {suite_name}")
        print(f"Beschreibung: {suite.get_test_description()}")
        print(f"Modell: {getattr(suite, 'model', 'N/A')}")
        print(f"{'='*60}")
        
        start_time = time.time()
        
        try:
            # Führe Tests aus
            results = suite.run_suite_with_setup()
            
            # Hole Suite Zusammenfassung
            summary = suite.get_suite_summary()
            
            duration = time.time() - start_time
            
            # Bestimme den Status basierend auf den Test-Ergebnissen
            if summary['passed'] == summary['total_tests']:
                suite_status = "completed"
            else:
                suite_status = "failed"
            
            result_data = {
                "suite_name": suite_name,
                "start_time": datetime.now().isoformat(),
                "duration": duration,
                "summary": summary,
                "results_count": len(results),
                "status": suite_status
            }
            
            print(f"\nTest Suite {suite_name} abgeschlossen:")
            print(f"  - Dauer: {duration:.2f} Sekunden")
            print(f"  - Tests: {summary['total_tests']}")
            print(f"  - Erfolgreich: {summary['passed']}")
            print(f"  - Fehlgeschlagen: {summary['failed']}")
            print(f"  - Fehler: {summary['errors']}")
            print(f"  - Durchschnittlicher Score: {summary['average_score']:.2f}")
            
            return result_data
        
        except Exception as e:
            duration = time.time() - start_time
            print(f"\nTest Suite {suite_name} fehlgeschlagen: {e}")
            
            return {
                "suite_name": suite_name,
                "start_time": datetime.now().isoformat(),
                "duration": duration,
                "error": str(e),
                "status": "failed"
            }
    
    def run_all_suites(self, suite_order: List[str] = None) -> Dict[str, Any]:
        """Führe alle Test Suiten aus"""
        if suite_order is None:
            suite_order = list(self.test_suites.keys())
        
        print(f"\n{'='*80}")
        print("START DES TESTSUITE SYSTEMS")
        print(f"{'='*80}")
        print(f"Startzeit: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Anzahl Test Suiten: {len(suite_order)}")
        print(f"Reihenfolge: {' -> '.join(suite_order)}")
        print(f"{'='*80}")
        
        # Validiere Umgebung
        validation_results = self.validate_environment(suite_order)
        if not all(validation_results.values()):
            print("\n⚠️  Nicht alle Voraussetzungen sind erfüllt. Einige Tests könnten fehlschlagen.")
        
        # Setup Umgebung
        self.setup_environment()
        
        # Führe Test Suiten aus
        overall_start_time = time.time()
        self.execution_results = {}
        
        for suite_name in suite_order:
            if self._stop_execution:
                print("\n⚠️  Ausführung wurde gestoppt")
                break
            
            print(f"\n{'-'*60}")
            print(f"NACHSTE TEST SUITE: {suite_name.upper()}")
            print(f"{'-'*60}")
            
            suite_result = self.run_single_suite(suite_name)
            self.execution_results[suite_name] = suite_result
            
            # Kurze Pause zwischen den Suiten
            time.sleep(1)
        
        overall_duration = time.time() - overall_start_time
        
        # Erstelle Gesamtergebnis
        overall_result = self._create_overall_result(overall_duration)
        
        print(f"\n{'='*80}")
        print("TESTSUITE AUSFÜHRUNG ABGESCHLOSSEN")
        print(f"{'='*80}")
        print(f"Endzeit: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Gesamtdauer: {overall_duration:.2f} Sekunden")
        
        # Zeige Gesamtergebnis
        self._display_overall_result(overall_result)
        
        return overall_result
    
    def run_specific_suite(self, suite_name: str) -> Dict[str, Any]:
        """Führe eine spezifische Test Suite aus"""
        return self.run_single_suite(suite_name)
    
    def stop_execution(self) -> None:
        """Stoppe die Ausführung"""
        self._stop_execution = True
        print("\n⚠️  Stoppe Ausführung...")
    
    def _create_overall_result(self, overall_duration: float) -> Dict[str, Any]:
        """Erstelle das Gesamtergebnis"""
        total_tests = 0
        total_passed = 0
        total_failed = 0
        total_errors = 0
        total_score = 0.0
        completed_suites = 0
        
        for suite_name, result in self.execution_results.items():
            if result["status"] == "completed":
                summary = result["summary"]
                total_tests += summary["total_tests"]
                total_passed += summary["passed"]
                total_failed += summary["failed"]
                total_errors += summary["errors"]
                total_score += summary["average_score"]
                completed_suites += 1
        
        average_score = total_score / completed_suites if completed_suites > 0 else 0.0
        
        overall_result = {
            "execution_info": {
                "start_time": next(iter(self.execution_results.values()), {}).get("start_time", datetime.now().isoformat()),
                "end_time": datetime.now().isoformat(),
                "overall_duration": overall_duration,
                "total_suites": len(self.test_suites),
                "completed_suites": completed_suites
            },
            "overall_summary": {
                "total_tests": total_tests,
                "total_passed": total_passed,
                "total_failed": total_failed,
                "total_errors": total_errors,
                "success_rate": (total_passed / total_tests * 100) if total_tests > 0 else 0,
                "average_score": average_score
            },
            "suite_results": self.execution_results,
            "detailed_results": []  # Ergebnisse werden direkt von den Test Suites geholt
        }
        
        return overall_result
    
    def _display_overall_result(self, overall_result: Dict[str, Any]) -> None:
        """Zeige das Gesamtergebnis an"""
        summary = overall_result["overall_summary"]
        execution_info = overall_result["execution_info"]
        
        print(f"\n{'='*60}")
        print("GESAMTERGEBNIS")
        print(f"{'='*60}")
        print(f"Ausführungszeit: {execution_info['overall_duration']:.2f} Sekunden")
        print(f"Test Suiten: {execution_info['completed_suites']}/{execution_info['total_suites']} abgeschlossen")
        print(f"{'='*60}")
        print(f"Gesamttests: {summary['total_tests']}")
        print(f"Erfolgreich: {summary['total_passed']}")
        print(f"Fehlgeschlagen: {summary['total_failed']}")
        print(f"Fehler: {summary['total_errors']}")
        print(f"Erfolgsrate: {summary['success_rate']:.1f}%")
        print(f"Durchschnittlicher Score: {summary['average_score']:.2f}")
        print(f"{'='*60}")
    
    def save_results(self, filename: str = None, format: str = "json") -> str:
        """Speichere die Ergebnisse in einer Datei"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"testsuite_results_{timestamp}.{format}"
        
        results_dir = Path(config.test_config.results_dir)
        filepath = results_dir / filename
        
        # Speichere detaillierte Ergebnisse nur wenn sie nicht leer sind
        if self.execution_results:
            if format == "json":
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(self.execution_results, f, ensure_ascii=False, indent=2, default=str)
            elif format == "yaml":
                with open(filepath, 'w', encoding='utf-8') as f:
                    yaml.dump(self.execution_results, f, default_flow_style=False, allow_unicode=True)
            print(f"\nErgebnisse gespeichert:")
            print(f"  - Detaillierte Ergebnisse: {filepath}")
        else:
            print(f"\nKeine detaillierten Ergebnisse zum Speichern vorhanden")
            return ""
        
        # Speichere Gesamtergebnis nur wenn es nicht leer ist
        overall_result = self._create_overall_result(0)  # Dauer wird im Logger gespeichert
        if overall_result and overall_result.get("overall_summary", {}).get("total_tests", 0) > 0:
            overall_filename = f"overall_{filename}"
            overall_filepath = results_dir / overall_filename
            
            if format == "json":
                with open(overall_filepath, 'w', encoding='utf-8') as f:
                    json.dump(overall_result, f, ensure_ascii=False, indent=2, default=str)
            elif format == "yaml":
                with open(overall_filepath, 'w', encoding='utf-8') as f:
                    yaml.dump(overall_result, f, default_flow_style=False, allow_unicode=True)
            print(f"  - Gesamtergebnis: {overall_filepath}")
        else:
            print(f"  - Kein Gesamtergebnis zum Speichern vorhanden")
        
        # Speichere Bericht nur wenn es Ergebnisse gibt
        # Berichte werden jetzt direkt von den Test Suites gespeichert
        print(f"  - Berichte werden direkt von den Test Suites gespeichert")
        
        return str(filepath)
    
    def get_progress(self) -> Dict[str, Any]:
        """Hole aktuellen Fortschritt"""
        return {
            "total_suites": len(self.test_suites),
            "completed_suites": len(self.execution_results),
            "current_suite": list(self.execution_results.keys())[-1] if self.execution_results else None,
            "stop_requested": self._stop_execution
        }

# Globale Orchestrator Instanz
orchestrator = TestSuiteOrchestrator()