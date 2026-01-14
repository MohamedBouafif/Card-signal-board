# Card-Based Student Signal Board

A lightweight platform where students/teachers create ephemeral "cards" representing academic signals.

## Features
- Create cards with subject, purpose, year, and message
- Email-based ownership verification
- Auto-expiring cards (7-day TTL)
- No user accounts required
- RESTful API

## Tech Stack
- **Backend**: FastAPI (Python)
- **Storage**: In-memory (demo)
- **Observability**: Prometheus metrics
- **Container**: Docker
- **Orchestration**: Kubernetes

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

## API Endpoints
- `POST /cards` - Create new card
- `GET /cards` - List active cards
- `GET /cards/{id}` - Get card details
- `DELETE /cards/{id}/{token}` - Delete card
- `GET /verify/{token}` - Verify card ownership
- `GET /metrics` - Prometheus metrics

## Project Status
🚧 **In Development** - DevOps Learning Project

---
*Built for Cloud & DevOps course - 2025*