import os
import requests
from dotenv import load_dotenv
from typing import Optional, Dict, Any
import logging

# Charger les variables d'environnement
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RateLimitExceededError(Exception):
    """Exception raised when API rate limit is exceeded"""
    pass


def check_ip_abuseipdb(ip_address: str) -> Optional[Dict[str, Any]]:
    """
    Check IP reputation via AbuseIPDB API considering rate limits.
    The free plan is limited to 1,000 requests per day.

    Args:
        ip_address (str): IP address to check

    Returns:
        dict: IP reputation data if request succeeds, None otherwise
            - abuseConfidenceScore: Abuse confidence score (0-100)
            - lastReportedAt: Last report date
            - usageType: IP usage type
            - ip: The checked IP address
            - totalReports: Number of reports for this IP
            - isp: Internet service provider
            - countryName: Country name

    Raises:
        ValueError: If API key is not found in .env
        RateLimitExceededError: If daily request quota is exceeded
                               (1,000 requests/day on free plan)
    """
    API_KEY = os.getenv("ABUSEIPDB_API_KEY")
    if not API_KEY:
        raise ValueError("API key not found in .env")

    url = "https://api.abuseipdb.com/api/v2/check"
    headers = {"Key": API_KEY, "Accept": "application/json"}
    params = {
        "ipAddress": ip_address, 
        "maxAgeInDays": "90",
        "verbose": True  # Include verbose output
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()

        # Check rate limits
        remaining = int(response.headers.get("X-RateLimit-Remaining", 0))
        limit = int(
            response.headers.get("X-RateLimit-Limit", 1000)
        )  # Default value

        if remaining <= 0:
            raise RateLimitExceededError(
                f"Daily request quota exceeded (Free plan: {limit} requests/day). "
                f"Used: {limit - remaining}/{limit}"
            )
        elif remaining < limit * 0.1:  # Alert if less than 10% remaining
            logger.warning(
                f"Only {remaining}/{limit} requests remaining today "
                f"(Free plan: 1,000 requests/day)"
            )

        data = response.json()["data"]

        # Return only the relevant information
        return {
            "ip": data.get("ipAddress"),
            "abuse_confidence_score": data.get("abuseConfidenceScore"),
            "last_reported_at": data.get("lastReportedAt"),
            "usage_type": data.get("usageType"),
            "total_reports": data.get("totalReports"),
            "isp": data.get("isp"),
            "country": data.get("countryName"),
            "is_whitelisted": data.get("isWhitelisted")
        }
    except RateLimitExceededError as e:
        logger.error(f"Rate limit error: {e}")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"API error: {e}")
        return None
    except KeyError as e:
        logger.error(f"Unexpected API response format: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return None