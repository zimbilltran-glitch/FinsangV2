# Project Technical Scoring Rubric (0-100)

Calculate the final score by summing the points across these four categories. A score below 70 indicates the project is NOT ready for production.

## 1. Technical Architecture (Max 30 points)
- **[30/30]** Bulletproof design: Microservices/Modular monolith well-defined, strict separation of concerns, high cohesion, low coupling, correct usage of design patterns.
- **[20/30]** Good design: Clean architecture but some minor tech debt or tightly coupled components.
- **[10/30]** Acceptable: Monolithic, somewhat messy, lacks clear boundaries but functions.
- **[0/30]** Spaghetti code: No discernible architecture, massive god classes, logic mixed into views/controllers.

## 2. Security & Data Integrity (Max 30 points)
- **[30/30]** Ironclad: Passes all FinTech production standards (encryption, proper hashing, OWASP mitigated, full audit trails, strict ACID transactions).
- **[20/30]** Strong: Standard web security practices followed (HTTPS, parameterized queries, basic auth), but lacks specific financial-grade controls (e.g., idempotency keys missing).
- **[10/30]** Vulnerable: Only basic security present; glaring holes like missing rate limiting or weak password policies.
- **[0/30]** Critical Risk: SQL injection possible, plaintext passwords, no authorization checks on resource access.

## 3. Production Readiness (Max 25 points)
- **[25/25]** Ready to ship: Comprehensive error handling, detailed logging, CI/CD pipeline defined, monitoring/alerting hooks in place, robust test coverage (unit/integration).
- **[15/25]** Almost there: Has error handling and basic logging, tests cover happy paths only, deployment is partially manual.
- **[5/25]** Proof of Concept: Bare minimum error handling, prints/console.logs instead of real logging, zero tests.
- **[0/25]** Development only: Fails to build or run consistently across environments.

## 4. Workflow Efficiency & Tooling (Max 15 points)
- **[15/15]** Highly Optimized: Excellent use of prompts, automated linting/formatting, logical split of tasks, DRY code principles strictly adhered to.
- **[10/15]** Standard: Good use of tools, some manual repetitive tasks remain, decent prompt construction.
- **[5/15]** Cluttered: Poor file organization, redundant code blocks, inefficient communication with agent.
- **[0/15]** Chaotic: No version control conventions, unstructured messy workspace.
