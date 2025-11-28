# IP Reputation Checker

A modern IP reputation checking tool that leverages AI and multiple API integrations to verify the quality of IPv4 addresses.

## Features

- AI-powered IP reputation analysis using Ollama
- Integration with AbuseIPDB API for threat intelligence
- Multiple reputation sources (VirusTotal, Cisco Talos, MXToolbox, etc.)
- Caching mechanism using DuckDB for improved performance
- FastAPI-based web interface
- Command-line interface for batch operations

## Requirements

- Python 3.13.9 (recommended due to grpcio compatibility issues with Python 3.14)
- Ollama with a compatible model (e.g., qwen3:latest)
- AbuseIPDB API key

## Installation

1. Install uv if you haven't already:
```bash
pip install uv
```

2. Clone the repository and navigate to the project directory:
```bash
git clone <repository-url>
cd ip-reputation-checker
```

3. Create a `.env` file with your AbuseIPDB API key:
```env
ABUSEIPDB_API_KEY="your_api_key_here"
```

4. Create a virtual environment with Python 3.13.9 (required for grpcio compatibility):
```bash
uv venv --python 3.13
```

5. Install dependencies using uv:
```bash
uv sync
```
## Usage

### Prerequisites

If you encounter issues with grpcio compilation, ensure you're using Python 3.13.9 in your virtual environment as there are known compatibility issues with Python 3.14. You can verify your Python version in the activated virtual environment with `python --version`.


### Command Line Interface

```bash
uv run python -m src.main <ip_address>
```

### Web API

Start the API server:
```bash
uv run python -m src.api
```

Then access the API at `http://localhost:8000`:
- GET `/check-ip/?ip_address=<ip_address>` - Check IP reputation

### Example

```bash
uv run python -m src.main 8.8.8.8
```

## Architecture

The project follows a modular architecture with the following components after refactoring to address code review issues:

- `src/core/` - Core logic for IP validation and analysis
- `src/models/` - AI model integration and management
- `src/api/` - FastAPI endpoints
- `src/database/` - Database operations and caching
- `src/tools/` - Utility functions and external API integrations
- `src/services/` - Centralized IP checking service to eliminate code duplication
- `src/exceptions/` - Standardized exception classes for error handling
- `config/settings.py` - Configuration management for URLs and parameters
- `src/cli/` - Command-line interface

## Key Improvements

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

### API Enhancements
- Updated to use shared `RateLimitExceededError` from abuseipdb_tool.py
- Improved error handling and response consistency

## Configuration

The project uses a configuration system through `config/settings.py` which supports environment variables via the `.env` file. Key settings include:
- Database path (`DB_PATH`)
- Ollama settings (`OLLAMA_API_BASE`, `OLLAMA_MODEL_NAME`, etc.)
- AbuseIPDB API key (`ABUSEIPDB_API_KEY`)
- Service URLs (`VIRUSTOTAL_URL`, `ABUSEIPDB_CHECK_URL`, etc.)
- Analysis thresholds (`ABUSE_CONFIDENCE_THRESHOLD`)