# OpenTransit

Open source transit ticketing system built with Python/FastAPI microservices.

## Table of Contents

- [Overview](#overview)
- [Tech Stack](#tech-stack)
- [Getting Started](#getting-started)
- [Project Structure](#project-structure)
- [API Documentation](#api-documentation)
- [Contributing](#contributing)
- [License](#license)

## Overview

OpenTransit is an open-source transit ticketing platform designed to make public transportation ticketing accessible, scalable, and easy to operate. It follows a microservices architecture to allow independent deployment and scaling of each component.

## Tech Stack

- **Language:** [Python 3.11+](https://www.python.org/downloads/)
- **API Framework:** [FastAPI](https://fastapi.tiangolo.com/)
- **Data Validation:** [Pydantic](https://docs.pydantic.dev/)
- **Database ORM:** [SQLAlchemy](https://docs.sqlalchemy.org/)
- **Async Server:** [Uvicorn](https://www.uvicorn.org/)
- **Containerization:** [Docker](https://docs.docker.com/)
- **Orchestration:** [Docker Compose](https://docs.docker.com/compose/)

## Getting Started

### Prerequisites

- [Python 3.11+](https://www.python.org/downloads/)
- [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/install/)

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/ramanlameika/OpenTransit.git
   cd OpenTransit
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Start services with Docker Compose:

   ```bash
   docker compose up --build
   ```

## Project Structure

```
OpenTransit/
├── services/
│   ├── ticketing/      # Ticket issuance and validation service
│   ├── auth/           # Authentication and authorization service
│   ├── routes/         # Transit routes and schedules service
│   └── payments/       # Payment processing service
├── docker-compose.yml
└── README.md
```

## API Documentation

Once the services are running, interactive API documentation is automatically available via:

- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

FastAPI generates these docs from the OpenAPI specification. See the [FastAPI documentation](https://fastapi.tiangolo.com/tutorial/first-steps/) for more details.

## Contributing

Contributions are welcome! Please open an [issue](https://github.com/ramanlameika/OpenTransit/issues) or submit a [pull request](https://github.com/ramanlameika/OpenTransit/pulls).

Before contributing, please review the [GitHub Flow](https://docs.github.com/en/get-started/using-github/github-flow) guide.

## License

This project is licensed under the [MIT License](https://github.com/ramanlameika/OpenTransit/blob/main/LICENSE).
