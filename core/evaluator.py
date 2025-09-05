"""
Bewertungsmaschine für Testergebnisse
"""
import time
import threading
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from openai import OpenAI
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re

from config import key_manager

@dataclass
class EvaluationResult:
    """Datenklasse für Bewertungsergebnisse"""
    test_name: str
    primary_score: float
    secondary_score: Optional[float] = None
    evaluation_details: Optional[str] = None
    confidence: Optional[float] = None
    primary_model: str = ""
    secondary_model: str = ""

class LLMClient:
    """LLM Client für Bewertungsanfragen"""
    
    def __init__(self, service: str):
        self.service = service
        self.client = OpenAI(
            api_key=key_manager.get_key(service),
            base_url=key_manager.get_base_url(service),
            timeout=key_manager.get_timeout(service)
        )
        self.model = key_manager.get_model(service)
    
    def evaluate_text(self, prompt: str, context: str = "") -> str:
        """Bewerte Text mit LLM"""
        try:
            # Sanitize the prompt and context to prevent encoding issues
            sanitized_prompt = self._sanitize_text(prompt)
            sanitized_context = self._sanitize_text(context)
            
            messages = [
                {"role": "system", "content": "Du bist ein hilfreicher Assistent für die Bewertung von Testergebnissen."},
                {"role": "user", "content": f"{sanitized_prompt}\n\nKontext: {sanitized_context}"}
            ]
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.1,
                max_tokens=1000
            )
            
            result = response.choices[0].message.content.strip()
            return self._sanitize_text(result)
        
        except Exception as e:
            # Sanitize the error message to prevent encoding issues
            error_msg = str(e)
            sanitized_error = self._sanitize_text(error_msg)
            return f"LLM Bewertung fehlgeschlagen: {sanitized_error}"
    
    def _sanitize_text(self, text: str) -> str:
        """Sanitize text to prevent encoding issues"""
        if not isinstance(text, str):
            return text
        
        # Replace problematic Unicode characters with ASCII equivalents
        import re
        # Replace en-dash, em-dash, minus-minus, and other problematic characters
        text = re.sub(r'[\u2013\u2014\u2212\u2248\u2192]', '-', text)  # Dashes and minus-minus and arrow
        text = re.sub(r'[\u202f\u2009\u200a\u200b\u200c\u200d\u2060]', ' ', text)  # Narrow spaces
        # Keep other Unicode characters but ensure they're properly encoded
        return text.strip()
    
    def evaluate_code_functionality(self, code: str, test_cases: List[Dict]) -> str:
        """Bewerte Code-Funktionalität"""
        prompt = f"""
        Bewerte den folgenden Code auf Funktionalität:
        
        Code:
        ```python
        {code}
        ```
        
        Testfälle:
        {test_cases}
        
        Bitte antworte mit:
        - "Code funktioniert" wenn der Code korrekt funktioniert
        - "Code funktioniert nicht" wenn der Code Fehler hat
        - Erkläre kurz warum
        """
        
        return self.evaluate_text(prompt)

class TextComparator:
    """Vergleichswerkzeuge für Texte"""
    
    @staticmethod
    def calculate_cosine_similarity(text1: str, text2: str) -> float:
        """Berechne Cosine Ähnlichkeit zwischen zwei Texten"""
        try:
            # Vorverarbeitung
            text1 = re.sub(r'\s+', ' ', text1.lower().strip())
            text2 = re.sub(r'\s+', ' ', text2.lower().strip())
            
            if not text1 or not text2:
                return 0.0
            
            # TF-IDF Vektoren erstellen
            vectorizer = TfidfVectorizer().fit_transform([text1, text2])
            vectors = vectorizer.toarray()
            
            # Cosine Ähnlichkeit berechnen
            similarity = cosine_similarity([vectors[0]], [vectors[1]])[0][0]
            return float(similarity)
        
        except Exception as e:
            print(f"Fehler bei der Ähnlichkeitsberechnung: {e}")
            return 0.0
    
    @staticmethod
    def calculate_bleu_score(reference: str, candidate: str) -> float:
        """Berechne BLEU Score für Übersetzungen"""
        try:
            from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
            from nltk.tokenize import word_tokenize
            
            # Tokenisierung
            reference_tokens = word_tokenize(reference.lower())
            candidate_tokens = word_tokenize(candidate.lower())
            
            if not candidate_tokens:
                return 0.0
            
            # BLEU Score berechnen
            smoothing_function = SmoothingFunction().method1
            bleu_score = sentence_bleu(
                [reference_tokens], 
                candidate_tokens, 
                smoothing_function=smoothing_function
            )
            
            return float(bleu_score)
        
        except Exception as e:
            print(f"Fehler bei der BLEU Score Berechnung: {e}")
            return 0.0
    
    @staticmethod
    def calculate_rouge_score(reference: str, candidate: str) -> float:
        """Berechne ROUGE Score für Zusammenfassungen"""
        try:
            from rouge_score import rouge_scorer
            
            scorer = rouge_scorer.RougeScorer(['rougeL'], use_stemmer=True)
            scores = scorer.score(candidate, reference)
            
            # ROUGE-L Score verwenden
            return float(scores['rougeL'].fmeasure)
        
        except Exception as e:
            print(f"Fehler bei der ROUGE Score Berechnung: {e}")
            return 0.0

class TestEvaluator:
    """Hauptbewertungsklasse für Tests"""
    
    def __init__(self):
        self.text_comparator = TextComparator()
        self._llm_clients = {}
        self._lock = threading.Lock()
    
    def _get_llm_client(self, service: str) -> LLMClient:
        """Hole oder erstelle LLM Client"""
        with self._lock:
            if service not in self._llm_clients:
                self._llm_clients[service] = LLMClient(service)
            return self._llm_clients[service]
    
    def evaluate_general_llm(self, test_name: str, generated_text: str, 
                           expected_text: str, evaluation_prompt: str) -> EvaluationResult:
        """Bewerte allgemeine LLM Tests"""
        # Primäre Bewertung durch Ähnlichkeitsmetriken
        primary_score = self.text_comparator.calculate_cosine_similarity(generated_text, expected_text)
        
        # Sekundäre Bewertung durch anderes LLM
        secondary_client = self._get_llm_client("evaluation")
        
        evaluation_prompt = f"""
        Bitte bewerte die folgende Antwort auf Basis des erwarteten Ergebnisses:
        
        Erwartetes Ergebnis:
        {expected_text}
        
        Generierte Antwort:
        {generated_text}
        
        Bewertungsauftrag:
        {evaluation_prompt}
        
        Bitte gib eine Bewertung von 0-1 ab, wobei 1 perfekt ist.
        """
        
        try:
            evaluation_result = secondary_client.evaluate_text(evaluation_prompt)
            
            # DEBUG: Log full evaluation result
            print(f"DEBUG: Full evaluation result for {test_name}: {repr(evaluation_result)}")
            
            # Extrahiere Score aus der Bewertung
            secondary_score = self._extract_score_from_text(evaluation_result)
            
            print(f"DEBUG: Extracted secondary score: {secondary_score}")
            
            return EvaluationResult(
                test_name=test_name,
                primary_score=primary_score,
                secondary_score=secondary_score,
                evaluation_details=evaluation_result,
                primary_model="text_similarity",
                secondary_model=key_manager.get_model("evaluation")
            )
        
        except Exception as e:
            return EvaluationResult(
                test_name=test_name,
                primary_score=primary_score,
                evaluation_details=f"Sekundäre Bewertung fehlgeschlagen: {str(e)}",
                primary_model="text_similarity"
            )
    
    def evaluate_coding_task(self, test_name: str, code: str, test_cases: List[Dict]) -> EvaluationResult:
        """Bewerte Coding Aufgaben"""
        # Primäre Bewertung durch Code-Ausführung und Analyse
        primary_score, evaluation_details = self._evaluate_code_execution(code, test_cases)
        
        # Sekundäre Bewertung durch LLM
        secondary_client = self._get_llm_client("evaluation")
        
        try:
            llm_evaluation = secondary_client.evaluate_code_functionality(code, test_cases)
            
            # Extrahiere Score aus der Bewertung
            secondary_score = 1.0 if "Code funktioniert" in llm_evaluation else 0.0
            
            return EvaluationResult(
                test_name=test_name,
                primary_score=primary_score,
                secondary_score=secondary_score,
                evaluation_details=f"Code Bewertung: {llm_evaluation}\n\nDetails: {evaluation_details}",
                primary_model="code_execution",
                secondary_model=key_manager.get_model("evaluation")
            )
        
        except Exception as e:
            return EvaluationResult(
                test_name=test_name,
                primary_score=primary_score,
                evaluation_details=f"LLM Bewertung fehlgeschlagen: {str(e)}\n\nDetails: {evaluation_details}",
                primary_model="code_execution"
            )
    
    def evaluate_audio_task(self, test_name: str, generated_text: str,
                          expected_text: str, task_type: str) -> EvaluationResult:
        """Bewerte Audio Aufgaben (Transkription, Übersetzung, Zusammenfassung)"""
        # Wähle die passende Metrik basierend auf dem Aufgabentyp
        if task_type == "transcription":
            primary_score = self.text_comparator.calculate_cosine_similarity(generated_text, expected_text)
        elif task_type == "translation":
            primary_score = self.text_comparator.calculate_bleu_score(expected_text, generated_text)
        elif task_type == "summarization":
            # For summarization, use the evaluation model score as primary since ROUGE scores are typically low
            primary_score = None  # Will be set by evaluation model
        else:
            primary_score = self.text_comparator.calculate_cosine_similarity(generated_text, expected_text)
        
        # Sekundäre Bewertung durch LLM
        secondary_client = self._get_llm_client("evaluation")
        
        evaluation_prompt = f"""
        Bitte bewerte die folgende {task_type} auf Qualität und Genauigkeit:
        
        Erwartetes Ergebnis:
        {expected_text}
        
        Generierte {task_type}:
        {generated_text}
        
        Bitte gib eine Bewertung von 0-1 ab, wobei 1 perfekt ist.
        """
        
        try:
            evaluation_result = secondary_client.evaluate_text(evaluation_prompt)
            secondary_score = self._extract_score_from_text(evaluation_result)
            
            # For summarization, use the evaluation model score as primary
            if task_type == "summarization":
                primary_score = secondary_score
                primary_model = "evaluation_model"
            else:
                primary_model = f"{task_type}_metric"
            
            return EvaluationResult(
                test_name=test_name,
                primary_score=primary_score,
                secondary_score=secondary_score,
                evaluation_details=evaluation_result,
                primary_model=primary_model,
                secondary_model=key_manager.get_model("evaluation")
            )
        
        except Exception as e:
            # Fallback to metric-based score if evaluation fails
            if primary_score is None:
                primary_score = self.text_comparator.calculate_rouge_score(expected_text, generated_text)
            
            return EvaluationResult(
                test_name=test_name,
                primary_score=primary_score,
                evaluation_details=f"Sekundäre Bewertung fehlgeschlagen: {str(e)}",
                primary_model=f"{task_type}_metric"
            )
    
    def _evaluate_code_execution(self, code: str, test_cases: List[Dict]) -> Tuple[float, str]:
        """Führe Code aus und bewerte das Ergebnis"""
        try:
            # Sichere Codeausführung in einem separaten Namespace
            namespace = {}
            exec(code, namespace)
            
            # Suche nach der Hauptfunktion
            function_name = None
            for name in namespace:
                if callable(namespace[name]) and not name.startswith('_'):
                    function_name = name
                    break
            
            if not function_name:
                return 0.0, "Keine ausführbare Funktion gefunden"
            
            # Führe Testfälle aus
            passed_tests = 0
            total_tests = len(test_cases)
            details = []
            
            for test_case in test_cases:
                try:
                    if 'input' in test_case:
                        result = namespace[function_name](**test_case['input'])
                    else:
                        result = namespace[function_name]()
                    
                    expected = test_case.get('expected')
                    if expected == result:
                        passed_tests += 1
                        details.append(f"Test bestanden: {test_case}")
                    else:
                        details.append(f"Test fehlgeschlagen: Erwartet {expected}, erhalten {result}")
                
                except Exception as e:
                    details.append(f"Test fehlgeschlagen mit Fehler: {str(e)}")
            
            score = passed_tests / total_tests if total_tests > 0 else 0.0
            details_str = "\n".join(details)
            
            return score, details_str
        
        except Exception as e:
            return 0.0, f"Codeausführung fehlgeschlagen: {str(e)}"
    
    def _extract_score_from_text(self, text: str) -> float:
        """Extrahiere numerischen Score aus Text"""
        try:
            # Suche nach Zahlen zwischen 0 und 1 (sowohl Dezimalzahlen als auch Ganzzahlen)
            import re
            matches = re.findall(r'(0?\.\d+|1\.0|1|0)', text)
            if matches:
                score = float(matches[0])
                # Stelle sicher, dass der Score im gültigen Bereich liegt
                return max(0.0, min(1.0, score))
            return 0.5  # Standardwert wenn kein Score gefunden
        except:
            return 0.5

# Globale Bewertungsinstanz
evaluator = TestEvaluator()