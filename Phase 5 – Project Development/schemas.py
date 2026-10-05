from typing import Optional
from pydantic import BaseModel, Field

class RegisterRequest(BaseModel):
    email: str
    full_name: str = Field(min_length=2, max_length=80)
    password: str = Field(min_length=6, max_length=100)

class LoginRequest(BaseModel):
    email: str
    password: str

class HomeRequest(BaseModel):
    total_budget: float = Field(gt=0)
    rooms: str = "Living Room"
    lights: int = Field(default=1, ge=0)
    fans: int = Field(default=1, ge=0)
    furniture: int = Field(default=1, ge=0)
    dining_tables: int = Field(default=0, ge=0)
    style: str = "Modern"
    additional_requirements: str = ""

class PartyRequest(BaseModel):
    total_budget: float = Field(gt=0)
    party_type: str = "Birthday"
    guests: int = Field(gt=0, le=5000)
    venue_type: str = "Not specified"
    catering: bool = True
    decoration: bool = True
    entertainment: bool = True
    additional_requirements: str = ""

class JewelryRequest(BaseModel):
    total_budget: float = Field(gt=0)
    occasion: str = "Wedding"
    preferences: str = "Elegant"
    outfit_description: str = ""
    image_name: Optional[str] = None
