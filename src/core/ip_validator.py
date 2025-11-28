import re
from typing import Optional


def is_valid_ipv4(ip_address: str) -> bool:
    """
    Validate if the provided string is a valid IPv4 address.
    
    Args:
        ip_address (str): The IP address to validate
        
    Returns:
        bool: True if the IP address is valid, False otherwise
    """
    # Regular expression pattern for IPv4 validation
    pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    
    if not re.match(pattern, ip_address):
        return False
    
    # Check each octet is between 0 and 255
    octets = ip_address.split('.')
    for octet in octets:
        value = int(octet)
        if value < 0 or value > 255:
            return False
    
    return True


def is_private_ip(ip_address: str) -> bool:
    """
    Check if the IP address is a private IP address.
    
    Args:
        ip_address (str): The IP address to check
        
    Returns:
        bool: True if the IP is private, False otherwise
    """
    if not is_valid_ipv4(ip_address):
        return False
    
    octets = ip_address.split('.')
    first_octet = int(octets[0])
    second_octet = int(octets[1])
    
    # Private IP ranges:
    # 10.0.0.0 to 10.255.255.255
    if first_octet == 10:
        return True
    
    # 172.16.0.0 to 172.31.255.255
    if first_octet == 172 and 16 <= second_octet <= 31:
        return True
    
    # 192.168.0.0 to 192.168.255.255
    if first_octet == 192 and second_octet == 168:
        return True
    
    # 127.0.0.0 to 127.255.255.255 (localhost)
    if first_octet == 127:
        return True
    
    # 169.254.0.0 to 169.254.255.255 (link-local)
    if first_octet == 169 and second_octet == 254:
        return True
    
    return False


def analyze_ip_quality(ip_address: str) -> dict:
    """
    Analyze the quality of an IPv4 address based on various criteria.
    
    Args:
        ip_address (str): The IP address to analyze
        
    Returns:
        dict: Analysis results with various quality indicators
    """
    if not is_valid_ipv4(ip_address):
        return {
            "valid": False,
            "error": f"Invalid IPv4 address format: {ip_address}",
            "quality_score": 0
        }
    
    is_private = is_private_ip(ip_address)
    
    # Determine quality indicators
    octets = ip_address.split('.')
    first_octet = int(octets[0])
    
    # Quality indicators
    is_reserved = first_octet in [0, 255]  # Reserved addresses
    is_loopback = first_octet == 127  # Loopback addresses
    is_link_local = first_octet == 169 and int(octets[1]) == 254  # Link-local addresses
    is_multicast = 224 <= first_octet <= 239  # Multicast addresses
    
    # Calculate quality score (0-100)
    quality_score = 100
    
    if is_private:
        quality_score -= 30  # Private IPs have lower quality for external checks
    if is_reserved:
        quality_score -= 50  # Reserved IPs are not valid for regular use
    if is_loopback:
        quality_score -= 50  # Loopback addresses are not external
    if is_link_local:
        quality_score -= 40  # Link-local addresses are not routable
    if is_multicast:
        quality_score -= 50 # Multicast addresses are special purpose
    
    # Ensure score doesn't go below 0
    quality_score = max(0, quality_score)
    
    return {
        "valid": True,
        "ip": ip_address,
        "is_private": is_private,
        "is_reserved": is_reserved,
        "is_loopback": is_loopback,
        "is_link_local": is_link_local,
        "is_multicast": is_multicast,
        "quality_score": quality_score
    }