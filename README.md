# Card-Based Student Signal Board

A lightweight platform where students/teachers create ephemeral "cards" representing academic signals.

## Features
- Create cards with subject, purpose, year, and message
- Email-based ownership verification
- Auto-expiring cards (7-day TTL)
- No user accounts required
- RESTful API
- Prometheus metrics for observability
- Structured logging with request tracing
- Docker containerization

## Tech Stack
- **Backend**: FastAPI (Python)
- **Storage**: In-memory (demo)
- **Observability**: Prometheus metrics + structured logging
- **Container**: Docker & Docker Compose
- **Orchestration**: Kubernetes (planned)
- **Testing**: pytest with comprehensive coverage

## Quick Start

### Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run server
uvicorn app.main:app --reload

# Access API docs
open http://localhost:8000/docs
```

### Docker
```bash
# Build
docker build -t card-signal-board .

# Run
docker run -p 8000:8000 card-signal-board
```

### Docker Compose
```bash
# One command setup
docker-compose up --build

# Access at http://localhost:8000/docs
```

## API Endpoints
- `POST /cards` - Create new card
- `GET /cards` - List active cards
- `GET /cards/{id}` - Get card details
- `DELETE /cards/{id}/{token}` - Delete card
- `GET /verify/{token}` - Verify card ownership
- `GET /metrics` - Prometheus metrics
- `GET /health` - Health check

## Pull Request Workflow

This project follows a **contextual PR approach** where each feature is implemented in a dedicated PR.

See [PULL_REQUEST_GUIDE.md](PULL_REQUEST_GUIDE.md) for detailed workflow instructions.

## Development Status

| Phase | Component | Status |
|-------|-----------|--------|
| 1 | Core API | ✅ Complete |
| 2 | Observability | ✅ Complete |
| 3 | Unit Tests | ✅ Complete (14/14 passing) |
| 4 | Containerization | ✅ Complete |
| 5 | CI/CD Pipeline | 🚧 In Progress |
| 6 | Kubernetes | 🚧 Coming Soon |
| 7 | Security Scanning | 🚧 Coming Soon |

## Project Status
🚧 **In Development** - DevOps Learning Project

---
*Built for Cloud & DevOps course - 2025*

## License
MIT
