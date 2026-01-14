# PR #1: Core API Endpoints

## 📋 Description
Implements the foundational REST API endpoints for the Card Signal Board application. This PR focuses on the core CRUD operations without observability or testing layers.

## ✨ Changes
- Implemented Card data model with Pydantic validation
- Added 6 RESTful endpoints:
  - `POST /cards` - Create new cards with 7-day TTL
  - `GET /cards` - List all active cards
  - `GET /cards/{id}` - Retrieve specific card
  - `DELETE /cards/{id}/{token}` - Delete card with ownership verification
  - `GET /verify/{token}` - Verify email token ownership
  - `GET /health` - Health check endpoint
- In-memory storage with UUID-based card IDs
- Email validation via Pydantic validators
- Automatic TTL expiration logic

## 🧪 Testing
```bash
# Install dependencies
pip install -r requirements.txt

# Start the server
uvicorn app.main:app --reload

# Test endpoints via interactive docs
open http://localhost:8000/docs
```

## 📝 Example Usage
```bash
# Create a card
curl -X POST http://localhost:8000/cards \
  -H "Content-Type: application/json" \
  -d '{
    "subject": "Math Tutoring",
    "purpose": "help",
    "year": 2,
    "message": "Available for tutoring",
    "email": "student@example.com"
  }'

# List cards
curl http://localhost:8000/cards

# Check health
curl http://localhost:8000/health
```

## ✅ Checklist
- [x] Core API endpoints implemented
- [x] Input validation with Pydantic
- [x] Error handling with proper HTTP status codes
- [x] TTL logic for card expiration
- [x] Token generation and verification
- [ ] (Next PR) Unit tests
- [ ] (Next PR) Prometheus metrics
- [ ] (Next PR) Structured logging

## 🚀 Next Steps
After this PR is merged:
1. PR #2: Add observability (Prometheus metrics + logging)
2. PR #3: Add comprehensive test suite
3. PR #4: Containerization (Dockerfile)
4. PR #5: CI/CD pipeline (GitHub Actions)
