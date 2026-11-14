# Security

## Security Model

### Input Validation
- All user text inputs are sanitized via `utils/security.sanitize_input()`
- Script tag stripping, null byte removal, length limits enforced
- File uploads validated by extension AND magic bytes (content inspection)

### File Upload Security
- Extension allowlist: pdf, docx, xlsx, csv, txt, pptx, png, jpg, jpeg
- Magic byte verification prevents extension spoofing
- Size limit enforced (default 10 MB, configurable)
- Path traversal prevention on all file paths

### PII Protection
- `utils/security.detect_pii()` identifies emails, phones, SSNs, credit cards
- `utils/security.mask_pii()` redacts sensitive data before logging
- No PII stored in audit logs (masked)

### Credential Management
- All secrets in environment variables only (`.env` file)
- No credentials in code, session state, or logs
- `.env` in `.gitignore` — never committed
- AWS credentials: standard boto3 chain (env → profile → EC2 IAM role)

### API Security
- Rate limiting via `utils/security.check_rate_limit()` (sliding window)
- Gmail: read-only OAuth scopes only
- AWS: principle of least privilege IAM policy

### Authentication (Phase 2)
- Google OAuth 2.0 for Gmail/Calendar
- AWS Cognito for app authentication (planned)
- Session tokens with configurable expiry

### Audit Trail
- Every AI action logged to AuditRecord
- Every file upload logged with filename and size
- Every user interaction (confirm task, add event) logged
- Audit records include timestamp, user, action, resource, success/error

### Transport Security
- HTTPS enforced in production
- Streamlit `server.cookie_secret` configured
- CORS headers via `ALLOWED_ORIGINS` setting

## Threat Model

| Threat | Mitigation |
|--------|-----------|
| XSS via email body | HTML sanitization in render functions |
| Path traversal in uploads | `is_safe_path()` check |
| File type spoofing | Magic byte validation |
| Credential exposure | Env vars only, no session state |
| Rate abuse of Bedrock | Rate limiting per user |
| PII in logs | `mask_pii()` before logging |
| SSRF via URLs | URL allowlist (Phase 2) |
| Prompt injection | Input length limits, sanitization |

## Security Checklist

- [x] Input sanitization
- [x] File type validation (extension + magic bytes)
- [x] File size limits
- [x] Path traversal prevention
- [x] PII detection and masking
- [x] Rate limiting
- [x] Audit logging
- [x] Credentials in env vars only
- [x] .gitignore for sensitive files
- [ ] HTTPS enforcement (deployment)
- [ ] OAuth token refresh security (Phase 2)
- [ ] Security headers (CSP, HSTS) (Phase 2)
- [ ] Dependency vulnerability scanning (Phase 2)
- [ ] Penetration testing (Phase 2)
