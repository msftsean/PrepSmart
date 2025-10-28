"""Crisis Profile data model."""

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator


class CrisisProfile(BaseModel):
    """User's crisis scenario and household information."""

    # Identifiers
    task_id: str = Field(..., description="Unique UUID for this crisis plan generation")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Crisis Type
    crisis_mode: Literal["natural_disaster", "economic_crisis"]
    specific_threat: str = Field(
        ...,
        description="e.g., 'hurricane', 'earthquake', 'government_shutdown', 'layoff'"
    )

    # Location
    location: dict = Field(..., description="User's geographic location")
    # location sub-fields:
    #   - zip_code: Optional[str]
    #   - city: str
    #   - state: str
    #   - country: str = "US"
    #   - latitude: Optional[float]
    #   - longitude: Optional[float]

    # Household Composition
    household: dict = Field(..., description="Household details")
    # household sub-fields:
    #   - adults: int (min: 1, max: 20)
    #   - children: int (min: 0, max: 20)
    #   - pets: int (min: 0, max: 10)
    #   - special_needs: Optional[str]

    housing_type: Literal["apartment", "house", "mobile_home", "other"]

    # Budget Constraint
    budget_tier: Literal[50, 100, 200] = Field(
        ...,
        description="Budget in USD for supply preparation"
    )

    # Economic Crisis Specific Fields (optional)
    financial_situation: Optional[dict] = Field(
        None,
        description="Financial details for economic crisis mode"
    )
    # financial_situation sub-fields:
    #   - current_income: float (monthly, can be 0)
    #   - monthly_expenses: float
    #   - available_savings: float
    #   - debt_obligations: float
    #   - dependents: int
    #   - employment_status: str

    @field_validator('location')
    @classmethod
    def validate_location(cls, v: dict) -> dict:
        """Ensure location has required fields."""
        required = ['city', 'state']
        for field in required:
            if field not in v:
                raise ValueError(f"Location missing required field: {field}")
        return v

    @field_validator('household')
    @classmethod
    def validate_household(cls, v: dict) -> dict:
        """Ensure household has valid composition."""
        if v.get('adults', 0) < 1:
            raise ValueError("At least 1 adult required")
        if v.get('adults', 0) + v.get('children', 0) > 20:
            raise ValueError("Household size cannot exceed 20 people")
        return v

    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "task_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                "created_at": "2025-10-28T14:32:00Z",
                "crisis_mode": "natural_disaster",
                "specific_threat": "hurricane",
                "location": {
                    "zip_code": "33139",
                    "city": "Miami Beach",
                    "state": "FL",
                    "country": "US",
                    "latitude": 25.79,
                    "longitude": -80.13
                },
                "household": {
                    "adults": 2,
                    "children": 1,
                    "pets": 1,
                    "special_needs": "infant formula needed"
                },
                "housing_type": "apartment",
                "budget_tier": 100,
                "financial_situation": None
            }
        }
