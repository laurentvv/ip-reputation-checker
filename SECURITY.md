# Security Policy

## Supported Versions

We provide security updates for the following versions:

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | ✅                 |

## Reporting a Vulnerability

If you discover a security vulnerability, please report it to us using the following process:

1. **Do not open a public issue** - this could put the community at risk
2. Contact the maintainers directly at: laurentvv@gmail.com
3. Include as much information as possible about the vulnerability
4. Allow time for the issue to be addressed before making any information public

## Security Measures

This project implements several security measures:

- **API Key Protection**: Uses python-dotenv for secure API key management
- **Input Validation**: Validates IPv4 addresses before processing
- **SQL Injection Prevention**: Uses parameterized queries for all database operations
- **Rate Limiting**: Implements rate limiting for API calls to prevent abuse

## Best Practices

- Keep your AbuseIPDB API key secure and never commit it to version control
- Regularly update dependencies using `uv sync --upgrade`
- Monitor API usage to stay within rate limits

## Security Updates

Security updates are released as needed. Users will be notified through GitHub releases.