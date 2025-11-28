from typing import Optional, Dict, Any
import time
import logging

from src.models.ollama_agent import OllamaIPChecker
from src.database.db_manager import DatabaseManager
from src.tools.abuseipdb_tool import check_ip_abuseipdb
from src.core.ip_validator import analyze_ip_quality
from config.settings import settings
from src.exceptions import InvalidIPAddressError, DatabaseError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class IPCheckService:
    """Service centralisé pour la vérification de la réputation d'IP"""
    
    def __init__(self, db_manager: Optional[DatabaseManager] = None, model_name: str = ""):
        self.db_manager = db_manager or DatabaseManager(settings.DB_PATH)
        self.model_name = model_name or settings.OLLAMA_MODEL_NAME
        self.ollama_checker = OllamaIPChecker(self.model_name)
    
    def check_ip_reputation(self, ip_address: str, use_cache: bool = True) -> tuple[str | None, str]:
        """
        Vérifier la réputation d'une adresse IP en utilisant le cache et l'analyse AI
        Returns: (reputation, full_response)
        """
        logger.info(f"Checking reputation for IP: {ip_address}")
        
        # Valider l'IP
        try:
            ip_analysis = analyze_ip_quality(ip_address)
            if not ip_analysis["valid"]:
                raise InvalidIPAddressError(f"Invalid IP address: {ip_address}")
        except Exception as e:
            logger.error(f"Error analyzing IP quality for {ip_address}: {str(e)}")
            raise InvalidIPAddressError(f"Invalid IP address: {ip_address}") from e
        
        # Vérifier si on doit utiliser le cache
        if use_cache:
            try:
                # Vérifier si l'IP est déjà dans la base de données avec une mauvaise réputation
                if self.db_manager.is_bad_ip(ip_address):
                    logger.info(f"Retrieved BAD reputation from database cache for IP: {ip_address}")
                    return "BAD", "Retrieved from database cache - BAD reputation"
                
                # Sinon, vérifier si l'IP est dans le cache avec une bonne réputation
                cached_reputation = self.db_manager.get_reputation(ip_address)
                if cached_reputation:
                    logger.info(f"Retrieved reputation from database cache for IP: {ip_address}")
                    return cached_reputation, "Retrieved from database cache"
            except DatabaseError as e:
                logger.warning(f"Database error during cache lookup for {ip_address}: {str(e)}")
                # Continue with fresh check if database is unavailable
            except Exception as e:
                logger.error(f"Unexpected error during cache lookup for {ip_address}: {str(e)}")
                raise DatabaseError(f"Database error during cache lookup: {str(e)}") from e
        
        # Effectuer une nouvelle vérification
        try:
            reputation, full_response = self.ollama_checker.check_ip_reputation(ip_address)
            logger.info(f"Ollama check completed for IP: {ip_address}, reputation: {reputation}")
        except Exception as e:
            logger.error(f"Error during Ollama IP reputation check for {ip_address}: {str(e)}")
            raise e
        
        # Stocker dans la base de données si on a un résultat
        if reputation:
            try:
                self.db_manager.store_reputation(ip_address, reputation)
            except DatabaseError as e:
                logger.error(f"Database error storing reputation for {ip_address}: {str(e)}")
                # Continue execution even if database storage fails
            except Exception as e:
                logger.error(f"Unexpected error storing reputation for {ip_address}: {str(e)}")
                raise DatabaseError(f"Database error storing reputation: {str(e)}") from e
        
        # Stocker l'analyse de qualité
        try:
            self.db_manager.store_analysis(
                ip_address,
                ip_analysis['quality_score'],
                ip_analysis['valid'],
                ip_analysis['is_private']
            )
        except DatabaseError as e:
            logger.error(f"Database error storing analysis for {ip_address}: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error storing analysis for {ip_address}: {str(e)}")
            raise DatabaseError(f"Database error storing analysis: {str(e)}") from e
        
        return reputation, full_response
    
    def check_ip_reputation_with_abuseipdb(self, ip_address: str) -> dict[str, Any] | None:
        """Vérifier la réputation d'une IP via l'API AbuseIPDB"""
        logger.info(f"Checking AbuseIPDB reputation for IP: {ip_address}")
        try:
            result = check_ip_abuseipdb(ip_address)
            logger.info(f"AbuseIPDB check completed for IP: {ip_address}")
            return result
        except Exception as e:
            logger.error(f"Error during AbuseIPDB check for {ip_address}: {str(e)}")
            raise e
    
    def run_check(self, ip_address: str, use_cache: bool = True) -> tuple[str | None, float, str]:
        """
        Exécuter un check complet avec timing
        Returns: (reputation, execution_time, full_response)
        """
        logger.info(f"Starting complete check for IP: {ip_address} with cache={use_cache}")
        start_time = time.time()
        try:
            reputation, response = self.check_ip_reputation(ip_address, use_cache)
            execution_time = time.time() - start_time
            logger.info(f"Complete check finished for IP: {ip_address}, time: {execution_time:.2f}s")
            return reputation, execution_time, response
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Error during complete check for {ip_address}: {str(e)}")
            raise e
    
    def create_enhanced_prompt(self, ip_address: str) -> str:
        """Créer un prompt amélioré en utilisant les URLs de configuration"""
        prompt = f"""
        You must analyze the reputation of the following IP address: {ip_address}.
        Follow the steps below to perform a complete evaluation. If negative results are found at any given step, you must stop the analysis immediately and conclude with a "BAD" verdict. Otherwise, continue until the end.

        ### IMPORTANT: If at any step you find an indication that the IP is malicious, stop the analysis immediately and respond with "BAD" without further explanation.
        
        ### Analysis Steps:
        0. **Reputation Sites**
        **VirusTotal**
        - Go to [{settings.VIRUSTOTAL_URL}{ip_address}]({settings.VIRUSTOTAL_URL}).
        - If detections are present, respond immediately "BAD".
        
        **AbuseIPDB**
        - Search the IP here: [{settings.ABUSEIPDB_CHECK_URL}{ip_address}]({settings.ABUSEIPDB_CHECK_URL}).
        - Note the confidence score (%) and abuse categories (spam, DDoS attack...).
        - If the confidence score is above {settings.ABUSE_CONFIDENCE_THRESHOLD}% or if abuse categories are detected, respond immediately "BAD".
        
        **Cisco Talos**
        - Use [{settings.TALOS_URL}{ip_address}]({settings.TALOS_URL}).
        - Get the "Talos Reputation" (Neutral/Malicious) and risk level.
        - If "Talos Reputation" is "Malicious" or risk level is high, respond immediately "BAD".
        
        **MXToolbox Blacklist Check**
        - Paste the IP here: [{settings.MXTOOLBOX_URL}{ip_address}]({settings.MXTOOLBOX_URL}).
        - List all blacklists where the IP is present (e.g. Spamhaus, Barracuda...).
        - If the IP is present in one or more blacklists, respond immediately "BAD".
        
        **Google Safe Browsing**
        - Check via: [{settings.GOOGLE_SAFE_BROWSING_URL}{ip_address}]({settings.GOOGLE_SAFE_BROWSING_URL}).
        - If the IP is reported as malicious, respond immediately "BAD".
        
        1. **Public blacklist verification**
        - Check if the IP is present in known public blacklists such as Spamhaus, AbuseIPDB, or other reliable sources.
        - If listed, note the associated reasons (spam, phishing, etc.).
        - If the IP is listed, respond immediately "BAD".
        
        2. **Association with malicious domains**
        - Search if the IP is linked to domains reported as malicious or involved in suspicious activities.
        - If an association is found, respond immediately "BAD".
        
        3. **Use in DDoS attacks**
        - Determine if the IP was involved in distributed denial-of-service (DDoS) attacks.
        - If the IP is involved in DDoS attacks, respond immediately "BAD".
        
        4. **Spam activities**
        - Check if the IP is used to send spam or is associated with unsolicited email servers.
        - If the IP is involved in spam activities, respond immediately "BAD".
        
        5. **Proxy or VPN**
        - Identify if the IP is used as an anonymous proxy, VPN server, or belongs to a TOR network.
        - If the IP is identified as a proxy or VPN, respond immediately "BAD".
        
        6. **Phishing attacks**
        - Search if the IP is involved in phishing campaigns or hosts fraudulent websites.
        - If the IP is involved in phishing attacks, respond immediately "BAD".
        
        7. **Malware**
        - Check if the IP is associated with malware distribution infrastructures.
        - If the IP is associated with malware, respond immediately "BAD".
        
        8. **Compromised accounts**
        - Search if the IP is linked to security incidents involving compromised accounts or data breaches.
        - If the IP is linked to compromised accounts, respond immediately "BAD".
        
        9. **Identity theft**
        - Identify if the IP is used in identity theft or fraud activities.
        - If the IP is involved in identity theft activities, respond immediately "BAD".
        
        10. **Geographic location**
            - Determine the geographic location of the IP (country, region, Internet service provider).
            - Note any anomalies, such as unusual location or unreliable ISP.
        
        11. **General Internet search**
            - Perform an in-depth search on the Internet to find additional information about this IP.
            - Consult forums, security reports, or relevant articles.
        
        12. **Synthesis and overall evaluation**
            - Analyze all collected information and provide an overall evaluation of the IP's reputation.
            - Clearly explain why you consider this IP as "GOOD" or "BAD".
        
        ### Expected response format:
        - If you find a negative indication at any step, respond with "BAD" only.
        - Otherwise, conclude with "GOOD" after checking all steps.
        """
        
        return prompt