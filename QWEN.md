# IP Reputation Checker - Project Context

## Project Overview

IP Reputation Checker is a modern Python application that leverages AI and multiple API integrations to verify the quality of IPv4 addresses. The project provides a centralized service for IP reputation analysis using AI-powered tools (Ollama) and multiple threat intelligence sources with a modular, maintainable architecture.

**Key Features:**
- AI-powered IP reputation analysis using Ollama
- Integration with AbuseIPDB API for threat intelligence (1000 checks/month for free tier)
- Multiple reputation sources (VirusTotal, Cisco Talos, MXToolbox, etc.)
- Caching mechanism using DuckDB for improved performance
- FastAPI-based web interface
- Command-line interface for batch operations

## Technical Architecture

The project follows a modular architecture with the following key components:

- `src/core/` - Core logic for IP validation and analysis
- `src/models/` - AI model integration and management
- `src/api/` - FastAPI endpoints
- `src/database/` - Database operations and caching
- `src/tools/` - Utility functions and external API integrations
- `src/services/` - Centralized IP checking service to eliminate code duplication
- `src/exceptions/` - Standardized exception classes for error handling
- `config/settings.py` - Configuration management for URLs and parameters
- `src/cli/` - Command-line interface

**Architecture Diagram:**
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   CLI / API     │───▶│  IPCheckService │───▶│  Ollama Agent   │
│                 │    │                  │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                               │
                               ▼
                     ┌──────────────────┐
                     │  DatabaseManager │
                     │  (DuckDB Cache)  │
                     └──────────────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │  External Services  │
                    │ (AbuseIPDB, VT, etc)│
                    └─────────────────────┘
```

## Dependencies & Setup

The project uses `uv` for dependency management with Python 3.13.9+ as the minimum requirement. Key dependencies include:
- `duckdb` - For caching and database operations
- `smolagents[litellm]` - For AI agent integration
- `requests`, `httpx` - For HTTP requests
- `python-dotenv` - For environment variable management
- `fastapi`, `uvicorn` - For the web API
- `pydantic` - For data validation
- Various web scraping and DNS libraries

**Setup Commands:**
```bash
# Install dependencies
uv sync

# Check a single IP address
uv run python -m src.main 8.8.8.8

# Start the API server
uv run python -m src.api
```

## Configuration

The project uses a configuration system through `config/settings.py` which supports environment variables via the `.env` file. Key settings include:
- Database path (`DB_PATH`)
- Ollama settings (`OLLAMA_API_BASE`, `OLLAMA_MODEL_NAME`, etc.)
- AbuseIPDB API key (`ABUSEIPDB_API_KEY`)
- Service URLs (`VIRUSTOTAL_URL`, `ABUSEIPDB_CHECK_URL`, etc.)
- Analysis thresholds (`ABUSE_CONFIDENCE_THRESHOLD`)

## Key Improvements Implemented

### Centralized IP Checking Service
- Created `src/services/ip_check_service.py` to eliminate code duplication between `src/main.py` and `src/models/ollama_agent.py`
- All IP reputation checks now go through the unified `IPCheckService`

### Standardized Error Handling
- Implemented centralized exception management in `src/exceptions.py`
- Uses custom exception classes like `RateLimitExceededError`, `InvalidIPAddressError`, etc.
- Consistent error propagation across all modules

### Configuration Management
- Moved hardcoded URLs and parameters to `config/settings.py`
- Supports environment variables for configuration
- Eliminates hardcoded URLs in prompts

### Database Management
- Unified database operations through `DatabaseManager` class
- Proper resource management with context managers
- Eliminates duplicate database connection logic

## Development Guidelines

- Follow PEP 8 guidelines for Python code
- Use type hints for all function parameters and return values
- Write docstrings for all public functions and classes
- Keep functions focused and avoid excessive complexity
- Use meaningful variable and function names

## Security Considerations

- API Key Protection: Uses python-dotenv for secure API key management
- Input Validation: Validates IPv4 addresses before processing
- SQL Injection Prevention: Uses parameterized queries for all database operations
- Rate Limiting: Implements rate limiting for API calls to prevent abuse

## Rate Limits

The AbuseIPDB API has rate limits that you should be aware of:
- Free tier: 1000 requests per day
- For more information: https://www.abuseipdb.com/api.html
- To register for an API key: https://www.abuseipdb.com/register#individual

## File Structure

- `pyproject.toml` - Project dependencies and metadata
- `README.md` - Main project documentation
- `CONTRIBUTING.md` - Contribution guidelines
- `SECURITY.md` - Security policy
- `IMPLEMENTATION_PLAN.md` - Implementation plan documentation
- `CONFIGURATION_PLAN.md` - Configuration plan
- `src/` - Source code with modular organization
- `config/` - Configuration files (may be ignored by git)
- `.env` - Environment variables (not committed)

## Building and Running

### Requirements
- Python 3.13.9 (recommended due to grpcio compatibility issues with Python 3.14)
- Ollama with a compatible model (e.g., qwen3:latest)
- AbuseIPDB API key

### Commands
```bash
# Install dependencies
uv sync

# Run with CLI
uv run python -m src.main <ip_address>

# Start API server
uv run python -m src.api

# The API serves on http://localhost:8000 by default
# Use endpoint: GET /check-ip/?ip_address=<ip_address>
```