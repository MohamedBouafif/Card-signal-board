import pytest
from fastapi.testclient import TestClient
from app.main import app, cards_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def cleanup_db():
    """Clear database before each test for isolation"""
    cards_db.clear()
    yield
    cards_db.clear()

class TestCardCreation:
    def test_create_card_success(self):
        """Test successful card creation"""
        payload = {
            "subject": "Math Tutoring",
            "purpose": "help",
            "year": 2,
            "message": "Available for tutoring",
            "email": "student@example.com"
        }
        response = client.post("/cards", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["subject"] == "Math Tutoring"
        assert "id" in data
        assert "token" in data
        assert "created_at" in data
        assert "expires_at" in data

    def test_create_card_invalid_email(self):
        """Test card creation with invalid email"""
        payload = {
            "subject": "Test",
            "purpose": "help",
            "year": 1,
            "message": "Test message",
            "email": "not-an-email"
        }
        response = client.post("/cards", json=payload)
        assert response.status_code == 422

    def test_create_card_missing_fields(self):
        """Test card creation with missing fields"""
        payload = {
            "subject": "Test",
            "purpose": "help"
        }
        response = client.post("/cards", json=payload)
        assert response.status_code == 422

class TestCardRetrieval:
    def test_list_cards_empty(self):
        """Test listing cards when empty"""
        response = client.get("/cards")
        assert response.status_code == 200
        assert response.json() == []

    def test_list_cards_with_data(self):
        """Test listing active cards"""
        payload = {
            "subject": "Physics",
            "purpose": "study_group",
            "year": 3,
            "message": "Join our study group",
            "email": "group@example.com"
        }
        create_response = client.post("/cards", json=payload)
        card_id = create_response.json()["id"]

        list_response = client.get("/cards")
        assert list_response.status_code == 200
        cards = list_response.json()
        assert len(cards) == 1
        assert cards[0]["id"] == card_id

    def test_get_card_success(self):
        """Test retrieving specific card"""
        payload = {
            "subject": "CS101",
            "purpose": "project",
            "year": 1,
            "message": "Team project resources",
            "email": "team@example.com"
        }
        create_response = client.post("/cards", json=payload)
        card_id = create_response.json()["id"]

        get_response = client.get(f"/cards/{card_id}")
        assert get_response.status_code == 200
        assert get_response.json()["id"] == card_id

    def test_get_card_not_found(self):
        """Test retrieving non-existent card"""
        response = client.get("/cards/invalid-id")
        assert response.status_code == 404

class TestCardDeletion:
    def test_delete_card_success(self):
        """Test successful card deletion with valid token"""
        payload = {
            "subject": "Delete Test",
            "purpose": "test",
            "year": 1,
            "message": "Test deletion",
            "email": "delete@example.com"
        }
        create_response = client.post("/cards", json=payload)
        card_id = create_response.json()["id"]
        token = create_response.json()["token"]

        delete_response = client.delete(f"/cards/{card_id}/{token}")
        assert delete_response.status_code == 200
        assert "deleted" in delete_response.json()["message"].lower()

    def test_delete_card_invalid_token(self):
        """Test deletion with invalid token"""
        payload = {
            "subject": "Auth Test",
            "purpose": "test",
            "year": 1,
            "message": "Test auth",
            "email": "auth@example.com"
        }
        create_response = client.post("/cards", json=payload)
        card_id = create_response.json()["id"]

        delete_response = client.delete(f"/cards/{card_id}/wrong-token")
        assert delete_response.status_code == 403

    def test_delete_card_not_found(self):
        """Test deletion of non-existent card"""
        response = client.delete("/cards/invalid-id/token")
        assert response.status_code == 403

class TestTokenVerification:
    def test_verify_token_success(self):
        """Test successful token verification"""
        payload = {
            "subject": "Token Test",
            "purpose": "verify",
            "year": 2,
            "message": "Test token",
            "email": "verify@example.com"
        }
        create_response = client.post("/cards", json=payload)
        token = create_response.json()["token"]
        card_id = create_response.json()["id"]

        verify_response = client.get(f"/verify/{token}")
        assert verify_response.status_code == 200
        data = verify_response.json()
        assert data["verified"] is True
        assert data["card_id"] == card_id
        assert data["email"] == "verify@example.com"

    def test_verify_token_not_found(self):
        """Test verification with invalid token"""
        response = client.get("/verify/invalid-token-xyz")
        assert response.status_code == 404

class TestObservability:
    def test_metrics_endpoint(self):
        """Test metrics endpoint returns Prometheus format"""
        response = client.get("/metrics")
        assert response.status_code == 200
        assert b"card_requests_total" in response.content
        assert b"card_response_seconds" in response.content

    def test_health_endpoint(self):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "timestamp" in data
