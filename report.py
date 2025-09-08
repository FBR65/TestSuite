"""
Report Writer for TestSuite System
Liest Daten aus /data/results und erstellt Berichte basierend auf evaluation_details
"""
import json
import os
import sys
import logging
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

# Füge das aktuelle Verzeichnis zum Python Path hinzu
sys.path.insert(0, str(Path(__file__).parent))

# Import existing modules
try:
    from config import config
    from core.evaluator import LLMClient
    USE_EXTERNAL_LLM = True
except ImportError as e:
    print(f"Warning: Could not import external modules: {e}")
    USE_EXTERNAL_LLM = False

# Simple independent logger for report.py
class ReportLogger:
    """Simple logger for report generation"""
    
    def __init__(self, name: str = "report_writer"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)
        
        # Add handler to logger
        if not self.logger.handlers:
            self.logger.addHandler(console_handler)
    
    def info(self, message: str):
        self.logger.info(message)
    
    def error(self, message: str):
        self.logger.error(message)
    
    def warning(self, message: str):
        self.logger.warning(message)
    
    def debug(self, message: str):
        self.logger.debug(message)

# Global logger instance
logger = ReportLogger()

# Constants
RESULTS_DIR = "data/results"

class SimpleLLMClient:
    """Simple fallback LLM client for report generation"""
    
    def __init__(self, service: str = "evaluation"):
        self.service = service
        # Use the correct EVALUATION_MODEL from environment
        self.model = os.getenv("EVALUATION_MODEL", "gpt-oss:120b")  # Default to gpt-oss:120b
        self.max_tokens = 800  # Drastically reduced to force very concise, complete responses
        self.timeout = 120  # Standard timeout
    
    def evaluate_text(self, prompt: str, context: str = "") -> str:
        """Evaluate text with LLM using fallback method"""
        try:
            # Import here to avoid issues if openai is not available
            from openai import OpenAI
            
            # Try to get API keys from environment
            import os
            api_key = os.getenv("EVALUATION_API_KEY", "")
            base_url = os.getenv("EVALUATION_API_BASE_URL", "http://localhost:8001/v1")
            
            if not api_key:
                return "LLM Bewertung fehlgeschlagen: Kein API-Schlüssel gefunden"
            
            client = OpenAI(
                api_key=api_key,
                base_url=base_url,
                timeout=self.timeout
            )
            
            # Sanitize the prompt and context to prevent encoding issues
            sanitized_prompt = self._sanitize_text(prompt)
            sanitized_context = self._sanitize_text(context)
            
            messages = [
                {"role": "system", "content": "Du bist ein hilfreicher Assistent für die Bewertung von Testergebnissen."},
                {"role": "user", "content": f"{sanitized_prompt}\n\nKontext: {sanitized_context}"}
            ]
            
            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.05,  # Lower temperature for more focused responses
                max_tokens=self.max_tokens,
                stream=True  # Enable streaming
            )
            
            # Collect the streamed response
            full_response = ""
            for chunk in response:
                if chunk.choices[0].delta.content is not None:
                    content = chunk.choices[0].delta.content
                    full_response += content
            
            return self._sanitize_text(full_response.strip())
        
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

class DataReader:
    """Data reading and parsing module"""
    
    def __init__(self, results_dir: str = RESULTS_DIR):
        self.results_dir = Path(results_dir)
        self.logger = logger
    
    def read_all_results(self) -> Dict[str, List[Dict]]:
        """Read all result files from the results directory"""
        results = {}
        
        if not self.results_dir.exists():
            self.logger.error(f"Results directory not found: {self.results_dir}")
            return results
        
        for test_type_dir in self.results_dir.iterdir():
            if test_type_dir.is_dir():
                test_type = test_type_dir.name
                results[test_type] = []
                
                for result_file in test_type_dir.glob("*.json"):
                    try:
                        result_data = self._read_result_file(result_file)
                        if result_data:
                            results[test_type].append(result_data)
                    except Exception as e:
                        self.logger.error(f"Error reading {result_file}: {e}")
        
        return results
    
    def _read_result_file(self, file_path: Path) -> Dict[str, Any]:
        """Read and parse a single result file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Check if evaluation_details exists at the top level
            evaluation_details = data.get("evaluation_details", "")
            if not evaluation_details:
                # Look for evaluation_details in output_data
                output_data = data.get("output_data", {})
                if isinstance(output_data, dict):
                    evaluation_details = output_data.get("evaluation_details", "")
                    # Also check for 'details' field as fallback
                    if not evaluation_details and "details" in output_data:
                        evaluation_details = output_data.get("details", "")
            
            # Extract relevant information
            result = {
                "file_path": str(file_path),
                "test_name": data.get("test_name", ""),
                "test_type": data.get("test_type", ""),
                "status": data.get("status", ""),
                "score": data.get("score", 0.0),
                "evaluation_details": evaluation_details,
                "start_time": data.get("start_time", ""),
                "end_time": data.get("end_time", ""),
                "duration": data.get("duration", 0.0)
            }
            
            # Debug logging
            if not evaluation_details:
                self.logger.debug(f"No evaluation_details found in {file_path}")
            else:
                self.logger.debug(f"Found evaluation_details in {file_path}: {evaluation_details[:100]}...")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error parsing {file_path}: {e}")
            return None

class ReportGenerator:
    """Report generation module"""
    
    def __init__(self):
        self.logger = logger
        self.llm_client = self._initialize_llm_client()
    
    def _initialize_llm_client(self):
        """Initialize LLM client using EVALUATION_MODEL or fallback"""
        try:
            if USE_EXTERNAL_LLM:
                return LLMClient("evaluation")
            else:
                self.logger.info("Using fallback LLM client")
                return SimpleLLMClient("evaluation")
        except Exception as e:
            self.logger.error(f"Error initializing external LLM client, using fallback: {e}")
            return SimpleLLMClient("evaluation")
    
    def generate_individual_evaluations(self, results: Dict[str, List[Dict]], prompt_type: str = "detailed_analysis") -> Dict[str, str]:
        """Generate individual evaluations for each test category"""
        evaluations = {}
        
        # Individual evaluation prompt based on type
        if prompt_type == "detailed_analysis":
            individual_prompt = """Analysiere die folgenden Testergebnisse für die Kategorie {category}:

{context}

Bitte erstelle eine prägnante Bewertung dieser Kategorie mit:
1. Zusammenfassung der Ergebnisse
2. Stärken und Schwächen
3. Wichtige Erkenntnisse
4. Operative Risiken

Gib deine Bewertung als kurzes Memo aus."""
        else:  # comprehensive_memo
            individual_prompt = """Erstelle ein kurzes Memo für die Kategorie {category}:

{context}

Enthalte:
- Zusammenfassung
- Stärken/Schwächen
- Risiken

Sei sehr kurz. Deutsch."""
        
        for category, test_results in results.items():
            if test_results:
                context = self._prepare_context_for_category(test_results)
                formatted_prompt = individual_prompt.format(category=category.upper(), context=context)
                
                try:
                    evaluation = self.llm_client.evaluate_text(formatted_prompt)
                    evaluations[category] = evaluation
                    # Detailed logging of LLM response
                    self.logger.info(f"Generated evaluation for {category} ({len(evaluation)} chars)")
                    self.logger.debug(f"LLM Response for {category}: {repr(evaluation[:200])}...")
                except Exception as e:
                    error_msg = f"Keine Bewertung möglich für {category}: {str(e)}"
                    evaluations[category] = error_msg
                    self.logger.error(f"Error generating evaluation for {category}: {e}")
        
        return evaluations
    
    def generate_general_llm_individual_evaluations(self, results: Dict[str, List[Dict]]) -> Dict[str, str]:
        """Generate individual evaluations for each specific model in GENERAL_LLM category"""
        evaluations = {}
        
        # Process only GENERAL_LLM results
        if 'general_llm' not in results or not results['general_llm']:
            return evaluations
        
        # Individual evaluation prompt for specific models
        individual_prompt = """Analysiere die folgenden Testergebnisse für das spezifische Modell {model_name}:

{context}

Erstelle eine prägnante Bewertung dieses spezifischen Modells mit:
- Zusammenfassung der Ergebnisse
- Stärken und Schwächen
- Operative Risiken

Sei sehr kurz und spezifisch für dieses Modell. Deutsch."""
        
        for result in results['general_llm']:
            if result.get("evaluation_details"):
                # Extract model name from test_name
                test_name = result['test_name']
                model_name = self._extract_model_name(test_name)
                
                context = self._prepare_context_for_single_result(result)
                formatted_prompt = individual_prompt.format(model_name=model_name, context=context)
                
                try:
                    evaluation = self.llm_client.evaluate_text(formatted_prompt)
                    evaluations[model_name] = evaluation
                    # Detailed logging of LLM response
                    self.logger.info(f"Generated evaluation for model {model_name} ({len(evaluation)} chars)")
                    self.logger.debug(f"LLM Response for {model_name}: {repr(evaluation[:200])}...")
                except Exception as e:
                    error_msg = f"Keine Bewertung möglich für {model_name}: {str(e)}"
                    evaluations[model_name] = error_msg
                    self.logger.error(f"Error generating evaluation for {model_name}: {e}")
            else:
                self.logger.warning(f"Result {result['test_name']} has no evaluation_details")
        
        return evaluations
    
    def _extract_model_name(self, test_name: str) -> str:
        """Extract model name from test name"""
        # Extract model name between underscores or specific patterns
        import re
        # Look for model patterns like Mistral_Mixtral_8x22B_Instruct_v0_1, mistralai_Mistral_Small_3_2_24B_Instruct_2506, etc.
        model_patterns = [
            r'Mistral_Mixtral_8x22B_Instruct_v0_1',
            r'mistralai_Mistral_Small_3_2_24B_Instruct_2506',
            r'mistralai_Mixtral_8x7B_Instruct',
            r'Mistral_Mixtral_8x22B_Instruct_v0_1',
            r'mistralai_Mistral_Small_3_2_24B_Instruct_2506',
            r'mistralai_Mixtral_8x7B_Instruct'
        ]
        
        for pattern in model_patterns:
            if pattern in test_name:
                return pattern
        
        # Fallback: extract last part of test name
        parts = test_name.split('_')
        if len(parts) >= 3:
            return '_'.join(parts[-3:])  # Return last 3 parts as model identifier
        
        return test_name  # Return original as fallback
    
    def _prepare_context_for_single_result(self, result: Dict) -> str:
        """Prepare context string for a single result"""
        context_parts = []
        
        context_parts.append(f"**Test**: {result['test_name']}")
        context_parts.append(f"**Status**: {result['status']}")
        context_parts.append(f"**Score**: {result['score']:.2f}")
        context_parts.append(f"**Bewertungsdetails**: {result['evaluation_details']}")
        
        return "\n".join(context_parts)
    
    def generate_comprehensive_report(self, individual_evaluations: Dict[str, str], general_llm_model_evaluations: Dict[str, str] = None) -> str:
        """Generate comprehensive report from individual evaluations using multiple requests"""
        
        # Format individual evaluations
        formatted_evaluations = ""
        for category, evaluation in individual_evaluations.items():
            formatted_evaluations += f"\n## {category.upper()} Bewertung\n{evaluation}\n"
        
        # Generate each section separately
        sections = {}
        
        # 1. Executive Summary
        self.logger.info("Generating Executive Summary...")
        executive_prompt = f"""Erstelle eine kurze Übersichtstabelle mit allen Modellkategorien, ihren Scores und Hauptrisiken. Füge Stärken und Schwächen hinzu. Sei sehr kurz. Deutsch.

{formatted_evaluations}"""
        
        sections['executive_summary'] = self.llm_client.evaluate_text(executive_prompt)
        
        # 2. Detaillierte Analyse jeder Kategorie - use individual evaluations directly
        self.logger.info("Generating detailed analysis from individual evaluations...")
        
        # Create detailed analysis using the individual evaluations with better structure
        detailed_analysis = f"""## 2. Detaillierte Analyse jeder Modellkategorie

### 2.1 AUDIO_MODEL
{individual_evaluations.get('audio_model', 'Keine Daten verfügbar')}

### 2.2 CODING_MODEL
{individual_evaluations.get('coding_model', 'Keine Daten verfügbar')}

### 2.3 GENERAL_LLM (Einzelne Modelle)"""
        
        # Add individual model evaluations for GENERAL_LLM if available
        if general_llm_model_evaluations:
            for model_name, evaluation in general_llm_model_evaluations.items():
                detailed_analysis += f"\n#### {model_name}\n{evaluation}\n"
        else:
            detailed_analysis += "\nKeine Einzelbewertungen der Modelle verfügbar."
        
        detailed_analysis += f"""

### 2.4 VLM
{individual_evaluations.get('vlm', 'Keine Daten verfügbar')}"""
        
        sections['detailed_analysis'] = detailed_analysis
        
        # detailed_analysis is now set directly above, no LLM call needed
        
        # 3. Handlungsempfehlungen - REMOVED to avoid truncation
        self.logger.info("Skipping action recommendations to prevent report truncation")
        sections['action_recommendations'] = "Handlungsempfehlungen wurden entfernt, um Berichtabbrüche zu vermeiden."
        
        # Combine all sections into final report with proper structure (without action recommendations)
        final_report = f"""**Bericht - Bewertung der getesteten KI-Modelle (Stand {datetime.now().strftime('%d.%m.%Y')})**

---

## 1. Executive Summary (Gesamtergebnisse)

{sections['executive_summary']}

---

{sections['detailed_analysis']}

---

*Bericht erstellt am {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}*"""
        
        return final_report
    
    def _is_report_truncated(self, report: str) -> bool:
        """Check if the report appears to be truncated"""
        if len(report) < 1500:  # Very short reports are likely incomplete
            return True
        
        # Check for common truncation patterns
        truncation_patterns = [
            r'\w+$',  # Ends with a single word (likely cut off mid-sentence)
            r'\.\s*$',  # Ends with a period but no conclusion
            r'###\s*$',  # Ends with a heading marker
            r'\|\s*$',  # Ends with a table row marker
            r'Fazit\s*$',  # Ends with "Fazit" without content
            r'Referenz.*$',  # Ends with incomplete reference
        ]
        
        import re
        for pattern in truncation_patterns:
            if re.search(pattern, report.strip()):
                return True
        
        # Check if the report has incomplete sections
        required_sections = ['## 1.', '## 2.', '## 3.', '## 4.', '## 5.', '## 6.']
        found_sections = 0
        for section in required_sections:
            if section in report:
                found_sections += 1
        
        # If we have fewer than 4 sections in a long report, it's likely incomplete
        if found_sections < 4 and len(report) > 2000:
            return True
        
        return False
    
    def generate_report(self, results: Dict[str, List[Dict]], prompt_type: str = "comprehensive_memo") -> str:
        """Generate comprehensive report from evaluation results"""
        try:
            # Step 1: Generate individual evaluations for each category
            self.logger.info(f"Generating individual evaluations with prompt type: {prompt_type}...")
            individual_evaluations = self.generate_individual_evaluations(results, prompt_type)
            
            # Step 2: Generate individual evaluations for each specific model in GENERAL_LLM
            self.logger.info("Generating individual evaluations for GENERAL_LLM models...")
            general_llm_model_evaluations = self.generate_general_llm_individual_evaluations(results)
            
            # Step 3: Generate comprehensive report from individual evaluations
            self.logger.info("Generating comprehensive report...")
            report = self.generate_comprehensive_report(individual_evaluations, general_llm_model_evaluations)
            
            return report
            
        except Exception as e:
            self.logger.error(f"Error generating report: {e}")
            return f"Fehler bei der Berichterstellung: {str(e)}"
    
    def _prepare_context_for_category(self, test_results: List[Dict]) -> str:
        """Prepare context string for a specific category - limit to first 3 results"""
        context_parts = []
        
        # Only process first 3 results to keep context concise
        for result in test_results[:3]:
            if result.get("evaluation_details"):
                context_parts.append(f"### {result['test_name']}")
                context_parts.append(f"**Status**: {result['status']}")
                context_parts.append(f"**Score**: {result['score']:.2f}")
                context_parts.append(f"**Bewertungsdetails**: {result['evaluation_details']}")
        
        return "\n".join(context_parts)
    
    def _prepare_context(self, results: Dict[str, List[Dict]]) -> str:
        """Prepare context string from evaluation results (legacy method)"""
        context_parts = []
        
        for test_type, test_results in results.items():
            if test_results:
                context_parts.append(f"\n## {test_type.upper()} Tests")
                
                for result in test_results:
                    if result.get("evaluation_details"):
                        context_parts.append(f"\n### {result['test_name']}")
                        context_parts.append(f"**Status**: {result['status']}")
                        context_parts.append(f"**Score**: {result['score']:.2f}")
                        context_parts.append(f"**Dauer**: {result['duration']:.2f}s")
                        context_parts.append(f"**Bewertungsdetails**: {result['evaluation_details']}")
        
        return "\n".join(context_parts)

class OutputHandler:
    """Output formatting and saving module"""
    
    def __init__(self):
        self.logger = logger
    
    def save_report(self, report: str, output_file: str = None) -> str:
        """Save report to file"""
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"test_report_{timestamp}.md"
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report)
            
            self.logger.info(f"Report saved to: {output_file}")
            return output_file
            
        except Exception as e:
            self.logger.error(f"Error saving report: {e}")
            raise
    
    def display_summary(self, report: str) -> None:
        """Display a summary of the generated report"""
        print("\n" + "="*60)
        print("BERICHTZUSAMMENFASSUNG")
        print("="*60)
        print(f"Generiert am: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Berichtlänge: {len(report)} Zeichen")
        print("="*60)
        
        # Extract and display key insights
        lines = report.split('\n')
        for i, line in enumerate(lines[:10]):  # Show first 10 lines
            # Try to encode with UTF-8, fallback to ASCII if it fails
            try:
                print(line)
            except UnicodeEncodeError:
                # Replace problematic characters
                clean_line = line.encode('ascii', 'ignore').decode('ascii')
                print(clean_line)
        
        if len(lines) > 10:
            print("... (weitere Details im gespeicherten Bericht)")
        
        print("="*60)

def main():
    """Main function to generate report"""
    try:
        # Initialize modules
        data_reader = DataReader()
        report_generator = ReportGenerator()
        output_handler = OutputHandler()
        
        # Read all results
        print("Lese Testergebnisse aus /data/results...")
        results = data_reader.read_all_results()
        
        # Check if we have any results
        if not any(results.values()):
            print("Keine Testergebnisse gefunden in /data/results")
            return 1
        
        # Generate report
        print("Generiere Bericht...")
        report = report_generator.generate_report(results)
        
        # Save and display report
        output_file = output_handler.save_report(report)
        output_handler.display_summary(report)
        
        print(f"\nBericht erfolgreich erstellt: {output_file}")
        
    except Exception as e:
        print(f"Fehler bei der Berichterstellung: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='TestSuite Report Generator')
    parser.add_argument('--results-dir', '-r', type=str, default=RESULTS_DIR,
                       help=f'Verzeichnis mit Testergebnissen (Standard: {RESULTS_DIR})')
    parser.add_argument('--output', '-o', type=str,
                       help='Ausgabedatei für den Bericht')
    parser.add_argument('--prompt-type', '-p', choices=['detailed_analysis', 'comprehensive_memo'],
                       default='comprehensive_memo',
                       help='Typ des zu verwendenden Prompts')
    
    args = parser.parse_args()
    
    # Override results directory if specified
    custom_results_dir = args.results_dir
    
    # Update DataReader with custom results directory
    data_reader = DataReader(custom_results_dir)
    
    # Generate report with specified prompt type
    report_generator = ReportGenerator()
    results = data_reader.read_all_results()
    
    if not any(results.values()):
        print("Keine Testergebnisse gefunden in angegebenem Verzeichnis")
        sys.exit(1)
    
    report = report_generator.generate_report(results, args.prompt_type)
    
    # Save report
    output_handler = OutputHandler()
    output_file = output_handler.save_report(report, args.output)
    output_handler.display_summary(report)
    
    print(f"\nBericht erfolgreich erstellt: {output_file}")