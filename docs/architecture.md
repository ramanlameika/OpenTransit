# OpenTransit Architecture

## Overview

OpenTransit is an open-source transit ticketing platform built as a set of independent Python/FastAPI microservices. Each service owns its own domain, data, and API surface, communicating over HTTP.

## Tech Stack

- **Language**: Python 3.11+
- **Framework**: FastAPI
- **Validation**: Pydantic v2
- **Authentication**: JWT (python-jose + passlib/bcrypt)
- **Server**: Uvicorn (ASGI)
- **Testing**: pytest + FastAPI TestClient

## Services

| Service    | Port | Responsibility                                      |
|------------|------|-----------------------------------------------------|
| auth       | 8001 | User registration, login, JWT issuance & validation |
| ticketing  | 8002 | Ticket lifecycle: creation, lookup, validation      |
| fare       | 8003 | Fare rules per route and passenger category         |
| agency     | 8004 | Transit agencies and their route definitions        |
| payment    | 8005 | Payment processing and refunds                      |

## Service Responsibilities

### Auth Service (port 8001)
Issues and validates JWT bearer tokens. All other services can verify tokens by decoding the JWT with the shared secret. Stores hashed passwords (bcrypt).

### Ticketing Service (port 8002)
Manages ticket records. A ticket is tied to a route and passenger. Tickets transition through `active → validated → expired/cancelled`. Ticketing queries the fare service to determine pricing (in a full implementation).

### Fare Service (port 8003)
Holds fare rules: how much a ticket costs for a given route and passenger category (standard, concession, child, senior). Consumed by the ticketing and payment services.

### Agency Service (port 8004)
Manages transit agencies and the routes they operate. Route data is referenced by the ticketing and fare services.

### Payment Service (port 8005)
Records payment transactions against a ticket. Supports card, wallet, and bank transfer. Payments can be refunded.

## Service Interaction Diagram

```
Client
  │
  ├─► Auth Service (8001)      ← register / login / verify token
  │
  ├─► Agency Service (8004)    ← list agencies & routes
  │
  ├─► Fare Service (8003)      ← get fare for route
  │
  ├─► Ticketing Service (8002) ← create & validate ticket
  │
  └─► Payment Service (8005)   ← pay for ticket / refund
```

In a production deployment, an API Gateway or service mesh would sit in front of all services and handle token verification, rate limiting, and routing.

## Data Storage

Currently each service uses an in-memory Python dict as its data store. In production, each service would own its own database (e.g., PostgreSQL), following the database-per-service pattern to maintain loose coupling.

## Security

- Passwords are hashed with bcrypt via passlib.
- JWTs are signed with HS256. The secret key should be rotated and injected via environment variable in production.
- In a multi-service deployment, services should validate the JWT on every request or delegate to an API Gateway.
