# OpenTransit
Open source transit ticketing system — Python/FastAPI microservices

## Getting Started Locally in VS Code

### Step 1 — Clone the repository
```bash
git clone https://github.com/ramanlameika/OpenTransit.git
```

### Step 2 — Open in VS Code

Open the cloned folder in VS Code. Then set up and run each service:

> Requires **Python 3.11+**.

```bash
cd OpenTransit/services/auth
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001
```

Repeat for each service (`ticketing`, `fare`, `agency`, `payment`) in separate terminals, using ports 8002–8005.

### Step 3 — Run the tests

```bash
# From any service directory:
cd OpenTransit/services/auth
pip install -r requirements.txt
pytest app/tests/ -v
```

Or run all services at once:

```bash
for svc in auth ticketing fare agency payment; do
  echo "=== $svc ===" && cd OpenTransit/services/$svc && pip install -q -r requirements.txt && pytest app/tests/ -q && cd ../..
done
```

## Recommended VS Code Extensions

Install these for the best experience:

- **Python** (`ms-python.python`) — syntax, linting, debugging
- **Pylance** (`ms-python.vscode-pylance`) — type checking
- **REST Client** (`humao.rest-client`) — test APIs from `.http` files
- **Docker** (`ms-azuretools.vscode-docker`) — manage containers
- **Thunder Client** (`rangav.vscode-thunder-client`) — GUI API tester (like Postman)

## Quick API test (no UI needed)

Once a service is running, try this in your browser or with `curl`:

```bash
# Register a user (auth service)
curl -X POST http://localhost:8001/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Password123!","full_name":"Test User"}'

# Login
curl -X POST http://localhost:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Password123!"}'
```

## Documentation

Full documentation is in [`docs/`](docs/) — start with [`architecture.md`](docs/architecture.md) for an overview, then [`api.md`](docs/api.md) for endpoint references.
