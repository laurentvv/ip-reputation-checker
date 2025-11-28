from smolagents import CodeAgent, WebSearchTool, LiteLLMModel
from typing import Optional, Tuple, Dict, Any
import time
from config.settings import settings


class OllamaIPChecker:
    """IP reputation checker using Ollama AI model"""
    
    def __init__(self, model_name: str = "ollama_chat/qwen3:latest"):
        self.model = self.create_model(model_name)
        self.agent = self.create_agent(self.model)
    
    def create_model(self, model_name: str) -> LiteLLMModel:
        """Create and return the LiteLLM model instance"""
        return LiteLLMModel(
            api_base=settings.OLLAMA_API_BASE,
            model_id=model_name,
            temperature=settings.OLLAMA_TEMPERATURE,
            num_ctx=settings.OLLAMA_NUM_CTX
        )
    
    def create_agent(self, model: LiteLLMModel) -> CodeAgent:
        """Create and return the CodeAgent instance"""
        return CodeAgent(
            tools=[WebSearchTool()],
            model=model,
            additional_authorized_imports=[
                "requests",
                "bs4",
                "dns",
                "googlesearch",
                "json",
                "httpx",
                "scrapy",
                "whois",
                "playwright",
                "re",
                "itertools",
                "statistics",
                "dns.resolver"
            ],
            add_base_tools=True,
        )
    
    def extract_reputation(self, response) -> Optional[str]:
        """Extract 'GOOD' or 'BAD' from response text"""
        # If the response is a dictionary, extract the text
        text = response.get("text") if isinstance(response, dict) else str(response)

        # Convert to uppercase for searching
        if text:
            text = text.upper()
        else:
            return None

        # Look for BAD or GOOD at the beginning of the response or after key phrases
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('BAD') or line.startswith('GOOD'):
                if line.startswith('BAD'):
                    return "BAD"
                elif line.startswith('GOOD'):
                    return "GOOD"
        
        # Look for the final answer pattern
        import re
        # Look for patterns like "Final answer: BAD" or "Final answer: GOOD"
        final_answer_match = re.search(r'FINAL ANSWER:\s*(BAD|GOOD)', text)
        if final_answer_match:
            result = final_answer_match.group(1)
            return result
        
        # Look for patterns like "Answer: BAD" or "Answer: GOOD"
        answer_match = re.search(r'ANSWER:\s*(BAD|GOOD)', text)
        if answer_match:
            result = answer_match.group(1)
            return result
        
        # Look for patterns like "Result: BAD" or "Result: GOOD"
        result_match = re.search(r'RESULT:\s*(BAD|GOOD)', text)
        if result_match:
            result = result_match.group(1)
            return result
        
        # If not found at the beginning, search in the entire text
        if "BAD" in text and "GOOD" not in text:
            return "BAD"
        elif "GOOD" in text and "BAD" not in text:
            return "GOOD"
        elif "GOOD" in text and "BAD" in text:
            # If both are present, check which appears first in the context
            bad_pos = text.find("BAD")
            good_pos = text.find("GOOD")
            if bad_pos != -1 and (good_pos == -1 or bad_pos < good_pos):
                return "BAD"
            elif good_pos != -1 and (bad_pos == -1 or good_pos < bad_pos):
                return "GOOD"
        
        # Check for "CONCLUSION" or "SUMMARY" sections that might contain the final verdict
        conclusion_patterns = [
            r'CONCLUSION.*?(BAD|GOOD)',
            r'SUMMARY.*?(BAD|GOOD)',
            r'OVERALL.*?(BAD|GOOD)',
            r'FINAL.*?(BAD|GOOD)'
        ]
        
        for pattern in conclusion_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                result = match.group(1).upper()
                if result in ["BAD", "GOOD"]:
                    return result
        
        return None
    
    def check_ip_reputation(self, ip_address: str) -> Tuple[Optional[str], str]:
        """
        Check IP reputation using AI agent
        Returns: (reputation, full_response)
        """
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
        - Your response must start with either "BAD" or "GOOD" and nothing else should come before these words in your response.
        - Do not provide any additional summary, conclusion, or cybersecurity information beyond what is directly related to the IP analysis.
        """
        
        try:
            response = self.agent.run(prompt)
            reputation = self.extract_reputation(response)
            
            return reputation, str(response)
        
        except Exception as e:
            return None, f"Error: {str(e)}"
    
    def run_check(self, ip_address: str) -> Tuple[Optional[str], float, str]:
        """
        Run a complete IP check with timing
        Returns: (reputation, execution_time, full_response)
        """
        start_time = time.time()
        reputation, response = self.check_ip_reputation(ip_address)
        execution_time = time.time() - start_time
        
        return reputation, execution_time, response