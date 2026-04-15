# OpenTransit

Open source transit ticketing system built with Python/FastAPI microservices.

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Getting Started](#getting-started)
- [API Documentation](#api-documentation)
- [Security](#security)
- [Contributing](#contributing)
- [License](#license)

## Overview

OpenTransit is an open source transit ticketing platform designed for public transportation operators. It provides a scalable, microservices-based backend for managing routes, tickets, users, and payments.

## Architecture

The system is composed of independent Python/FastAPI microservices:

| Service | Responsibility |
|---|---|
| `auth-service` | User authentication and authorization (JWT/OAuth2) |
| `ticket-service` | Ticket issuance, validation, and lifecycle management |
| `route-service` | Transit route and schedule management |
| `payment-service` | Payment processing and transaction records |
| `notification-service` | Email/SMS notifications to passengers |

Services communicate over HTTP/REST and are deployed behind an API gateway. Each service maintains its own database to enforce bounded contexts.

## Getting Started

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- PostgreSQL 15+

### Local Development

```bash
# Clone the repository
git clone https://github.com/ramanlameika/OpenTransit.git
cd OpenTransit

# Copy environment template and fill in values
cp .env.example .env

# Start all services
docker compose up --build
```

### Environment Variables

| Variable | Description | Required |
|---|---|---|
| `SECRET_KEY` | Secret key for JWT signing (min 32 chars) | Yes |
| `DATABASE_URL` | PostgreSQL connection string | Yes |
| `PAYMENT_API_KEY` | Payment gateway API key | Yes |
| `ALLOWED_ORIGINS` | Comma-separated list of allowed CORS origins | Yes |
| `DEBUG` | Enable debug mode (`false` in production) | No |

> **Warning:** Never commit `.env` files or secrets to version control. Use a secrets manager (e.g., AWS Secrets Manager, HashiCorp Vault) in production.

## API Documentation

Interactive API docs are served by each microservice at `/docs` (Swagger UI) and `/redoc` (ReDoc) when running locally.

Authentication endpoints follow the OAuth2 password flow. All protected routes require a valid Bearer token in the `Authorization` header.

## Security

Security is a first-class concern for a transit ticketing system that handles personal data and payments. Key controls include:

### Authentication & Authorization

- JWT tokens are signed with RS256 (asymmetric keys); private keys are never stored in the repository.
- Tokens have short expiry times (15 minutes for access tokens, 7 days for refresh tokens).
- Role-based access control (RBAC) enforces least-privilege access across all services.
- Passwords are hashed with bcrypt (cost factor ≥ 12).

### Data Protection

- All data in transit is encrypted via TLS 1.2+.
- Sensitive fields (payment card data, government IDs) are encrypted at rest using AES-256.
- The system is designed for GDPR compliance: users can request data export and deletion.
- PCI-DSS scoping is minimized by delegating card processing to a certified payment gateway; raw card data never touches OpenTransit services.

### Input Validation & Injection Prevention

- All API inputs are validated with Pydantic models before processing.
- Parameterized queries (via SQLAlchemy ORM) prevent SQL injection.
- Content Security Policy (CSP) and other security headers are enforced at the API gateway.

### Dependency Management

- Dependencies are pinned to exact versions in `requirements.txt`.
- [Dependabot](https://docs.github.com/en/code-security/dependabot) is enabled to track vulnerable packages.
- Run `pip audit` locally to check for known CVEs before releasing.

### Vulnerability Reporting

Please report security vulnerabilities privately. See [SECURITY.md](SECURITY.md) for the full disclosure policy.

## Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) before submitting a pull request. All contributions must pass CI checks, including linting, unit tests, and a `pip audit` security scan.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
