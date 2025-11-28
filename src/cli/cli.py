"""
Command-line interface for IP reputation checking.

This module provides a command-line interface for checking IP address
reputation using AI and API integrations.
"""

import argparse
import sys
import logging
from typing import Optional

from src.core.ip_validator import analyze_ip_quality, is_valid_ipv4
from src.services.ip_check_service import IPCheckService
from src.tools.abuseipdb_tool import check_ip_abuseipdb

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def display_results(ip: str, reputation: Optional[str], execution_time: float, full_response: str):
    """
    Display the IP reputation check results in a formatted way.

    Args:
        ip: The IP address that was checked
        reputation: The reputation result ('GOOD' or 'BAD')
        execution_time: Time taken for the check in seconds
        full_response: Complete response from the AI agent
    """
    separator = "="*60
    print(f"\n{separator}")
    print("IP REPUTATION CHECK RESULTS")
    print(separator)
    print(f"IP Address: {ip}")
    print(f"Reputation: {reputation or 'N/A'}")
    print(f"Execution Time: {execution_time:.2f} seconds")
    print("-"*60)
    print("Full AI Response:")
    print(full_response)
    print(separator)

    # Log the same information
    logger.info(f"IP REPUTATION CHECK RESULTS")
    logger.info(f"IP Address: {ip}")
    logger.info(f"Reputation: {reputation or 'N/A'}")
    logger.info(f"Execution Time: {execution_time:.2f} seconds")
    logger.info(f"Full AI Response: {full_response}")


def display_ip_analysis(analysis: dict):
    """
    Display IP quality analysis results.

    Args:
        analysis: Dictionary containing IP quality analysis data
    """
    print("\nIP Quality Analysis:")
    print(f"  Valid IPv4: {analysis['valid']}")
    logger.info(f"IP Quality Analysis - Valid: {analysis['valid']}")

    if analysis['valid']:
        print(f"  Private IP: {analysis['is_private']}")
        print(f"  Quality Score: {analysis['quality_score']}/100")
        print(f"  Reserved IP: {analysis['is_reserved']}")
        print(f"  Loopback IP: {analysis['is_loopback']}")
        print(f"  Link-local IP: {analysis['is_link_local']}")
        print(f"  Multicast IP: {analysis['is_multicast']}")

        logger.info(f"IP Quality Analysis - Private: {analysis['is_private']}")
        logger.info(f"IP Quality Analysis - Quality Score: {analysis['quality_score']}/100")
        logger.info(f"IP Quality Analysis - Reserved: {analysis['is_reserved']}")
        logger.info(f"IP Quality Analysis - Loopback: {analysis['is_loopback']}")
        logger.info(f"IP Quality Analysis - Link-local: {analysis['is_link_local']}")
        logger.info(f"IP Quality Analysis - Multicast: {analysis['is_multicast']}")
    else:
        logger.warning(f"Invalid IP address: {analysis.get('ip', 'Unknown')}")
        logger.warning(f"Error: {analysis.get('error', 'Unknown error')}")


def main():
    """Main CLI function to execute the IP reputation checker."""
    parser = argparse.ArgumentParser(
        description="Check IP reputation using AI and API integrations"
    )
    parser.add_argument(
        "ip_address", 
        help="The IP address to check"
    )
    parser.add_argument(
        "--no-cache", 
        action="store_true",
        help="Skip database cache and perform fresh check"
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Only validate the IP address without reputation check"
    )
    parser.add_argument(
        "--abuseipdb-only",
        action="store_true",
        help="Only check using AbuseIPDB API"
    )
    
    args = parser.parse_args()
    ip_address = args.ip_address
    
    # Validate IP format first
    if not is_valid_ipv4(ip_address):
        logger.error(f"Invalid IPv4 address format: {ip_address}")
        sys.exit(1)
    
    # Perform IP quality analysis
    analysis = analyze_ip_quality(ip_address)
    display_ip_analysis(analysis)
    
    if args.validate_only:
        return
    
    # Initialize components
    service = IPCheckService()
    
    # Check if we should skip if reputation is already BAD in database
    if not args.no_cache and not args.abuseipdb_only:
        if service.db_manager.is_bad_ip(ip_address):
            print(f"\nIP {ip_address} found in database with BAD reputation - Skipping further checks")
            print("Use --no-cache to override this behavior")
            logger.info(f"IP {ip_address} found in database with BAD reputation - Skipping further checks")
            return
    
    # Perform reputation check based on options
    if args.abuseipdb_only:
        print(f"\nChecking {ip_address} using AbuseIPDB API...")
        logger.info(f"Checking {ip_address} using AbuseIPDB API...")
        result = check_ip_abuseipdb(ip_address)

        if result:
            print(f"Abuse Confidence Score: {result['abuse_confidence_score']}")
            print(f"Total Reports: {result['total_reports']}")
            print(f"ISP: {result['isp']}")
            print(f"Country: {result['country']}")
            print(f"Last Reported: {result['last_reported_at']}")

            logger.info(f"Abuse Confidence Score: {result['abuse_confidence_score']}")
            logger.info(f"Total Reports: {result['total_reports']}")
            logger.info(f"ISP: {result['isp']}")
            logger.info(f"Country: {result['country']}")
            logger.info(f"Last Reported: {result['last_reported_at']}")
        else:
            print("Could not retrieve data from AbuseIPDB")
            logger.warning(f"Could not retrieve data from AbuseIPDB for IP {ip_address}")
    
    else:
        print(f"\nChecking {ip_address} using AI agent...")
        logger.info(f"Checking {ip_address} using AI agent...")

        # Perform the check using the centralized service
        reputation, execution_time, full_response = service.run_check(ip_address)

        # Display results
        display_results(ip_address, reputation, execution_time, full_response)

        # The service already handles storing the results in the database
        logger.info(f"Completed check for {ip_address}, reputation: {reputation}")


if __name__ == "__main__":
    main()