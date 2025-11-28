"""
Main module for IP reputation checking.

This module provides a command-line interface for checking IP address
reputation using AI and API integrations.
"""

import time
import argparse
import logging
from src.services.ip_check_service import IPCheckService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Les fonctions create_model, create_agent, setup_database et extract_reputation sont maintenant dans le service IPCheckService


def check_ip_reputation(ip_address: str) -> tuple[str | None, str]:
    """
    Check IP reputation using the centralized IPCheckService
    Returns: (reputation, full_response)
    """
    service = IPCheckService()
    return service.check_ip_reputation(ip_address)


def main():
    """Main function to run IP reputation check"""
    parser = argparse.ArgumentParser(description="Check IP reputation using AI agent.")
    parser.add_argument("ip_address", help="The IP address to check.")
    args = parser.parse_args()

    start_time = time.time()

    # Use the centralized service for checking IP reputation
    service = IPCheckService()
    reputation, service_execution_time, full_response = service.run_check(args.ip_address)

    elapsed_time = time.time() - start_time
    minutes, seconds = divmod(elapsed_time, 60)

    logger.info("--- FINAL RESULT ---")
    logger.info(f"IP Address analyzed: {args.ip_address}")
    logger.info(f"Determined reputation: {reputation}")
    logger.info(f"Full model response:\n{full_response}")
    logger.info(f"Service execution time: {service_execution_time:.2f} seconds")
    logger.info(f"Total execution time: {int(minutes)} min {int(seconds)} sec")


if __name__ == "__main__":
    main()