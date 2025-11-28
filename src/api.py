"""
FastAPI endpoint for IP reputation checking.

This module provides a REST API for checking IP address reputation using
the AbuseIPDB service.
"""

from fastapi import FastAPI, HTTPException, Query
import uvicorn

# Importer la fonction et l'exception du module partagé
from src.tools.abuseipdb_tool import check_ip_abuseipdb
from src.exceptions import RateLimitExceededError

# Initialiser l'application FastAPI
app = FastAPI(
    title="IP Reputation API",
    description="API for checking IP address reputation via AbuseIPDB and AI analysis",
    version="1.0.0"
)

@app.get("/check-ip/")
async def check_ip(ip_address: str = Query(..., description="IP address to check")) -> dict:
    """
    Check IP reputation via AbuseIPDB.

    Returns:
        dict: IP reputation information
    """
    try:
        result = check_ip_abuseipdb(ip_address)
        
        if result is None:
            raise HTTPException(
                status_code=500,
                detail="Error checking IP reputation"
            )
            
        return {
            "ip": ip_address,
            "abuse_confidence_score": result.get("abuse_confidence_score"),
            "last_reported_at": result.get("last_reported_at"),
            "usage_type": result.get("usage_type")
        }
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except RateLimitExceededError as e:
        raise HTTPException(
            status_code=429,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected error: {str(e)}"
        ) from e

@app.get("/health/")
async def health_check() -> dict:
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)