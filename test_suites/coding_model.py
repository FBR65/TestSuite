"""
Coding Model Tests
"""
import subprocess
import tempfile
import os
import time
from typing import Dict, Any, List
from openai import OpenAI

from config import key_manager
from .base_suite import BaseTestSuite
from core import logger, evaluator, TestResult

class CodingModelTestSuite(BaseTestSuite):
    """Test Suite für Coding Model Tests"""
    
    def __init__(self):
        super().__init__("coding_model")
        # Initialize available models for coding
        self.available_models = key_manager.get_available_models("coding_llm")
        self.current_model = None
        self.llm_client = None
        self.model = None
        
        # Use first available model instead of "coding"
        available_model_keys = list(self.available_models.keys())
        if available_model_keys:
            self.set_model(available_model_keys[0])  # Use first available model
        else:
            print("ERROR: No coding models available")
    
    def get_test_description(self) -> str:
        """Gib eine Beschreibung der Test Suite zurück"""
        return "Bewertung von Codegenerierung und Debugging Fähigkeiten"
    
    def set_model(self, model_type: str) -> bool:
        """Wechsle zu einem anderen Modell"""
        try:
            if model_type not in self.available_models:
                print(f"Modell {model_type} nicht verfügbar. Verfügbare Modelle: {list(self.available_models.keys())}")
                return False
            
            self.current_model = model_type
            self.model = key_manager.get_model("coding_llm", model_type)
            self.llm_client = OpenAI(
                api_key=key_manager.get_key("coding_llm", model_type),
                base_url=key_manager.get_base_url("coding_llm", model_type),
                timeout=key_manager.get_timeout("coding_llm", model_type)
            )
            return True
        except Exception as e:
            print(f"Fehler beim Wechseln zu Modell {model_type}: {e}")
            return False
    
    def validate_prerequisites(self) -> bool:
        """Validiere Voraussetzungen für die Test Suite"""
        try:
            # Teste Python Verfügbarkeit
            result = subprocess.run(["python", "--version"], capture_output=True, text=True)
            return result.returncode == 0
        except FileNotFoundError:
            print("Python nicht gefunden")
            return False
    
    def execute_python_code(self, code: str, test_cases: List[Dict]) -> Dict[str, Any]:
        """Führe Python Code sicher aus"""
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            results = []
            
            for test_case in test_cases:
                try:
                    # Führe den Code aus
                    exec_globals = {}
                    exec(compile(open(temp_file).read(), temp_file, 'exec'), exec_globals)
                    
                    # Finde die Hauptfunktion
                    function_name = None
                    for name in exec_globals:
                        if callable(exec_globals[name]) and not name.startswith('_'):
                            function_name = name
                            break
                    
                    if not function_name:
                        results.append({
                            "status": "error",
                            "message": "Keine ausführbare Funktion gefunden"
                        })
                        continue
                    
                    # Führe Testfall aus
                    if 'input' in test_case:
                        # Versuche zuerst mit positional arguments
                        try:
                            if len(test_case['input']) == 1:
                                # Single argument - call as positional
                                input_value = list(test_case['input'].values())[0]
                                result = exec_globals[function_name](input_value)
                            else:
                                # Multiple arguments - call as keyword arguments
                                result = exec_globals[function_name](**test_case['input'])
                        except TypeError as e:
                            # Wenn keyword arguments fehlschlagen, versuche positional
                            if 'unexpected keyword argument' in str(e):
                                # Extrahiere values und rufe mit positional arguments auf
                                input_values = list(test_case['input'].values())
                                result = exec_globals[function_name](*input_values)
                            else:
                                raise e
                    else:
                        result = exec_globals[function_name]()
                    
                    expected = test_case.get('expected')
                    if expected == result:
                        results.append({
                            "status": "success",
                            "input": test_case.get('input'),
                            "expected": expected,
                            "result": result
                        })
                    else:
                        results.append({
                            "status": "failed",
                            "input": test_case.get('input'),
                            "expected": expected,
                            "result": result
                        })
                
                except Exception as e:
                    results.append({
                        "status": "error",
                        "input": test_case.get('input'),
                        "error": str(e)
                    })
            
            # Bereinige temporäre Datei
            os.unlink(temp_file)
            
            # Berechne Gesamtscore
            successful = len([r for r in results if r['status'] == 'success'])
            total = len(results)
            score = successful / total if total > 0 else 0.0
            
            return {
                "score": score,
                "results": results,
                "total_tests": total,
                "passed_tests": successful
            }
        
        except Exception as e:
            return {
                "score": 0.0,
                "error": str(e),
                "results": []
            }
    
    def test_python_arithmetic_mean(self) -> Dict[str, Any]:
        """Teste Python Funktion für arithmetisches Mittel"""
        prompt = "Erstelle eine Python-Funktion, die eine Liste von Zahlen entgegennimmt und das arithmetische Mittel berechnet."
        
        test_cases = [
            {"input": {"numbers": [1, 2, 3, 4, 5]}, "expected": 3.0},
            {"input": {"numbers": [10, 20, 30]}, "expected": 20.0},
            {"input": {"numbers": []}, "expected": 0},  # Edge case
            {"input": {"numbers": [1.5, 2.5, 3.5]}, "expected": 2.5}
        ]
        
        try:
            # Generiere Code mit LLM
            response = self.llm_client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.1
            )
            
            generated_code = response.choices[0].message.content
            
            # Extrahiere Code aus der Antwort
            import re
            code_match = re.search(r'```python\n(.*?)\n```', generated_code, re.DOTALL)
            if code_match:
                code = code_match.group(1)
            else:
                # Versuche, Code direkt zu extrahieren
                code = generated_code
            
            # Führe Code aus
            execution_result = self.execute_python_code(code, test_cases)
            
            # Bewertung durchEvaluator
            evaluation_result = evaluator.evaluate_coding_task(
                test_name="python_arithmetic_mean",
                code=code,
                test_cases=test_cases
            )
            
            return {
                "generated_code": code,
                "execution_result": execution_result,
                "evaluation_score": evaluation_result.secondary_score if evaluation_result.secondary_score is not None else evaluation_result.primary_score,
                "evaluation_details": evaluation_result.evaluation_details,
                "test_cases": test_cases
            }
        
        except Exception as e:
            return {
                "error": str(e),
                "score": 0.0,
                "details": f"Python arithmetisches Mittel Test fehlgeschlagen: {e}"
            }
    
    def test_javascript_debugging(self) -> Dict[str, Any]:
        """Teste JavaScript Debugging"""
        prompt = "Finde den Fehler in diesem JavaScript-Code, der eine Endlosschleife verursacht: `for (let i = 0; i < 10; i++) { console.log(i); }`"
        
        # Der Code hat eigentlich keine Endlosschleife, das ist der Test
        correct_analysis = "Der Code hat keine Endlosschleife. Die Schleife läuft genau 10 Mal von i=0 bis i=9."
        
        try:
            # Generiere Analyse mit LLM
            response = self.llm_client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.1
            )
            
            generated_analysis = response.choices[0].message.content
            
            # Prüfe ob die Analyse korrekt ist
            is_correct = "endlosschleife" not in generated_analysis.lower() or \
                        "keine endlosschleife" in generated_analysis.lower() or \
                        "läuft 10 mal" in generated_analysis.lower()
            
            score = 1.0 if is_correct else 0.0
            
            # Bewertung durchEvaluator
            evaluation_result = evaluator.evaluate_general_llm(
                test_name="javascript_debugging",
                generated_text=generated_analysis,
                expected_text=correct_analysis,
                evaluation_prompt="Bewerte ob die Analyse korrekt ist und dass der Code keine Endlosschleife hat."
            )
            
            return {
                "generated_analysis": generated_analysis,
                "is_correct": is_correct,
                "manual_score": score,
                "evaluation_score": evaluation_result.primary_score,
                "expected_analysis": correct_analysis,
                "details": evaluation_result.evaluation_details
            }
        
        except Exception as e:
            return {
                "error": str(e),
                "score": 0.0,
                "details": f"JavaScript Debugging Test fehlgeschlagen: {e}"
            }
    
    def test_python_string_operations(self) -> Dict[str, Any]:
        """Teste String Operationen"""
        prompt = "Erstelle eine Python-Funktion, die einen String entgegennimmt und die Anzahl der Wörter zurückgibt."
        
        test_cases = [
            {"input": {"text": "Hallo Welt"}, "expected": 2},
            {"input": {"text": "Das ist ein Test"}, "expected": 4},
            {"input": {"text": ""}, "expected": 0},  # Edge case
            {"input": {"text": "EinzelnesWort"}, "expected": 1}
        ]
        
        try:
            # Generiere Code mit LLM
            response = self.llm_client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.1
            )
            
            generated_code = response.choices[0].message.content
            
            # Extrahiere Code
            import re
            code_match = re.search(r'```python\n(.*?)\n```', generated_code, re.DOTALL)
            if code_match:
                code = code_match.group(1)
            else:
                code = generated_code
            
            # Führe Code aus
            execution_result = self.execute_python_code(code, test_cases)
            
            # Bewertung durchEvaluator
            evaluation_result = evaluator.evaluate_coding_task(
                test_name="python_string_operations",
                code=code,
                test_cases=test_cases
            )
            
            return {
                "generated_code": code,
                "execution_result": execution_result,
                "evaluation_score": evaluation_result.secondary_score if evaluation_result.secondary_score is not None else evaluation_result.primary_score,
                "evaluation_details": evaluation_result.evaluation_details,
                "test_cases": test_cases
            }
        
        except Exception as e:
            return {
                "error": str(e),
                "score": 0.0,
                "details": f"Python String Operationen Test fehlgeschlagen: {e}"
            }
    
    def test_python_list_operations(self) -> Dict[str, Any]:
        """Teste List Operationen"""
        prompt = "Erstelle eine Python-Funktion, die eine Liste von Zahlen entgegennimmt und die größte Zahl zurückgibt."
        
        test_cases = [
            {"input": {"numbers": [1, 5, 3, 9, 2]}, "expected": 9},
            {"input": {"numbers": [-1, -5, -3]}, "expected": -1},
            {"input": {"numbers": [42]}, "expected": 42},  # Edge case
            {"input": {"numbers": []}, "expected": None}  # Edge case
        ]
        
        try:
            # Generiere Code mit LLM
            response = self.llm_client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.1
            )
            
            generated_code = response.choices[0].message.content
            
            # Extrahiere Code
            import re
            code_match = re.search(r'```python\n(.*?)\n```', generated_code, re.DOTALL)
            if code_match:
                code = code_match.group(1)
            else:
                code = generated_code
            
            # Führe Code aus
            execution_result = self.execute_python_code(code, test_cases)
            
            # Bewertung durchEvaluator
            evaluation_result = evaluator.evaluate_coding_task(
                test_name="python_list_operations",
                code=code,
                test_cases=test_cases
            )
            
            return {
                "generated_code": code,
                "execution_result": execution_result,
                "evaluation_score": evaluation_result.secondary_score if evaluation_result.secondary_score is not None else evaluation_result.primary_score,
                "evaluation_details": evaluation_result.evaluation_details,
                "test_cases": test_cases
            }
        
        except Exception as e:
            return {
                "error": str(e),
                "score": 0.0,
                "details": f"Python List Operationen Test fehlgeschlagen: {e}"
            }
    
    def run_all_tests(self) -> List[TestResult]:
        """Führe alle Tests in der Suite aus"""
        # Get all available models
        available_models = list(self.available_models.keys())
        print(f"Verfügbare Modelle: {available_models}")
        
        all_results = []
        
        # Run tests for each model
        for model_type in available_models:
            print(f"\n{'='*60}")
            print(f"TESTE MODELL: {model_type}")
            print(f"{'='*60}")
            
            # Switch to this model
            if not self.set_model(model_type):
                print(f"✗ Konnte nicht zu Modell {model_type} wechseln")
                continue
            
            # Run all tests for this model
            tests = [
                ("python_arithmetic_mean", self.test_python_arithmetic_mean),
                ("javascript_debugging", self.test_javascript_debugging),
                ("python_string_operations", self.test_python_string_operations),
                ("python_list_operations", self.test_python_list_operations)
            ]
            
            model_results = []
            for test_name, test_func in tests:
                # Add model name to test name for identification
                test_name_with_model = f"{test_name}_{model_type}"
                result = self.run_single_test(test_name_with_model, test_func)
                all_results.append(result)
                model_results.append(result)
            
            all_results.extend(model_results)
        
        return all_results