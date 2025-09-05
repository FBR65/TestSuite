"""
Sichere API-Schlüsselverwaltung
"""
import os
from typing import Dict, Optional
import logging
from .settings import config

logger = logging.getLogger(__name__)

class APIKeyManager:
    """Verwaltet API-Schlüssel und deren Validierung"""
    
    def __init__(self):
        self._keys = {}
        self._validate_keys()
    
    def _validate_keys(self) -> None:
        """Validiere alle API-Schlüssel"""
        missing_keys = []
        
        for service, api_config in config.api_configs.items():
            if not api_config.api_key:
                missing_keys.append(service)
                logger.warning(f"API-Schlüssel für {service} fehlt")
            else:
                self._keys[service] = api_config.api_key
                logger.info(f"API-Schlüssel für {service} erfolgreich geladen")
        
        if missing_keys:
            raise ValueError(f"Fehlende API-Schlüssel für Dienste: {', '.join(missing_keys)}")
    
    def get_key(self, service: str, model_type: str = "default") -> str:
        """Hole API-Schlüssel für einen bestimmten Dienst und Modelltyp"""
        if service not in config.multi_model_configs:
            raise ValueError(f"Unbekannter Dienst: {service}")
        if model_type not in config.multi_model_configs[service].models:
            raise ValueError(f"Unbekannter Modelltyp '{model_type}' für Dienst {service}")
        return config.multi_model_configs[service].models[model_type].api_key
    
    def get_base_url(self, service: str, model_type: str = "default") -> str:
        """Hole Basis-URL für einen bestimmten Dienst und Modelltyp"""
        if service not in config.multi_model_configs:
            raise ValueError(f"Unbekannter Dienst: {service}")
        if model_type not in config.multi_model_configs[service].models:
            raise ValueError(f"Unbekannter Modelltyp '{model_type}' für Dienst {service}")
        return config.multi_model_configs[service].models[model_type].base_url
    
    def get_model(self, service: str, model_type: str = "default") -> str:
        """Hole Modellname für einen bestimmten Dienst und Modelltyp"""
        if service not in config.multi_model_configs:
            raise ValueError(f"Unbekannter Dienst: {service}")
        if model_type not in config.multi_model_configs[service].models:
            raise ValueError(f"Unbekannter Modelltyp '{model_type}' für Dienst {service}")
        return config.multi_model_configs[service].models[model_type].model
    
    def get_timeout(self, service: str, model_type: str = "default") -> int:
        """Hole Timeout für einen bestimmten Dienst und Modelltyp"""
        if service not in config.multi_model_configs:
            raise ValueError(f"Unbekannter Dienst: {service}")
        if model_type not in config.multi_model_configs[service].models:
            raise ValueError(f"Unbekannter Modelltyp '{model_type}' für Dienst {service}")
        return config.multi_model_configs[service].models[model_type].timeout
    
    def get_max_retries(self, service: str, model_type: str = "default") -> int:
        """Hole maximale Wiederholungen für einen bestimmten Dienst und Modelltyp"""
        if service not in config.multi_model_configs:
            raise ValueError(f"Unbekannter Dienst: {service}")
        if model_type not in config.multi_model_configs[service].models:
            raise ValueError(f"Unbekannter Modelltyp '{model_type}' für Dienst {service}")
        return config.multi_model_configs[service].models[model_type].max_retries
    
    def get_available_models(self, service: str) -> Dict[str, str]:
        """Hole alle verfügbaren Modelle für einen Dienst"""
        if service not in config.multi_model_configs:
            raise ValueError(f"Unbekannter Dienst: {service}")
        return {model_name: model_config.model for model_name, model_config in config.multi_model_configs[service].models.items()}
    
    def get_default_model_type(self, service: str) -> str:
        """Hole den Standardmodelltyp für einen Dienst"""
        if service not in config.multi_model_configs:
            raise ValueError(f"Unbekannter Dienst: {service}")
        return config.multi_model_configs[service].default_model
    
    def is_service_available(self, service: str) -> bool:
        """Prüfe ob ein Dienst verfügbar ist"""
        return service in self._keys and bool(self._keys[service])

# Globale Instanz
key_manager = APIKeyManager()