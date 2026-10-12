# Security baseline

- Argon2 for newly created passwords.
- Legacy PBKDF2 hashes remain verifiable and can be upgraded after login.
- HttpOnly cookie-based session token.
- Short-lived access token.
- Database-side tenant filtering.
- Role checks at API boundaries.
- Audit logging for authentication and important mutations.

Before public launch also add:
- HTTPS-only cookies
- rate limiting/login throttling
- password reset and email verification
- secure upload validation and limits
- security headers
- database backups and restore tests
- dependency/security scanning
- monitoring and alerting
- CSRF strategy for any cross-site cookie mutation flow
