# FinTech Production Standards

## 1. Security (OWASP Top 10 Context)
- **Authentication & Session Management:**
  - All endpoints must require strong authentication unless explicitly public.
  - JWTs must have short expiration times (e.g., 15 mins) and be paired with secure, HttpOnly, SameSite refresh tokens.
  - Rate limiting must be enforced on all login and password reset routes.
- **Data Protection:**
  - PII (Personally Identifiable Information) and financial data (e.g., PANs, SSNs) must be encrypted at rest (AES-256) and in transit (TLS 1.3).
  - Passwords must be hashed using Argon2 or bcrypt with a minimum work factor of 12.
- **Injection Prevention:**
  - Use parameterized queries or safe ORMs exclusively. No dynamic SQL concatenation.

## 2. Database & Architecture Architecture
- **Transaction Integrity:**
  - All financial modifications must happen within ACID-compliant database transactions using proper isolation levels (e.g., SERIALIZABLE or repeatable read for ledger updates).
  - Implement idempotency keys for all state-mutating API requests to prevent double-charging or duplicate entity creation.
- **Performance & Scalability:**
  - Enforce limits on pagination (e.g., max 100 items per request) to prevent resource exhaustion.
  - Crucial queries must have composite indexes supporting the filtering and sorting conditions.
  - Avoid N+1 query patterns; use eager loading or data loaders.

## 3. DevOps & Observability
- **Audit Logging:**
  - Every significant action (login, permission change, monetary transaction) must be recorded in an immutable audit log containing User ID, Action, Timestamp, IP, and Resource ID.
- **Resilience:**
  - Outbound third-party API calls must implement circuit breakers, timeouts, and sensible retry logic with exponential backoff.
