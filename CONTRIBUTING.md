# Contributing to IP Reputation Checker

Thank you for your interest in contributing to IP Reputation Checker! This document provides guidelines and instructions for contributing to the project.

## Table of Contents
1. [Getting Started](#getting-started)
2. [Development Setup](#development-setup)
3. [Code Style](#code-style)
4. [Testing](#testing)
5. [Pull Request Process](#pull-request-process)
6. [Reporting Issues](#reporting-issues)

## Getting Started

Before contributing, please ensure you have:
- A GitHub account
- Git installed on your system
- Python 3.13.9+ installed
- Ollama running with a compatible model (e.g., qwen3:latest)

## Development Setup

1. Fork the repository on GitHub
2. Clone your fork:
   ```bash
   git clone https://github.com/YOUR_USERNAME/ip-reputation-checker.git
   cd ip-reputation-checker
   ```
3. Create a virtual environment:
   ```bash
   uv venv --python 3.13
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```
4. Install dependencies:
   ```bash
   uv sync
   ```
5. Create a `.env` file with your API keys:
   ```env
   ABUSEIPDB_API_KEY="your_api_key_here"
   ```

## Code Style

- Follow PEP 8 guidelines for Python code
- Use type hints for all function parameters and return values
- Write docstrings for all public functions and classes
- Keep functions focused and avoid excessive complexity
- Use meaningful variable and function names

## Testing

- Write unit tests for new functionality
- Ensure all existing tests pass before submitting changes
- Test manually with various IP addresses to verify functionality

## Pull Request Process

1. Create a new branch for your feature/fix: `git checkout -b feature/your-feature-name`
2. Make your changes and commit them with clear, descriptive messages
3. Run tests to ensure everything works as expected
4. Push your changes to your fork: `git push origin feature/your-feature-name`
5. Create a pull request from your fork to the main repository
6. Fill out the pull request template with a clear description of your changes

## Reporting Issues

When reporting issues, please include:
- A clear, descriptive title
- Steps to reproduce the issue
- Expected behavior vs. actual behavior
- Any relevant error messages
- Your environment details (OS, Python version, etc.)

## Code Review Process

All contributions will be reviewed by project maintainers. Please be patient during the review process and be prepared to make changes based on feedback.

## Questions?

If you have questions about contributing, feel free to open an issue for discussion.