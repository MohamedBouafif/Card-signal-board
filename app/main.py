from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, field_validator
from datetime import datetime, timedelta
import uuid

# Data Models
class Card(BaseModel):
    subject: str
    purpose: str
    year: int
    message: str
    email: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, v):
        if "@" not in v:
            raise ValueError("Invalid email format")
        return v

# In-memory storage
cards_db = {}

# FastAPI app
app = FastAPI(
    title="Card Signal Board",
    description="Create ephemeral academic signal cards with 7-day TTL"
)

# Helper functions
def generate_token():
    """Generate unique verification token"""
    return str(uuid.uuid4())

def is_expired(expires_at: str) -> bool:
    """Check if card has expired"""
    return datetime.fromisoformat(expires_at) < datetime.utcnow()

# Routes

@app.post("/cards", response_model=dict, status_code=201)
async def create_card(card: Card):
    """Create a new card with 7-day TTL"""
    card_id = str(uuid.uuid4())
    token = generate_token()
    now = datetime.utcnow()
    expires_at = (now + timedelta(days=7)).isoformat()
    
    cards_db[card_id] = {
        **card.model_dump(),
        "id": card_id,
        "token": token,
        "created_at": now.isoformat(),
        "expires_at": expires_at
    }
    
    return cards_db[card_id]

@app.get("/cards")
async def list_cards():
    """List all active (non-expired) cards"""
    active_cards = {
        k: v for k, v in cards_db.items()
        if not is_expired(v["expires_at"])
    }
    return list(active_cards.values())

@app.get("/cards/{card_id}")
async def get_card(card_id: str):
    """Get card details by ID"""
    if card_id not in cards_db or is_expired(cards_db[card_id]["expires_at"]):
        raise HTTPException(status_code=404, detail="Card not found or expired")
    return cards_db[card_id]

@app.delete("/cards/{card_id}/{token}")
async def delete_card(card_id: str, token: str):
    """Delete card (requires valid token)"""
    if card_id not in cards_db or cards_db[card_id]["token"] != token:
        raise HTTPException(status_code=403, detail="Unauthorized: invalid token")
    
    del cards_db[card_id]
    return {"message": "Card deleted successfully"}

@app.get("/verify/{token}")
async def verify_token(token: str):
    """Verify email token ownership"""
    for card_id, card in cards_db.items():
        if card["token"] == token and not is_expired(card["expires_at"]):
            return {
                "verified": True,
                "card_id": card_id,
                "email": card["email"]
            }
    raise HTTPException(status_code=404, detail="Token not found or invalid")

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}
