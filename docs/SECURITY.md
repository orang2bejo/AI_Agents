# Security Documentation

This document provides comprehensive information about the security features, modes, and configurations available in the Windows Use Autonomous Agent.

## Table of Contents

1. [Security Overview](#security-overview)
2. [Security Levels](#security-levels)
3. [Domain Allowlist](#domain-allowlist)
4. [Guardrails Engine](#guardrails-engine)
5. [Action Types & Validation](#action-types--validation)
6. [Configuration](#configuration)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)

## Security Overview

The Windows Use Autonomous Agent implements a multi-layered security system designed to protect against malicious operations while maintaining functionality for legitimate automation tasks.

### Core Security Components

- **Guardrails Engine**: Validates all actions before execution
- **Domain Allowlist**: Controls web access to trusted domains only
- **Rate Limiting**: Prevents abuse through request throttling
- **Audit Logging**: Tracks all security-related events
- **Human-in-the-Loop (HITL)**: Requires human approval for sensitive operations

## Security Levels

The system supports four security levels that determine the strictness of validation:

### LOW
- **Use Case**: Development and testing environments
- **Restrictions**: Minimal validation, most operations allowed
- **Risk**: High - suitable only for isolated environments
- **Example Operations**: Basic file operations, simple commands

### MEDIUM (Default)
- **Use Case**: Standard production environments
- **Restrictions**: Balanced security with functionality
- **Risk**: Moderate - good for most use cases
- **Example Operations**: Office automation, safe file operations

### HIGH
- **Use Case**: Sensitive environments with valuable data
- **Restrictions**: Strict validation, requires confirmation for many operations
- **Risk**: Low - enhanced protection
- **Example Operations**: Limited file access, restricted commands

### CRITICAL
- **Use Case**: High-security environments, financial systems
- **Restrictions**: Maximum security, minimal automated operations
- **Risk**: Very Low - maximum protection
- **Example Operations**: Read-only operations, heavily restricted access

### Setting Security Level

```python
from windows_use.security import GuardrailsEngine, SecurityLevel

engine = GuardrailsEngine()
engine.set_security_level(SecurityLevel.HIGH)
```

## Domain Allowlist

The domain allowlist controls which websites and web services the agent can access during web automation tasks.

### Default Allowed Domains

The system comes with a curated list of trusted domains:

- `github.com` - Code repositories and documentation
- `stackoverflow.com` - Programming help and solutions
- `python.org` - Python documentation and packages
- `microsoft.com` - Microsoft services and documentation
- `google.com` - Search and Google services
- `openai.com` - AI services and documentation
- `huggingface.co` - AI models and datasets
- `pypi.org` - Python package index

### Managing Domain Allowlist

#### Adding Domains
```python
engine = GuardrailsEngine()
engine.add_allowed_domain("example.com")
engine.add_allowed_domain("api.service.com")
```

#### Removing Domains
```python
engine.remove_allowed_domain("example.com")
```

#### Checking Domain Status
```python
if engine.is_domain_allowed("github.com"):
    print("Domain is allowed")
```

#### Listing All Allowed Domains
```python
allowed = engine.get_allowed_domains()
print(f"Allowed domains: {allowed}")
```

#### Clearing All Domains
```python
engine.clear_allowed_domains()  # Use with caution!
```

### Domain Validation Rules

1. **Case Insensitive**: Domains are stored and compared in lowercase
2. **Exact Match**: Subdomains must be explicitly allowed
3. **Protocol Agnostic**: HTTP and HTTPS are both controlled by the same allowlist
4. **Wildcard Support**: Not currently supported (planned for future release)

## Guardrails Engine

The Guardrails Engine is the core security component that validates all actions before execution.

### Supported Action Types

| Action Type | Description | Default Security Level |
|-------------|-------------|------------------------|
| `FILE_READ` | Reading files from disk | LOW |
| `FILE_WRITE` | Writing/creating files | MEDIUM |
| `FILE_DELETE` | Deleting files | HIGH |
| `SYSTEM_COMMAND` | Executing system commands | HIGH |
| `OFFICE_AUTOMATION` | Office application automation | MEDIUM |
| `NETWORK_ACCESS` | Web requests and downloads | MEDIUM |
| `REGISTRY_ACCESS` | Windows registry operations | CRITICAL |
| `PROCESS_CONTROL` | Starting/stopping processes | HIGH |

### Validation Process

1. **Rate Limit Check**: Ensures request frequency is within limits
2. **Action Type Validation**: Validates based on specific action rules
3. **Security Level Assessment**: Determines risk level
4. **Confirmation Requirement**: Flags operations requiring human approval
5. **Audit Logging**: Records all validation results

### Example Usage

```python
from windows_use.security import GuardrailsEngine, ActionType

engine = GuardrailsEngine()

# Validate file operation
result = engine.validate_action(
    ActionType.FILE_WRITE,
    {"file_path": "C:\\Users\\user\\document.txt"}
)

if result.allowed:
    print(f"Operation allowed: {result.reason}")
else:
    print(f"Operation blocked: {result.reason}")
    print(f"Recommendations: {result.recommendations}")
```

## Action Types & Validation

### File Operations

#### Protected Directories
The following directories are protected from write/delete operations:
- `C:\Windows`
- `C:\Program Files`
- `C:\Program Files (x86)`
- `C:\System32`
- `C:\Users\All Users`

#### Blocked File Extensions
Executable and script files are blocked by default:
- `.exe`, `.bat`, `.cmd`, `.ps1`
- `.vbs`, `.scr`, `.com`, `.pif`

#### Safe Directories
Operations in these directories are generally allowed:
- User home directory (`~`)
- `Documents`, `Desktop`, `Downloads`
- Project directory (`D:\Project Jarvis`)

### System Commands

#### Allowed Commands
- `dir`, `ls`, `pwd`, `cd`
- `type`, `cat`, `echo`
- `find`, `grep`

#### Blocked Commands
- `format`, `del`, `rm`, `rmdir`
- `shutdown`, `restart`
- `net`, `sc`, `reg`, `regedit`
- `taskkill`, `wmic`

### Network Operations

All network operations are subject to domain allowlist validation. Operations to non-allowed domains will be blocked.

## Configuration

### Configuration File

Create a JSON configuration file to customize security settings:

```json
{
  "max_file_size_mb": 100,
  "allowed_file_extensions": [
    ".txt", ".docx", ".xlsx", ".pdf"
  ],
  "blocked_file_extensions": [
    ".exe", ".bat", ".cmd"
  ],
  "protected_directories": [
    "C:\\Windows",
    "C:\\Program Files"
  ],
  "rate_limit_requests_per_minute": 60,
  "rate_limit_window_seconds": 60,
  "default_allowed_domains": [
    "github.com",
    "stackoverflow.com"
  ]
}
```

### Loading Configuration

```python
engine = GuardrailsEngine(config_path="path/to/security_config.json")
```

### Environment Variables

Set security level via environment variable:

```bash
set SECURITY_LEVEL=high
```

## Best Practices

### For Developers

1. **Always Validate**: Never bypass security validation
2. **Principle of Least Privilege**: Use the highest appropriate security level
3. **Regular Audits**: Review audit logs regularly
4. **Domain Management**: Keep allowlist minimal and up-to-date
5. **Configuration Management**: Use version control for security configs

### For System Administrators

1. **Monitor Logs**: Set up log monitoring and alerting
2. **Regular Updates**: Keep security rules updated
3. **Access Control**: Limit who can modify security settings
4. **Backup Configs**: Maintain backups of security configurations
5. **Incident Response**: Have procedures for security violations

### For End Users

1. **Understand Prompts**: Read confirmation prompts carefully
2. **Report Issues**: Report suspicious behavior immediately
3. **Follow Policies**: Adhere to organizational security policies
4. **Regular Training**: Stay updated on security best practices

## Troubleshooting

### Common Issues

#### "Domain not allowed" Error
**Problem**: Web automation fails with domain restriction
**Solution**: Add the domain to allowlist or contact administrator

```python
engine.add_allowed_domain("required-domain.com")
```

#### "Rate limit exceeded" Error
**Problem**: Too many requests in short time
**Solution**: Wait and retry, or adjust rate limits

```python
engine.clear_rate_limits()  # Emergency reset
```

#### "Protected directory" Error
**Problem**: Cannot write to system directories
**Solution**: Use user directories or request elevated permissions

#### "Security level too restrictive" Error
**Problem**: Operations blocked by high security level
**Solution**: Lower security level if appropriate

```python
engine.set_security_level(SecurityLevel.MEDIUM)
```

### Debugging

#### Enable Debug Logging
```python
import logging
logging.getLogger('windows_use.security').setLevel(logging.DEBUG)
```

#### Check Security Status
```python
status = engine.get_security_status()
print(f"Current security level: {status['security_level']}")
print(f"Allowed domains: {status['allowed_domains_count']}")
print(f"Rate limits: {status['rate_limits']}")
```

#### Review Audit Log
```python
audit_log = engine.get_audit_log(limit=50)
for entry in audit_log:
    print(f"{entry['timestamp']}: {entry['action_type']} - {entry['allowed']}")
```

### Getting Help

If you encounter security issues:

1. Check this documentation
2. Review audit logs for details
3. Consult system administrator
4. Report bugs to development team
5. Check project documentation at `docs/`

---

**Note**: Security is an ongoing process. Regularly review and update your security configuration based on your organization's needs and threat landscape.