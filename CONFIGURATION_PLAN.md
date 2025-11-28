# Plan de Configuration pour IP Reputation Checker

## Structure du fichier de configuration

### config/settings.py
```python
"""
Configuration settings for IP Reputation Checker
"""
import os
from typing import Dict, Any
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

class Settings:
    """Classe de configuration pour l'application"""
    
    # Paramètres de base de données
    DB_PATH: str = os.getenv("DB_PATH", "ip_reputation.db")
    
    # Paramètres Ollama
    OLLAMA_API_BASE: str = os.getenv("OLLAMA_API_BASE", "http://localhost:11434")
    OLLAMA_MODEL_NAME: str = os.getenv("OLLAMA_MODEL_NAME", "ollama_chat/qwen3:latest")
    OLLAMA_TEMPERATURE: float = float(os.getenv("OLLAMA_TEMPERATURE", "0.3"))
    OLLAMA_NUM_CTX: int = int(os.getenv("OLLAMA_NUM_CTX", "8096"))
    
    # Paramètres AbuseIPDB
    ABUSEIPDB_API_KEY: str = os.getenv("ABUSEIPDB_API_KEY", "")
    
    # URLs des services de réputation (maintenant dans la configuration)
    VIRUSTOTAL_URL: str = os.getenv("VIRUSTOTAL_URL", "https://www.virustotal.com/gui/ip-address/")
    ABUSEIPDB_CHECK_URL: str = os.getenv("ABUSEIPDB_CHECK_URL", "https://www.abuseipdb.com/check/")
    TALOS_URL: str = os.getenv("TALOS_URL", "https://talosintelligence.com/reputation_center/lookup?search=")
    MxTOOLBOX_URL: str = os.getenv("MXTOOLBOX_URL", "https://mxtoolbox.com/SuperTool.aspx?action=blacklist:")
    GOOGLE_SAFE_BROWSING_URL: str = os.getenv("GOOGLE_SAFE_BROWSING_URL", "https://transparencyreport.google.com/safe-browsing/search?url=")
    
    # Paramètres d'analyse
    ABUSE_CONFIDENCE_THRESHOLD: int = int(os.getenv("ABUSE_CONFIDENCE_THRESHOLD", "50"))
    
    # Paramètres API
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    
    @classmethod
    def validate(cls) -> None:
        """Valider la configuration"""
        if not cls.ABUSEIPDB_API_KEY:
            print("Warning: ABUSEIPDB_API_KEY is not set in environment variables")
        
        if not cls.OLLAMA_API_BASE:
            raise ValueError("OLLAMA_API_BASE is required")

# Instance globale des paramètres
settings = Settings()
settings.validate()
```

### Variables d'environnement requises (.env)
```
# Base de données
DB_PATH=ip_reputation.db

# Ollama
OLLAMA_API_BASE=http://localhost:11434
OLLAMA_MODEL_NAME=ollama_chat/qwen3:latest
OLLAMA_TEMPERATURE=0.3
OLLAMA_NUM_CTX=8096

# AbuseIPDB
ABUSEIPDB_API_KEY=your_api_key_here

# URLs des services de réputation
VIRUSTOTAL_URL=https://www.virustotal.com/gui/ip-address/
ABUSEIPDB_CHECK_URL=https://www.abuseipdb.com/check/
TALOS_URL=https://talosintelligence.com/reputation_center/lookup?search=
MXTOOLBOX_URL=https://mxtoolbox.com/SuperTool.aspx?action=blacklist:
GOOGLE_SAFE_BROWSING_URL=https://transparencyreport.google.com/safe-browsing/search?url=

# Paramètres d'analyse
ABUSE_CONFIDENCE_THRESHOLD=50

# API
API_HOST=0.0.0
API_PORT=8000
```

## Mise à jour des prompts

Les prompts dans `src/models/ollama_agent.py` et `src/main.py` seront mis à jour pour utiliser ces variables de configuration au lieu d'URL codées en dur.

Exemple de modification dans les prompts :
```python
# Ancien code
prompt = f"""
VirusTotal
- Go to [https://www.virustotal.com/gui/ip-address/{ip_address}](https://www.virustotal.com/gui/ip-address/).
"""

# Nouveau code
from config.settings import settings
prompt = f"""
VirusTotal
- Go to [{settings.VIRUSTOTAL_URL}{ip_address}]({settings.VIRUSTOTAL_URL}).
"""
```

## Structure du module d'exceptions

### src/exceptions.py
```python
"""
Exceptions personnalisées pour IP Reputation Checker
"""

class IPReputationError(Exception):
    """Base exception for IP reputation checker"""
    pass

class RateLimitExceededError(IPReputationError):
    """Exception raised when API rate limit is exceeded"""
    pass

class InvalidIPAddressError(IPReputationError):
    """Exception raised when an IP address is invalid"""
    pass

class DatabaseError(IPReputationError):
    """Exception raised when a database operation fails"""
    pass

class AIServiceError(IPReputationError):
    """Exception raised when the AI service fails"""
    pass
```

## Plan de migration

1. Créer les fichiers de configuration
2. Mettre à jour les modules existants pour utiliser la configuration
3. Remplacer les URLs codées en dur dans les prompts
4. Mettre à jour la gestion des erreurs pour utiliser les exceptions centralisées
5. Mettre à jour le service centralisé d'analyse d'IP
6. Mettre à jour l'API pour utiliser les composants centralisés
7. Tester l'application pour s'assurer que tout fonctionne correctement