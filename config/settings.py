"""
Konfigurationsverwaltung für das TestSuite System
"""
import os
from typing import Dict, Any
from dataclasses import dataclass
from dotenv import load_dotenv

# Lade Umgebungsvariablen
load_dotenv()

@dataclass
class APIConfig:
    """API Konfiguration für verschiedene Dienste"""
    api_key: str
    base_url: str
    model: str
    timeout: int = 30
    max_retries: int = 3

@dataclass
class MultiModelConfig:
    """Multi-Model Konfiguration für verschiedene Dienste"""
    models: Dict[str, APIConfig]
    default_model: str

@dataclass
class TestConfig:
    """Test Konfiguration"""
    max_test_duration: int = 300  # Sekunden
    similarity_threshold: float = 0.8
    enable_logging: bool = True
    log_level: str = "INFO"
    results_dir: str = "data/results"

@dataclass
class SystemConfig:
    """Gesamtsystem Konfiguration"""
    api_configs: Dict[str, APIConfig]
    multi_model_configs: Dict[str, MultiModelConfig]
    test_config: TestConfig
    debug_mode: bool = False
    
    @classmethod
    def from_env(cls) -> 'SystemConfig':
        """Erstelle Konfiguration aus Umgebungsvariablen"""
        # API Konfigurationen
        api_configs = {
            "llm": APIConfig(
                api_key=os.getenv("LLM_API_KEY", ""),
                base_url=os.getenv("LLM_API_BASE_URL", "http://localhost:8001/v1"),
                model=os.getenv("LLM_MODEL", "local-gpt-3.5-turbo")
            ),
            "whisper": APIConfig(
                api_key=os.getenv("WHISPER_API_KEY", ""),
                base_url=os.getenv("WHISPER_API_BASE_URL", "http://localhost:8002/v1"),
                model=os.getenv("WHISPER_MODEL", "whisper-large")
            ),
            "voxtral": APIConfig(
                api_key=os.getenv("VOXTRAL_API_KEY", ""),
                base_url=os.getenv("VOXTRAL_API_BASE_URL", "http://10.78.0.4:8110/v1"),
                model=os.getenv("VOXTRAL_MODEL", "local-voxtral")
            ),
            "vision": APIConfig(
                api_key=os.getenv("VISION_API_KEY", ""),
                base_url=os.getenv("VISION_API_BASE_URL", "http://localhost:8003/v1"),
                model=os.getenv("VISION_MODEL", "local-gpt-4-vision")
            ),
            "evaluation": APIConfig(
                api_key=os.getenv("EVALUATION_API_KEY", ""),
                base_url=os.getenv("EVALUATION_API_BASE_URL", "http://localhost:8001/v1"),
                model=os.getenv("EVALUATION_MODEL", "local-gpt-4")
            )
        }
        
        # Test Konfiguration
        test_config = TestConfig(
            max_test_duration=int(os.getenv("MAX_TEST_DURATION", "300")),
            similarity_threshold=float(os.getenv("SIMILARITY_THRESHOLD", "0.8")),
            enable_logging=os.getenv("ENABLE_LOGGING", "true").lower() == "true",
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            results_dir=os.getenv("RESULTS_DIR", "data/results")
        )
        
        # System Konfiguration
        debug_mode = os.getenv("DEBUG_MODE", "false").lower() == "true"
        
        # Multi-Model Konfigurationen
        # Parse LLM models from environment variable
        llm_models_config = {}
        if os.getenv("LLM_MODELS"):
            try:
                import json
                llm_models_dict = json.loads(os.getenv("LLM_MODELS"))
                for model_name, base_url in llm_models_dict.items():
                    model_key = model_name.replace("/", "_").replace(".", "_").replace("-", "_")
                    llm_models_config[model_key] = APIConfig(
                        api_key=os.getenv("LLM_API_KEY", ""),
                        base_url=base_url,
                        model=model_name
                    )
            except json.JSONDecodeError:
                print("Warning: Invalid JSON in LLM_MODELS environment variable")
        
        # Don't add default model - use only the models defined in LLM_MODELS
        
        # Parse Coding-specific LLM models from environment variable
        coding_llm_models_config = {}
        if os.getenv("CODING_LLM_MODELS"):
            try:
                import json
                coding_llm_models_dict = json.loads(os.getenv("CODING_LLM_MODELS"))
                for model_name, base_url in coding_llm_models_dict.items():
                    model_key = model_name.replace("/", "_").replace(".", "_").replace("-", "_")
                    coding_llm_models_config[model_key] = APIConfig(
                        api_key=os.getenv("CODING_API_KEY", os.getenv("LLM_API_KEY", "")),
                        base_url=base_url,
                        model=model_name
                    )
            except json.JSONDecodeError:
                print("Warning: Invalid JSON in CODING_LLM_MODELS environment variable")
        
        # Parse VLM-specific LLM models from environment variable
        vlm_llm_models_config = {}
        if os.getenv("VLM_LLM_MODELS"):
            try:
                import json
                vlm_llm_models_dict = json.loads(os.getenv("VLM_LLM_MODELS"))
                for model_name, base_url in vlm_llm_models_dict.items():
                    model_key = model_name.replace("/", "_").replace(".", "_").replace("-", "_")
                    vlm_llm_models_config[model_key] = APIConfig(
                        api_key=os.getenv("LLM_API_KEY", ""),
                        base_url=base_url,
                        model=model_name
                    )
            except json.JSONDecodeError:
                print("Warning: Invalid JSON in VLM_LLM_MODELS environment variable")
        
        multi_model_configs = {
            "llm": MultiModelConfig(
                models=llm_models_config,
                default_model=os.getenv("LLM_DEFAULT_MODEL", "default")
            ),
            "whisper": MultiModelConfig(
                models={
                    "default": APIConfig(
                        api_key=os.getenv("WHISPER_API_KEY", ""),
                        base_url=os.getenv("WHISPER_API_BASE_URL", "http://localhost:8002/v1"),
                        model=os.getenv("WHISPER_MODEL", "whisper-large")
                    )
                },
                default_model="default"
            ),
            "vision": MultiModelConfig(
                models={
                    "default": APIConfig(
                        api_key=os.getenv("VISION_API_KEY", ""),
                        base_url=os.getenv("VISION_API_BASE_URL", "http://localhost:8003/v1"),
                        model=os.getenv("VISION_MODEL", "local-gpt-4-vision")
                    )
                },
                default_model="default"
            ),
            # Add VLM-specific models - these should be separate from general LLM models
            "vlm_llm": MultiModelConfig(
                models=vlm_llm_models_config,
                default_model=os.getenv("VLM_LLM_DEFAULT_MODEL", "default")
            ),
            "coding_llm": MultiModelConfig(
                models=coding_llm_models_config,
                default_model=os.getenv("CODING_LLM_DEFAULT_MODEL", "default")
            ),
            "voxtral": MultiModelConfig(
                models={
                    "default": APIConfig(
                        api_key=os.getenv("VOXTRAL_API_KEY", ""),
                        base_url=os.getenv("VOXTRAL_API_BASE_URL", "http://localhost:8110/v1"),
                        model=os.getenv("VOXTRAL_MODEL", "local-voxtral")
                    )
                },
                default_model="default"
            ),
            "evaluation": MultiModelConfig(
                models={
                    "default": APIConfig(
                        api_key=os.getenv("EVALUATION_API_KEY", ""),
                        base_url=os.getenv("EVALUATION_API_BASE_URL", "http://localhost:8001/v1"),
                        model=os.getenv("EVALUATION_MODEL", "local-gpt-4")
                    )
                },
                default_model="default"
            )
        }
        
        return cls(
            api_configs=api_configs,
            multi_model_configs=multi_model_configs,
            test_config=test_config,
            debug_mode=debug_mode
        )

# Globale Konfigurationsinstanz
config = SystemConfig.from_env()