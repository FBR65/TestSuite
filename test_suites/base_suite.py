"""
Basisklasse für alle Test Suiten
"""
import time
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime

from core import logger, evaluator, TestResult
from config import config

class BaseTestSuite(ABC):
    """Abstrakte Basisklasse für alle Test Suiten"""
    
    def __init__(self, suite_name: str):
        self.suite_name = suite_name
        self.test_results = []
        # Create model-specific logger
        from core.logger import get_suite_logger
        # Create a new logger instance for this suite
        self.model_logger = get_suite_logger(self.suite_name)
    
    @abstractmethod
    def run_all_tests(self) -> List[TestResult]:
        """Führe alle Tests in der Suite aus"""
        pass
    
    @abstractmethod
    def get_test_description(self) -> str:
        """Gib eine Beschreibung der Test Suite zurück"""
        pass
    
    def run_single_test(self, test_name: str, test_func, **kwargs) -> TestResult:
        """Führe einen einzelnen Test aus"""
        start_time = time.time()
        
        # Logge Teststart
        result = self.model_logger.log_test_start(
            test_name=f"{self.suite_name}_{test_name}",
            test_type=self.suite_name,
            input_data=kwargs
        )
        
        try:
            # Führe Test aus
            test_result = test_func(**kwargs)
            
            # Berechne Dauer
            duration = time.time() - start_time
            result.duration = duration
            
            # Logge Testergebnis
            # Use the evaluation_score if available, otherwise use the score
            final_score = 0.0
            final_status = "failed"  # Default status
            
            if isinstance(test_result, dict):
                # Check for specific success indicators - these override everything else
                if test_result.get('is_correct', False):
                    final_status = "success"
                    # For JavaScript debugging, use the manual_score when is_correct is true
                    if 'manual_score' in test_result:
                        final_score = test_result['manual_score']
                    else:
                        final_score = 1.0  # Perfect score when is_correct is true
                elif test_result.get('status') == 'success':
                    final_status = "success"
                    if 'score' in test_result:
                        final_score = test_result['score']
                elif 'evaluation_score' in test_result and test_result['evaluation_score'] >= config.test_config.similarity_threshold:
                    final_status = "success"
                    final_score = test_result['evaluation_score']
                elif 'score' in test_result and test_result['score'] >= config.test_config.similarity_threshold:
                    final_status = "success"
                    final_score = test_result['score']
                elif 'execution_result' in test_result and isinstance(test_result['execution_result'], dict):
                    execution_score = test_result['execution_result'].get('score', 0.0)
                    if execution_score >= config.test_config.similarity_threshold:
                        final_status = "success"
                        final_score = execution_score
            
            # Update result status and score
            result.status = final_status
            result.score = final_score
            
            self.model_logger.log_test_result(
                result=result,
                output_data=test_result,
                score=final_score,
                details=test_result.get('details', '') if isinstance(test_result, dict) else str(test_result),
                input_data=test_result.get('input_data', {}) if isinstance(test_result, dict) else None
            )
            
            return result
        
        except Exception as e:
            # Logge Fehler
            duration = time.time() - start_time
            result.duration = duration
            self.model_logger.log_test_result(
                result=result,
                error_message=str(e),
                input_data=kwargs
            )
            return result
    
    def get_suite_summary(self) -> Dict[str, Any]:
        """Erstelle eine Zusammenfassung der Test Suite"""
        # Hole alle Ergebnisse für diese Suite, unabhängig vom Status
        all_results = self.model_logger.get_results()
        suite_results = [r for r in all_results if r.test_type == self.suite_name]
        
        if not suite_results:
            return {
                "suite_name": self.suite_name,
                "total_tests": 0,
                "passed": 0,
                "failed": 0,
                "errors": 0,
                "average_score": 0.0,
                "description": self.get_test_description()
            }
        
        passed = len([r for r in suite_results if r.status == "success"])
        failed = len([r for r in suite_results if r.status == "failed"])
        errors = len([r for r in suite_results if r.status == "error"])
        
        scores = [r.score for r in suite_results if r.score is not None]
        average_score = sum(scores) / len(scores) if scores else 0.0
        
        return {
            "suite_name": self.suite_name,
            "total_tests": len(suite_results),
            "passed": passed,
            "failed": failed,
            "errors": errors,
            "average_score": average_score,
            "description": self.get_test_description()
        }
    
    def validate_prerequisites(self) -> bool:
        """Validiere Voraussetzungen für die Test Suite"""
        return True
    
    def setup_suite(self) -> None:
        """Richte die Test Suite ein"""
        pass
    
    def teardown_suite(self) -> None:
        """Räume die Test Suite auf"""
        pass
    
    def run_suite_with_setup(self) -> List[TestResult]:
        """Führe die Test Suite mit Setup und Teardown aus"""
        try:
            # Validiere Voraussetzungen
            if not self.validate_prerequisites():
                raise Exception("Voraussetzungen für die Test Suite nicht erfüllt")
            
            # Setup
            self.setup_suite()
            
            # Führe Tests aus
            results = self.run_all_tests()
            
            return results
        
        except Exception as e:
            print(f"Fehler bei der Ausführung der Test Suite {self.suite_name}: {e}")
            return []
        
        finally:
            # Teardown
            self.teardown_suite()