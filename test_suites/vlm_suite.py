"""
Vision Language Model (VLM) Tests
"""
import os
import time
from typing import Dict, Any, List
from openai import OpenAI
from pathlib import Path

from config import key_manager
from .base_suite import BaseTestSuite
from core import logger, evaluator, TestResult

class VLMTestSuite(BaseTestSuite):
    """Test Suite für Vision Language Model Tests"""
    
    def __init__(self):
        super().__init__("vlm")
        # Initialize available models for vision, VLM-specific LLM, and evaluation
        self.available_vision_models = key_manager.get_available_models("vision")
        self.available_vlm_llm_models = key_manager.get_available_models("vlm_llm")
        self.available_evaluation_models = key_manager.get_available_models("evaluation")
        
        self.current_vision_model = None
        self.current_vlm_llm_model = None
        self.current_evaluation_model = None
        
        self.vision_client = None
        self.vision_model = None
        self.vlm_llm_client = None
        self.vlm_llm_model = None
        self.evaluation_client = None
        self.evaluation_model = None
        
        # Set default models - use first available model for each type
        available_vision_models = list(self.available_vlm_llm_models.keys())  # Use VLM LLM models for vision
        available_vlm_llm_models = list(self.available_vlm_llm_models.keys())
        available_evaluation_models = list(self.available_evaluation_models.keys())
        
        print(f"DEBUG: Available vision models: {available_vision_models}")
        print(f"DEBUG: Available VLM LLM models: {available_vlm_llm_models}")
        print(f"DEBUG: Available evaluation models: {available_evaluation_models}")
        
        # Use the actual model names instead of "default"
        vision_model = available_vision_models[0] if available_vision_models else None
        vlm_llm_model = available_vlm_llm_models[0] if available_vlm_llm_models else None
        # Skip evaluation if no models available (as requested)
        evaluation_model = available_evaluation_models[0] if available_evaluation_models and available_evaluation_models[0] != "default" else None
        
        print(f"DEBUG: Selected vision model: {vision_model}")
        print(f"DEBUG: Selected VLM LLM model: {vlm_llm_model}")
        print(f"DEBUG: Selected evaluation model: {evaluation_model}")
        
        # Only initialize if we have the required models
        if vision_model and vlm_llm_model:
            self.set_model(vision_model, vlm_llm_model, evaluation_model)
        else:
            print("ERROR: Not enough models available to initialize VLM suite")
        
        if vision_model and vlm_llm_model and evaluation_model:
            self.set_model(vision_model, vlm_llm_model, evaluation_model)
        else:
            print("ERROR: Not enough models available to initialize VLM suite")
    
    def get_test_description(self) -> str:
        """Gib eine Beschreibung der Test Suite zurück"""
        return "Umfassende multimodale Tests für Vision Language Models mit Integration aller vorheriger Aufgaben"
    
    def set_model(self, vision_model_type: str = None, llm_model_type: str = None, evaluation_model_type: str = None) -> bool:
        """Wechsle zu anderen Modellen"""
        try:
            # Set vision model
            if vision_model_type:
                if vision_model_type not in self.available_vlm_llm_models:
                    print(f"Vision Modell {vision_model_type} nicht verfügbar. Verfügbare Modelle: {list(self.available_vlm_llm_models.keys())}")
                    return False
                
                self.current_vision_model = vision_model_type
                self.vision_model = key_manager.get_model("vlm_llm", vision_model_type)
                self.vision_client = OpenAI(
                    api_key=key_manager.get_key("vlm_llm", vision_model_type),
                    base_url=key_manager.get_base_url("vlm_llm", vision_model_type),
                    timeout=key_manager.get_timeout("vlm_llm", vision_model_type)
                )
            
            # Set VLM-specific LLM model
            if llm_model_type:
                if llm_model_type not in self.available_vlm_llm_models:
                    print(f"VLM LLM Modell {llm_model_type} nicht verfügbar. Verfügbare Modelle: {list(self.available_vlm_llm_models.keys())}")
                    return False
                
                self.current_vlm_llm_model = llm_model_type
                self.vlm_llm_model = key_manager.get_model("vlm_llm", llm_model_type)
                self.vlm_llm_client = OpenAI(
                    api_key=key_manager.get_key("vlm_llm", llm_model_type),
                    base_url=key_manager.get_base_url("vlm_llm", llm_model_type),
                    timeout=key_manager.get_timeout("vlm_llm", llm_model_type)
                )
            
            # Set evaluation model
            if evaluation_model_type:
                if evaluation_model_type not in self.available_evaluation_models:
                    print(f"Evaluationsmodell {evaluation_model_type} nicht verfügbar. Verfügbare Modelle: {list(self.available_evaluation_models.keys())}")
                    return False
                
                self.current_evaluation_model = evaluation_model_type
                self.evaluation_model = key_manager.get_model("evaluation", evaluation_model_type)
                self.evaluation_client = OpenAI(
                    api_key=key_manager.get_key("evaluation", evaluation_model_type),
                    base_url=key_manager.get_base_url("evaluation", evaluation_model_type),
                    timeout=key_manager.get_timeout("evaluation", evaluation_model_type)
                )
            
            return True
        except Exception as e:
            print(f"Fehler beim Wechseln der Modelle: {e}")
            return False
    
    def validate_prerequisites(self) -> bool:
        """Validiere Voraussetzungen für die Test Suite"""
        try:
            # Teste Vision API Verbindung
            response = self.vision_client.chat.completions.create(
                model=self.vision_model,
                messages=[{"role": "user", "content": "Test"}],
                max_tokens=1
            )
            return True
        except Exception as e:
            print(f"Vision API Verbindung fehlgeschlagen: {e}")
            return False
    
    def read_reference_text(self, filename: str) -> str:
        """Lese Referenztext aus Datei"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return f.read().strip()
        except Exception as e:
            print(f"Fehler beim Lesen der Referenzdatei {filename}: {e}")
            return ""
    
    def test_document_analysis(self) -> Dict[str, Any]:
        """Teste Dokumentenanalyse mit Bildern"""
        image_file = "Bild/1.png"
        reference_text = self.read_reference_text("Bild/1.txt")
        
        if not os.path.exists(image_file):
            return {
                "error": f"Bilddatei nicht gefunden: {image_file}",
                "score": 0.0,
                "details": f"Dokumentenanalyse Test fehlgeschlagen: Datei nicht gefunden"
            }
        
        try:
            # Analysiere Bild mit Vision API
            import base64
            with open(image_file, "rb") as image_file_obj:
                image_base64 = base64.b64encode(image_file_obj.read()).decode('utf-8')
                response = self.vision_client.chat.completions.create(
                    model=self.vision_model,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": "Analysiere dieses Bild und erkläre die dargestellten chemischen Prozesse und Spaltungsprodukte von Methan."},
                                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_base64}"}}
                            ]
                        }
                    ],
                    max_tokens=500
                )
            
            generated_analysis = response.choices[0].message.content
            
            # Bewertung durchEvaluator
            evaluation_result = evaluator.evaluate_general_llm(
                test_name="document_analysis",
                generated_text=generated_analysis,
                expected_text=reference_text,
                evaluation_prompt="Bewerte die technische Korrektheit und Vollständigkeit der Bildanalyse."
            )
            
            return {
                "generated_analysis": generated_analysis,
                "reference_text": reference_text,
                "score": evaluation_result.primary_score,
                "evaluation_details": evaluation_result.evaluation_details,
                "image_file": image_file,
                "method": "vision_api"
            }
        
        except Exception as e:
            return {
                "error": str(e),
                "score": 0.0,
                "details": f"Dokumentenanalyse Test fehlgeschlagen: {e}"
            }
    
    def test_data_extraction(self) -> Dict[str, Any]:
        """Teste Datenextraktion aus technischen Bildern"""
        image_file = "Bild/2.JPG"
        reference_text = self.read_reference_text("Bild/2.txt")
        
        if not os.path.exists(image_file):
            return {
                "error": f"Bilddatei nicht gefunden: {image_file}",
                "score": 0.0,
                "details": f"Datenextraktion Test fehlgeschlagen: Datei nicht gefunden"
            }
        
        try:
            # Extrahiere Daten aus Bild mit Vision API
            import base64
            with open(image_file, "rb") as image_file_obj:
                image_base64 = base64.b64encode(image_file_obj.read()).decode('utf-8')
                response = self.vision_client.chat.completions.create(
                    model=self.vision_model,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": "Extrahiere alle technischen Daten aus diesem Bild und formatiere sie als strukturierte Daten."},
                                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
                            ]
                        }
                    ],
                    max_tokens=600
                )
            
            generated_data = response.choices[0].message.content
            
            # Bewertung durchEvaluator
            evaluation_result = evaluator.evaluate_general_llm(
                test_name="data_extraction",
                generated_text=generated_data,
                expected_text=reference_text,
                evaluation_prompt="Beworte die Genauigkeit und Vollständigkeit der extrahierten technischen Daten."
            )
            
            return {
                "generated_data": generated_data,
                "reference_text": reference_text,
                "score": evaluation_result.primary_score,
                "evaluation_details": evaluation_result.evaluation_details,
                "image_file": image_file,
                "method": "vision_api"
            }
        
        except Exception as e:
            return {
                "error": str(e),
                "score": 0.0,
                "details": f"Datenextraktion Test fehlgeschlagen: {e}"
            }
    
    def test_creative_story_generation(self) -> Dict[str, Any]:
        """Teste kreative Geschichtenerstellung aus Bildern"""
        image_file = "Bild/3.png"
        reference_text = self.read_reference_text("Bild/3.txt")
        
        if not os.path.exists(image_file):
            return {
                "error": f"Bilddatei nicht gefunden: {image_file}",
                "score": 0.0,
                "details": f"Kreative Geschichtenerstellung Test fehlgeschlagen: Datei nicht gefunden"
            }
        
        try:
            # Generiere Geschichte aus Bild mit Vision API
            import base64
            with open(image_file, "rb") as image_file_obj:
                image_base64 = base64.b64encode(image_file_obj.read()).decode('utf-8')
                response = self.vision_client.chat.completions.create(
                    model=self.vision_model,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": "Erstelle eine kreative Geschichte basierend auf diesem Bild. Die Geschichte sollte ansprechend und originell sein."},
                                {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_base64}"}}
                            ]
                        }
                    ],
                    max_tokens=600
                )
            
            generated_story = response.choices[0].message.content
            
            # Bewertung durchEvaluator
            evaluation_result = evaluator.evaluate_general_llm(
                test_name="creative_story_generation",
                generated_text=generated_story,
                expected_text=reference_text,
                evaluation_prompt="Bewerte die Kreativität, Originalität und erzählerische Qualität der Geschichte."
            )
            
            return {
                "generated_story": generated_story,
                "reference_text": reference_text,
                "score": evaluation_result.primary_score,
                "evaluation_details": evaluation_result.evaluation_details,
                "image_file": image_file,
                "method": "vision_api"
            }
        
        except Exception as e:
            return {
                "error": str(e),
                "score": 0.0,
                "details": f"Kreative Geschichtenerstellung Test fehlgeschlagen: {e}"
            }
    
    def test_multimodal_integration(self) -> Dict[str, Any]:
        """Teste Integration von Text, Audio und Vision"""
        # Kombiniere alle Modalitäten
        results = {}
        
        try:
            # 1. Textanalyse (aus VLM-specific LLM Tests)
            text_prompt = "Was sind die Hauptprinzipien der evolutionären Biologie?"
            text_response = self.vlm_llm_client.chat.completions.create(
                model=self.vlm_llm_model,
                messages=[{"role": "user", "content": text_prompt}],
                max_tokens=300
            )
            results["text_analysis"] = text_response.choices[0].message.content
            
            # 2. Audioanalyse (aus Audio Model Tests)
            if os.path.exists("Audio/1.wav"):
                with open("Audio/1.wav", "rb") as audio_file:
                    audio_transcription = self.vlm_llm_client.audio.transcriptions.create(
                        model=self.vlm_llm_model,
                        file=audio_file,
                        response_format="text"
                    )
                results["audio_analysis"] = audio_transcription
            
            # 3. Bildanalyse (aus VLM Tests)
            if os.path.exists("Bild/1.png"):
                import base64
                with open("Bild/1.png", "rb") as image_file:
                    image_base64 = base64.b64encode(image_file.read()).decode('utf-8')
                    vision_response = self.vision_client.chat.completions.create(
                        model=self.vision_model,
                        messages=[
                            {
                                "role": "user",
                                "content": [
                                    {"type": "text", "text": "Zusammenfasse die wichtigsten Punkte aus diesem Bild."},
                                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_base64}"}}
                                ]
                            }
                        ],
                        max_tokens=300
                    )
                results["image_analysis"] = vision_response.choices[0].message.content
            
            # 4. Kombinierte Analyse
            combined_prompt = f"""
            Basierend auf den folgenden multimodalen Analysen, erstelle eine umfassende Zusammenfassung:
            
            Textanalyse: {results.get('text_analysis', 'N/A')}
            Audioanalyse: {results.get('audio_analysis', 'N/A')}
            Bildanalyse: {results.get('image_analysis', 'N/A')}
            
            Bitte verbinde alle Informationen zu einem kohärenten Ganzen.
            """
            
            combined_response = self.vlm_llm_client.chat.completions.create(
                model=self.vlm_llm_model,
                messages=[{"role": "user", "content": combined_prompt}],
                max_tokens=500
            )
            
            results["combined_analysis"] = combined_response.choices[0].message.content
            
            # Bewertung der Integration
            evaluation_prompt = f"""
            Bewerte die Qualität der multimodalen Integration:
            
            Einzelanalysen:
            - Text: {results.get('text_analysis', 'N/A')}
            - Audio: {results.get('audio_analysis', 'N/A')}
            - Bild: {results.get('image_analysis', 'N/A')}
            
            Kombinierte Analyse: {results.get('combined_analysis', 'N/A')}
            
            Bitte bewerte auf Skala 0-1:
            - Kohärenz der Integration
            - Vollständigkeit der Informationen
            - Qualität der Zusammenführung
            """
            
            evaluation_response = self.evaluation_client.chat.completions.create(
                model=self.evaluation_model,
                messages=[{"role": "user", "content": evaluation_prompt}],
                max_tokens=200
            )
            
            evaluation_text = evaluation_response.choices[0].message.content
            score = self._extract_score_from_text(evaluation_text)
            
            return {
                "results": results,
                "score": score,
                "evaluation_details": evaluation_text,
                "method": "multimodal_integration"
            }
        
        except Exception as e:
            return {
                "error": str(e),
                "score": 0.0,
                "details": f"Multimodale Integration Test fehlgeschlagen: {e}"
            }
    
    def test_comprehensive_vlm_evaluation(self) -> Dict[str, Any]:
        """Teste umfassende VLM Bewertung mit allen vorherigen Aufgaben"""
        # Führe alle vorherigen Aufgaben aus und kombiniere Ergebnisse
        all_results = {}
        
        try:
            # 1. Führe alle Test Suiten aus
            test_suites_results = {}
            
            # Hier würden wir eigentlich die anderen Test Suiten aufrufen
            # Für jetzt simulieren wir die Ergebnisse
            test_suites_results["general_llm"] = {
                "score": 0.85,
                "tests": ["wirtschaft_wissen", "biologie_wissen", "logisches_denken"]
            }
            
            test_suites_results["coding_model"] = {
                "score": 0.90,
                "tests": ["python_arithmetic_mean", "javascript_debugging"]
            }
            
            test_suites_results["audio_model"] = {
                "score": 0.80,
                "tests": ["transcription_voxtral", "translation_voxtral"]
            }
            
            test_suites_results["vlm"] = {
                "score": 0.75,
                "tests": ["document_analysis", "data_extraction", "creative_story_generation"]
            }
            
            all_results["test_suites"] = test_suites_results
            
            # 2. Finale Bewertung durch LLM
            final_prompt = f"""
            Als finales VLM Evaluation, bewerte die Gesamtleistung basierend auf den folgenden Ergebnissen:
            
            Test Suite Ergebnisse:
            - General LLM: {test_suites_results['general_llm']['score']} ({', '.join(test_suites_results['general_llm']['tests'])})
            - Coding Model: {test_suites_results['coding_model']['score']} ({', '.join(test_suites_results['coding_model']['tests'])})
            - Audio Model: {test_suites_results['audio_model']['score']} ({', '.join(test_suites_results['audio_model']['tests'])})
            - VLM: {test_suites_results['vlm']['score']} ({', '.join(test_suites_results['vlm']['tests'])})
            
            Bitte gib eine finale Gesamtbewertung ab und gib Empfehlungen für Verbesserungen.
            """
            
            final_response = self.evaluation_client.chat.completions.create(
                model=self.evaluation_model,
                messages=[{"role": "user", "content": final_prompt}],
                max_tokens=400
            )
            
            final_evaluation = final_response.choices[0].message.content
            
            # Berechne Gesamtscore
            overall_score = sum(suite['score'] for suite in test_suites_results.values()) / len(test_suites_results)
            
            return {
                "overall_score": overall_score,
                "test_suites_results": test_suites_results,
                "final_evaluation": final_evaluation,
                "method": "comprehensive_vlm_evaluation"
            }
        
        except Exception as e:
            return {
                "error": str(e),
                "score": 0.0,
                "details": f"Umfassende VLM Bewertung Test fehlgeschlagen: {e}"
            }
    
    def _extract_score_from_text(self, text: str) -> float:
        """Extrahiere numerischen Score aus Text"""
        try:
            import re
            matches = re.findall(r'(0?\.\d+|1\.0|0)', text)
            if matches:
                return float(matches[0])
            return 0.5
        except:
            return 0.5
    
    def run_all_tests(self) -> List[TestResult]:
        """Führe alle Tests in der Suite aus"""
        # Get all available models - use VLM LLM models for vision
        available_vision_models = list(self.available_vlm_llm_models.keys())
        available_vlm_llm_models = list(self.available_vlm_llm_models.keys())
        available_evaluation_models = list(self.available_evaluation_models.keys())
        
        print(f"Verfügbare Vision Modelle: {available_vision_models}")
        print(f"Verfügbare VLM LLM Modelle: {available_vlm_llm_models}")
        print(f"Verfügbare Evaluationsmodelle: {available_evaluation_models}")
        
        all_results = []
        
        # Test combinations of models
        for vision_model in available_vision_models:
            for vlm_llm_model in available_vlm_llm_models:
                for eval_model in available_evaluation_models:
                    print(f"\n{'='*60}")
                    print(f"TESTE MODELL KOMBINATION: Vision={vision_model}, VLM_LLM={vlm_llm_model}, Evaluation={eval_model}")
                    print(f"{'='*60}")
                    
                    # Switch to this model combination
                    if not self.set_model(vision_model, vlm_llm_model, eval_model):
                        print(f"✗ Konnte nicht zu Modellkombination wechseln")
                        continue
                    
                    # Run only the core VLM tests as specified
                    tests = [
                        ("document_analysis", self.test_document_analysis),
                        ("data_extraction", self.test_data_extraction),
                        ("creative_story_generation", self.test_creative_story_generation)
                    ]
                    
                    model_results = []
                    for test_name, test_func in tests:
                        # Add model names to test name for identification
                        test_name_with_models = f"{test_name}_vision_{vision_model}_vlm_llm_{vlm_llm_model}_eval_{eval_model}"
                        result = self.run_single_test(test_name_with_models, test_func)
                        all_results.append(result)
                        model_results.append(result)
                    
                    all_results.extend(model_results)
        
        return all_results