"""
Haupt-Einstiegspunkt für das TestSuite System
"""
import sys
import argparse
import os
from pathlib import Path

# Füge das aktuelle Verzeichnis zum Python Path hinzu
sys.path.insert(0, str(Path(__file__).parent))

# NLTK Ressourcen vorbereiten
try:
    import nltk
    # Prüfe ob punkt_tab bereits vorhanden ist
    try:
        nltk.data.find('tokenizers/punkt_tab')
    except LookupError:
        print("Lade NLTK punkt_tab Ressource...")
        nltk.download('punkt_tab', quiet=True)
        print("NLTK punkt_tab Ressource erfolgreich geladen.")
except ImportError:
    print("NLTK nicht installiert. Installiere mit: pip install nltk")
except Exception as e:
    print(f"Fehler beim Laden der NLTK Ressourcen: {e}")

from core.orchestrator import orchestrator
from core import logger
from config import config

def main():
    """Hauptfunktion"""
    parser = argparse.ArgumentParser(description='TestSuite System - KI Modell Bewertung')
    parser.add_argument('--suite', '-s',
                       choices=['general_llm', 'coding_model', 'audio_model', 'vlm', 'all'],
                       default='all',
                       help='Welche Test Suite ausführen (default: all)')
    parser.add_argument('--order', '-O',
                       nargs='+',
                       choices=['general_llm', 'coding_model', 'audio_model', 'vlm'],
                       help='Ausführungsreihenfolge der Test Suiten')
    parser.add_argument('--config', '-c',
                       type=str,
                       help='Konfigurationsdatei laden')
    parser.add_argument('--results-dir', '-r',
                       type=str,
                       help='Verzeichnis für Ergebnisse')
    parser.add_argument('--verbose', '-v',
                       action='store_true',
                       help='Ausführliche Ausgabe')
    parser.add_argument('--save-results',
                       action='store_true',
                       help='Ergebnisse automatisch speichern')
    parser.add_argument('--output', '-o',
                       type=str,
                       help='Ausgabedatei für Ergebnisse')
    parser.add_argument('--format', '-f',
                       choices=['json', 'yaml'],
                       default='json',
                       help='Ausgabeformat der Ergebnisse (default: json)')
    
    args = parser.parse_args()
    
    print(f"{'='*80}")
    print("TESTSUITE SYSTEM")
    print(f"{'='*80}")
    print(f"Version: 1.0.0")
    print(f"Python: {sys.version}")
    print(f"{'='*80}")
    
    try:
        # Konfiguration anpassen
        if args.results_dir:
            config.test_config.results_dir = args.results_dir
        
        # Zeige Konfiguration
        if args.verbose:
            print(f"Konfiguration:")
            print(f"  - Ergebnisse Verzeichnis: {config.test_config.results_dir}")
            print(f"  - Logging Level: {config.test_config.log_level}")
            print(f"  - Ähnlichkeitsschwelle: {config.test_config.similarity_threshold}")
            print(f"  - Max Test Dauer: {config.test_config.max_test_duration}s")
            print()
        
        # Bestimme welche Test Suiten ausgeführt werden sollen
        if args.suite == 'all':
            suites_to_run = list(orchestrator.test_suites.keys())
            if args.order:
                # Filtere nur die angeforderten Suiten
                suites_to_run = [s for s in args.order if s in orchestrator.test_suites]
        else:
            suites_to_run = [args.suite]
        
        print(f"Auszuführende Test Suiten: {', '.join(suites_to_run)}")
        
        # Führe Test Suiten aus
        if len(suites_to_run) == 1:
            # Einzelne Suite
            result = orchestrator.run_specific_suite(suites_to_run[0])
        else:
            # Mehrere Suiten
            result = orchestrator.run_all_suites(suites_to_run)
        
        # Speichere Ergebnisse wenn angefordert
        if args.save_results or args.output:
            output_file = args.output or None
            saved_file = orchestrator.save_results(output_file, format=args.format)
            print(f"\nErgebnisse gespeichert in: {saved_file}")
        
        # Zeige Test-Ergebnisse
        if len(suites_to_run) == 1:
            suite_result = orchestrator.execution_results.get(suites_to_run[0])
            if suite_result and suite_result["status"] == "completed":
                summary = suite_result["summary"]
                print(f"Test Suite: {suites_to_run[0]}")
                print(f"Status: {'ERFOLGREICH' if summary['passed'] == summary['total_tests'] else 'FEHLGESCHLAGEN'}")
                print(f"Tests: {summary['total_tests']}")
                print(f"Erfolgreich: {summary['passed']}")
                print(f"Fehlgeschlagen: {summary['failed']}")
                print(f"Fehler: {summary['errors']}")
                print(f"Durchschnittlicher Score: {summary['average_score']:.2f}")
        else:
            # Gesamtergebnis
            total_tests = 0
            total_passed = 0
            total_failed = 0
            total_errors = 0
            
            for suite_name, suite_result in orchestrator.execution_results.items():
                if suite_result["status"] == "completed":
                    summary = suite_result["summary"]
                    total_tests += summary["total_tests"]
                    total_passed += summary["passed"]
                    total_failed += summary["failed"]
                    total_errors += summary["errors"]
                    print(f"  {suite_name}: {summary['passed']}/{summary['total_tests']} erfolgreich")
            
            print(f"\nGesamt:")
            print(f"  Tests: {total_tests}")
            print(f"  Erfolgreich: {total_passed}")
            print(f"  Fehlgeschlagen: {total_failed}")
            print(f"  Fehler: {total_errors}")
            print(f"  Erfolgsrate: {(total_passed/total_tests*100):.1f}%" if total_tests > 0 else "  Erfolgsrate: 0%")
        
        # Beende mit passendem Exit Code
        exit_code = 0 if all(r["status"] == "completed" for r in orchestrator.execution_results.values()) else 1
        sys.exit(exit_code)
        
    except KeyboardInterrupt:
        print(f"\n\n⚠️  Ausführung durch Benutzer abgebrochen")
        orchestrator.stop_execution()
        sys.exit(1)
        
    except Exception as e:
        print(f"\n\nKRITISCHER FEHLER: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()