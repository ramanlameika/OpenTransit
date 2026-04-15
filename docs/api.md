# OpenTransit API Reference

All services return JSON. Errors follow the format:
```json
{"detail": "Error message"}
```

---

## Auth Service — port 8001

### `GET /health`
Returns service health status.

**Response 200**
```json
{"status": "ok", "service": "auth"}
```

---

### `POST /auth/register`
Register a new user.

**Request body**
```json
{
  "email": "alice@example.com",
  "password": "Password123!",
  "full_name": "Alice Smith"
}
```

**Response 201**
```json
{
  "id": "uuid",
  "email": "alice@example.com",
  "full_name": "Alice Smith",
  "created_at": "2024-01-01T00:00:00"
}
```

**Errors**: `409 Conflict` — email already registered.

---

### `POST /auth/login`
Authenticate and receive a JWT.

**Request body**
```json
{
  "email": "alice@example.com",
  "password": "Password123!"
}
```

**Response 200**
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```

**Errors**: `401 Unauthorized` — invalid credentials.

---

### `GET /auth/me`
Get the currently authenticated user.

**Headers**: `Authorization: Bearer <token>`

**Response 200**
```json
{
  "id": "uuid",
  "email": "alice@example.com",
  "full_name": "Alice Smith",
  "created_at": "2024-01-01T00:00:00"
}
```

**Errors**: `401 Unauthorized`, `403 Forbidden` — missing or invalid token.

---

## Ticketing Service — port 8002

### `GET /health`
```json
{"status": "ok", "service": "ticketing"}
```

### `GET /tickets`
List all tickets.

**Response 200** — array of ticket objects.

---

### `POST /tickets`
Create a new ticket.

**Request body**
```json
{
  "route_id": "R1",
  "passenger_id": "P1",
  "ticket_type": "single"
}
```
`ticket_type` values: `single`, `day_pass`, `weekly`, `monthly`

**Response 201**
```json
{
  "id": "uuid",
  "route_id": "R1",
  "passenger_id": "P1",
  "ticket_type": "single",
  "status": "active",
  "created_at": "2024-01-01T00:00:00",
  "validated_at": null
}
```

---

### `GET /tickets/{ticket_id}`
Get a single ticket.

**Response 200** — ticket object. **Errors**: `404`.

---

### `POST /tickets/{ticket_id}/validate`
Mark a ticket as validated (e.g., on boarding).

**Response 200** — ticket with `status: "validated"` and `validated_at` set.

**Errors**: `404`, `400 Bad Request` — ticket not in `active` status.

---

## Fare Service — port 8003

### `GET /health`
```json
{"status": "ok", "service": "fare"}
```

### `GET /fares`
List all fare records.

---

### `POST /fares`
Create a fare rule.

**Request body**
```json
{
  "route_id": "R1",
  "fare_type": "standard",
  "amount": 2.50
}
```
`fare_type` values: `standard`, `concession`, `child`, `senior`

**Response 201**
```json
{
  "id": "uuid",
  "route_id": "R1",
  "fare_type": "standard",
  "amount": 2.50,
  "created_at": "2024-01-01T00:00:00"
}
```

**Errors**: `400` — negative amount.

---

### `GET /fares/{route_id}`
Get all fares for a route.

**Response 200** — array of fare objects. **Errors**: `404` — no fares for route.

---

## Agency Service — port 8004

### `GET /health`
```json
{"status": "ok", "service": "agency"}
```

### `GET /agencies`
List all agencies.

---

### `POST /agencies`
Create an agency.

**Request body**
```json
{
  "name": "City Transit",
  "region": "Downtown",
  "contact_email": "admin@citytransit.com"
}
```

**Response 201**
```json
{
  "id": "uuid",
  "name": "City Transit",
  "region": "Downtown",
  "contact_email": "admin@citytransit.com",
  "created_at": "2024-01-01T00:00:00"
}
```

---

### `GET /agencies/{agency_id}`
Get a single agency. **Errors**: `404`.

---

### `GET /agencies/{agency_id}/routes`
List routes operated by the agency.

**Response 200** — array of route objects. **Errors**: `404` — agency not found.

---

## Payment Service — port 8005

### `GET /health`
```json
{"status": "ok", "service": "payment"}
```

### `POST /payments`
Create a payment for a ticket.

**Request body**
```json
{
  "ticket_id": "uuid",
  "amount": 2.50,
  "method": "card"
}
```
`method` values: `card`, `wallet`, `bank_transfer`

**Response 201**
```json
{
  "id": "uuid",
  "ticket_id": "uuid",
  "amount": 2.50,
  "method": "card",
  "status": "completed",
  "created_at": "2024-01-01T00:00:00",
  "refunded_at": null
}
```

**Errors**: `400` — amount must be positive.

---

### `GET /payments/{payment_id}`
Get payment status. **Errors**: `404`.

---

### `POST /payments/{payment_id}/refund`
Refund a completed payment.

**Response 200** — payment with `status: "refunded"` and `refunded_at` set.

**Errors**: `404`, `400` — payment already refunded or not in `completed` state.
