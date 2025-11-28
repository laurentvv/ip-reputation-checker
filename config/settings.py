"""
Configuration settings for IP Reputation Checker
"""
import os
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
    MXTOOLBOX_URL: str = os.getenv("MXTOOLBOX_URL", "https://mxtoolbox.com/SuperTool.aspx?action=blacklist:")
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