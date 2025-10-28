# Data Model: PrepSmart

**Feature**: PrepSmart Multi-Agent Crisis Preparedness Assistant
**Date**: 2025-10-28
**Purpose**: Define all data entities, their schemas, validation rules, and relationships.

## Overview

PrepSmart uses several interconnected data entities representing crisis scenarios, AI agent outputs, and user plans. This document defines the structure of each entity for consistent implementation across Python backend (using Pydantic models), JSON API contracts, and database schemas.

### Architecture Note: Blackboard Pattern
PrepSmart uses a **blackboard pattern** for multi-agent coordination. The Blackboard entity (defined below) serves as shared state, containing all intermediate and final results from agents. Agents read from and write to the blackboard atomically. The Coordinator Agent monitors the blackboard to determine agent execution order and completion status.

---

## 1. Blackboard (Shared State)

**Description**: Central coordination entity for multi-agent orchestration using the blackboard pattern. Contains all input data, intermediate agent results, and final complete plan.

### Schema

```python
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class Blackboard(BaseModel):
    """Shared state for multi-agent coordination."""

    # Identifiers
    task_id: str = Field(..., description="Unique UUID linking all agent outputs")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Input Data
    crisis_profile: Optional[dict] = Field(None, description="User's crisis scenario (CrisisProfile)")

    # Intermediate Agent Results
    risk_assessment: Optional[dict] = Field(None, description="From Risk Assessment Agent")
    supply_plan: Optional[dict] = Field(None, description="From Supply Planning Agent")
    emergency_plan: Optional[dict] = Field(None, description="From Emergency Plan Generator (natural disaster)")
    economic_plan: Optional[dict] = Field(None, description="From Financial Advisor (economic crisis)")
    resource_locations: Optional[list[dict]] = Field(None, description="From Resource Locator Agent")
    video_recommendations: Optional[list[dict]] = Field(None, description="From Video Curator Agent")

    # Final Output
    complete_plan: Optional[dict] = Field(None, description="From Documentation Agent")
    pdf_path: Optional[str] = Field(None, description="Path to generated PDF")

    # Coordination State
    status: str = Field(default="initialized", description="'initialized', 'processing', 'completed', 'failed'")
    agents_completed: list[str] = Field(default_factory=list, description="List of agent names that have written to blackboard")
    agents_failed: list[str] = Field(default_factory=list, description="List of agent names that failed")

    # Execution Tracking
    execution_start: Optional[datetime] = None
    execution_end: Optional[datetime] = None
    total_execution_seconds: Optional[float] = None

    # Cost Tracking
    total_tokens_used: int = Field(default=0, description="Sum of all agent token usage")
    total_cost_estimate: float = Field(default=0.0, description="Estimated Claude API cost in USD")

    class Config:
        json_schema_extra = {
            "example": {
                "task_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                "status": "processing",
                "crisis_profile": {"crisis_mode": "natural_disaster", "specific_threat": "hurricane"},
                "risk_assessment": {"overall_risk_level": "EXTREME"},
                "agents_completed": ["RiskAssessmentAgent", "SupplyPlanningAgent"],
                "total_tokens_used": 3500,
                "total_cost_estimate": 0.042
            }
        }
```

### Agent Interaction Pattern

```python
# Agent reads from blackboard
async def process(self, blackboard: Blackboard) -> Blackboard:
    crisis_profile = blackboard.crisis_profile

    # Some agents may depend on other agents' results
    if blackboard.risk_assessment:
        risk_level = blackboard.risk_assessment['overall_risk_level']

    # Agent does its work
    result = await self.generate_output(crisis_profile)

    # Agent writes to blackboard atomically
    blackboard.supply_plan = result
    blackboard.agents_completed.append(self.agent_name)
    blackboard.total_tokens_used += self.tokens_used
    blackboard.updated_at = datetime.utcnow()

    return blackboard
```

### Coordinator Monitoring

```python
# Coordinator determines which agents can run
def get_ready_agents(blackboard: Blackboard) -> list[str]:
    """Returns list of agents whose preconditions are met."""
    ready = []

    # Risk Assessment Agent: Always ready (no dependencies)
    if "RiskAssessmentAgent" not in blackboard.agents_completed:
        ready.append("RiskAssessmentAgent")

    # Supply Planning Agent: Depends on Risk Assessment
    if (blackboard.risk_assessment is not None and
        "SupplyPlanningAgent" not in blackboard.agents_completed):
        ready.append("SupplyPlanningAgent")

    # ... etc for other agents

    return ready
```

### Database Schema (SQLite)

```sql
CREATE TABLE blackboards (
    task_id TEXT PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    crisis_profile_json TEXT NOT NULL,
    risk_assessment_json TEXT,
    supply_plan_json TEXT,
    emergency_plan_json TEXT,
    economic_plan_json TEXT,
    resource_locations_json TEXT,
    video_recommendations_json TEXT,
    complete_plan_json TEXT,
    pdf_path TEXT,

    status TEXT DEFAULT 'initialized',
    agents_completed_json TEXT,  -- JSON array
    agents_failed_json TEXT,     -- JSON array

    execution_start TIMESTAMP,
    execution_end TIMESTAMP,
    total_execution_seconds REAL,

    total_tokens_used INTEGER DEFAULT 0,
    total_cost_estimate REAL DEFAULT 0.0,

    FOREIGN KEY (task_id) REFERENCES crisis_profiles(task_id)
);

CREATE INDEX idx_blackboard_status ON blackboards(status);
CREATE INDEX idx_blackboard_updated ON blackboards(updated_at);
```

---

## 2. Crisis Profile

**Description**: Represents a user's crisis scenario input, collected via the questionnaire form.

### Schema

```python
from pydantic import BaseModel, Field, validator
from typing import Literal, Optional
from datetime import datetime

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
    #   - special_needs: Optional[str] (e.g., "wheelchair access", "infant", "elderly")

    housing_type: Literal["apartment", "house", "mobile_home", "other"]

    # Budget Constraint
    budget_tier: Literal[50, 100, 200] = Field(
        ...,
        description="Budget in USD for supply preparation"
    )

    # Economic Crisis Specific Fields (optional)
    runtime_questions: Optional[dict] = Field(
        None,
        description="User responses to runtime questions asked by agents during economic crisis mode"
    )
    # runtime_questions sub-fields (collected by agents, not upfront):
    #   - primary_concern: str (e.g., "Eviction or foreclosure", "Losing utilities", "Can't afford food")
    #   - runway: str (e.g., "Less than 2 weeks", "2-4 weeks", "1-3 months")
    #   - top_priority: str (e.g., "Keep my housing", "Feed my family")
    #   - income_check: str ("Yes" or "No")
    #   - income_range: Optional[str] (e.g., "$0-500", "$500-1500", if income_check is "Yes")
    #   - supply_focus: Optional[str] (e.g., "Food stockpiling", "Medication", "Essential bills")

    @validator('location')
    def validate_location(cls, v):
        """Ensure location has required fields."""
        required = ['city', 'state']
        for field in required:
            if field not in v:
                raise ValueError(f"Location missing required field: {field}")
        return v

    @validator('household')
    def validate_household(cls, v):
        """Ensure household has valid composition."""
        if v.get('adults', 0) < 1:
            raise ValueError("At least 1 adult required")
        if v.get('adults', 0) + v.get('children', 0) > 20:
            raise ValueError("Household size cannot exceed 20 people")
        return v
```

### Example JSON

```json
{
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
  "runtime_questions": null
}
```

### Database Schema (SQLite)

```sql
CREATE TABLE crisis_profiles (
    task_id TEXT PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    crisis_mode TEXT NOT NULL,
    specific_threat TEXT NOT NULL,
    location_json TEXT NOT NULL,  -- JSON string
    household_json TEXT NOT NULL, -- JSON string
    housing_type TEXT NOT NULL,
    budget_tier INTEGER NOT NULL,
    runtime_questions_json TEXT, -- JSON string, nullable (for economic crisis mode)
    status TEXT DEFAULT 'processing', -- 'processing', 'completed', 'failed'
    completed_at TIMESTAMP
);

CREATE INDEX idx_crisis_created ON crisis_profiles(created_at);
CREATE INDEX idx_crisis_status ON crisis_profiles(status);
```

---

## 2. Risk Assessment

**Description**: Output from the Risk Assessment Agent analyzing disaster threats for a location.

### Schema

```python
class ThreatDetail(BaseModel):
    """Individual threat within a risk assessment."""
    threat_type: str = Field(..., description="e.g., 'hurricane', 'earthquake'")
    severity_score: int = Field(..., ge=0, le=100, description="0-100 scale")
    risk_level: Literal["EXTREME", "HIGH", "MEDIUM", "LOW"]
    distance_to_threat: Optional[float] = Field(None, description="Miles to threat source")
    historical_context: str = Field(..., description="Historical data context")
    specific_warnings: list[str] = Field(default_factory=list)

class RiskAssessment(BaseModel):
    """Risk analysis for a location."""
    task_id: str
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    location: str = Field(..., description="Human-readable location string")

    primary_threat: ThreatDetail
    secondary_threats: list[ThreatDetail] = Field(default_factory=list)

    overall_severity_score: int = Field(..., ge=0, le=100)
    overall_risk_level: Literal["EXTREME", "HIGH", "MEDIUM", "LOW"]

    time_sensitive: bool = Field(
        ...,
        description="True if threat is imminent (e.g., hurricane in 48 hours)"
    )
    evacuation_recommended: bool

    recommendations: list[str] = Field(
        ...,
        description="Immediate action items based on risk"
    )

    source: str = Field(
        default="AI Risk Assessment Agent + FEMA guidance",
        description="Attribution for risk data"
    )
```

### Example JSON

```json
{
  "task_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "generated_at": "2025-10-28T14:32:15Z",
  "location": "Miami Beach, FL",
  "primary_threat": {
    "threat_type": "hurricane",
    "severity_score": 95,
    "risk_level": "EXTREME",
    "distance_to_threat": 45,
    "historical_context": "Category 5 Hurricane Melissa is 45 miles offshore. Miami Beach has experienced 8 major hurricanes since 1992, including Andrew (Cat 5) and Irma (Cat 4).",
    "specific_warnings": [
      "Storm surge expected 10-15 feet in coastal areas",
      "Sustained winds 160+ mph within 24 hours",
      "Mandatory evacuation order in effect for Zone A"
    ]
  },
  "secondary_threats": [
    {
      "threat_type": "flooding",
      "severity_score": 85,
      "risk_level": "HIGH",
      "distance_to_threat": 0,
      "historical_context": "Low-lying coastal area prone to flooding during hurricanes and king tides.",
      "specific_warnings": ["Roads may be impassable within 12 hours"]
    }
  ],
  "overall_severity_score": 95,
  "overall_risk_level": "EXTREME",
  "time_sensitive": true,
  "evacuation_recommended": true,
  "recommendations": [
    "Evacuate IMMEDIATELY to inland shelter",
    "Finalize supply gathering within next 2 hours",
    "Secure all outdoor items and board windows NOW"
  ],
  "source": "AI Risk Assessment Agent + FEMA guidance + NOAA Hurricane Center"
}
```

---

## 3. Supply Plan

**Description**: Personalized emergency supply checklist organized by budget tiers.

### Schema

```python
class SupplyItem(BaseModel):
    """Individual item in supply plan."""
    name: str
    quantity: int = Field(..., ge=1)
    unit: str = Field(..., description="e.g., 'gallons', 'pieces', 'days'")
    estimated_price: float = Field(..., ge=0)
    priority: Literal["critical", "prepared", "comprehensive"]
    category: str = Field(..., description="e.g., 'water', 'food', 'first_aid', 'tools'")
    crisis_specific: bool = Field(
        False,
        description="True if item is specific to crisis type (e.g., plywood for hurricane)"
    )
    alternatives: list[str] = Field(
        default_factory=list,
        description="Free or cheaper alternatives"
    )
    rationale: str = Field(..., description="Why this item is needed")

class SupplyTier(BaseModel):
    """Budget tier with its items."""
    tier_name: Literal["Critical", "Prepared", "Comprehensive"]
    description: str
    items: list[SupplyItem]
    total_cost: float = Field(..., ge=0)
    duration_days: int = Field(..., description="How many days this tier covers")

class SupplyPlan(BaseModel):
    """Complete supply plan with all tiers."""
    task_id: str
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    crisis_type: str
    household_size: int = Field(..., description="Total people (adults + children)")
    budget_constraint: int = Field(..., description="User's budget tier")

    tiers: dict[str, SupplyTier] = Field(
        ...,
        description="Keys: 'critical', 'prepared', 'comprehensive'"
    )

    recommended_tier: Literal["critical", "prepared", "comprehensive"]

    total_items: int = Field(..., description="Total number of items in recommended tier")

    storage_tips: list[str] = Field(
        default_factory=list,
        description="How to store supplies for household type"
    )

    acquisition_timeline: str = Field(
        ...,
        description="When to purchase supplies (e.g., '24 hours if threat imminent')"
    )
```

### Example JSON

```json
{
  "task_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "generated_at": "2025-10-28T14:32:30Z",
  "crisis_type": "hurricane",
  "household_size": 3,
  "budget_constraint": 100,
  "tiers": {
    "critical": {
      "tier_name": "Critical",
      "description": "Bare minimum survival needs for 72 hours",
      "items": [
        {
          "name": "Drinking Water",
          "quantity": 9,
          "unit": "gallons",
          "estimated_price": 12.00,
          "priority": "critical",
          "category": "water",
          "crisis_specific": false,
          "alternatives": ["Fill bathtub and clean containers at home (FREE)"],
          "rationale": "1 gallon per person per day for 3 days (3 people × 3 days = 9 gallons)"
        },
        {
          "name": "Non-perishable Food",
          "quantity": 9,
          "unit": "meals",
          "estimated_price": 25.00,
          "priority": "critical",
          "category": "food",
          "crisis_specific": false,
          "alternatives": ["Peanut butter, crackers, canned goods from pantry"],
          "rationale": "3 meals per day for 3 people for 3 days"
        },
        {
          "name": "Flashlight with Batteries",
          "quantity": 2,
          "unit": "pieces",
          "estimated_price": 15.00,
          "priority": "critical",
          "category": "lighting",
          "crisis_specific": false,
          "alternatives": ["Charge all devices fully, use phone flashlight"],
          "rationale": "Power outages likely during hurricane"
        },
        {
          "name": "Battery-powered Radio",
          "quantity": 1,
          "unit": "pieces",
          "estimated_price": 20.00,
          "priority": "critical",
          "category": "communication",
          "crisis_specific": true,
          "alternatives": ["Car radio if evacuation vehicle available"],
          "rationale": "Essential for emergency broadcasts when power/internet out"
        },
        {
          "name": "First Aid Kit",
          "quantity": 1,
          "unit": "pieces",
          "estimated_price": 18.00,
          "priority": "critical",
          "category": "first_aid",
          "crisis_specific": false,
          "alternatives": ["Assemble from household items: bandages, pain relievers, antiseptic"],
          "rationale": "Treat minor injuries when emergency services unavailable"
        }
      ],
      "total_cost": 90.00,
      "duration_days": 3
    }
  },
  "recommended_tier": "critical",
  "total_items": 5,
  "storage_tips": [
    "Store supplies in waterproof container or high shelf (apartment flood risk)",
    "Keep grab-and-go bag near exit for rapid evacuation",
    "Store food away from chemicals/cleaning supplies"
  ],
  "acquisition_timeline": "Purchase within next 2 hours. Hurricane expected landfall in 24 hours. Stores may close soon."
}
```

---

## 4. Emergency Plan

**Description**: Family action plan with evacuation routes, meeting points, and communication strategy.

### Schema

```python
class EvacuationRoute(BaseModel):
    """Single evacuation route."""
    priority: Literal["primary", "secondary", "tertiary"]
    description: str = Field(..., description="Turn-by-turn directions")
    destination: str = Field(..., description="Safe destination address")
    estimated_time: str = Field(..., description="e.g., '45 minutes normal, 2+ hours heavy traffic'")
    notes: list[str] = Field(default_factory=list, description="Important considerations")

class MeetingPoint(BaseModel):
    """Designated meeting location for family."""
    location_type: Literal["local", "out_of_area", "emergency_shelter"]
    name: str
    address: str
    phone: Optional[str] = None
    notes: str = Field(..., description="Why this location and when to use it")

class EmergencyContact(BaseModel):
    """Template contact information."""
    relationship: str = Field(..., description="e.g., 'Out-of-state relative', 'Local friend'")
    purpose: str = Field(..., description="Why this contact is important")
    info_needed: list[str] = Field(
        ...,
        description="What info to fill in (name, phone, email, address)"
    )

class EmergencyPlan(BaseModel):
    """Complete family emergency action plan."""
    task_id: str
    generated_at: datetime = Field(default_factory=datetime.utcnow)

    crisis_type: str
    household_composition: str = Field(..., description="Human-readable, e.g., '2 adults, 1 child, 1 pet'")

    # Evacuation
    evacuation_routes: list[EvacuationRoute]
    evacuation_triggers: list[str] = Field(
        ...,
        description="Conditions that require immediate evacuation"
    )

    # Meeting Points
    meeting_points: list[MeetingPoint]

    # Communication
    communication_plan: dict = Field(..., description="How family will stay in contact")
    # communication_plan sub-fields:
    #   - primary_method: str (e.g., "Text messages")
    #   - backup_methods: list[str] (e.g., ["Social media check-ins", "Out-of-state contact relay"])
    #   - check_in_schedule: str (e.g., "Every 4 hours")
    #   - emergency_keywords: list[str] (e.g., ["CODE RED" = immediate danger])

    # Contacts
    emergency_contacts_template: list[EmergencyContact]

    # Special Considerations
    special_needs: list[str] = Field(
        default_factory=list,
        description="Household-specific considerations (infant care, medications, pet care)"
    )

    # Documents
    important_documents: list[str] = Field(
        ...,
        description="Documents to grab/copy before evacuation"
    )

    # Timeline
    action_timeline: dict[str, list[str]] = Field(
        ...,
        description="When to do what. Keys: '24_hours_before', '12_hours_before', etc."
    )
```

### Example JSON

```json
{
  "task_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "generated_at": "2025-10-28T14:32:45Z",
  "crisis_type": "hurricane",
  "household_composition": "2 adults, 1 child (toddler), 1 dog",
  "evacuation_routes": [
    {
      "priority": "primary",
      "description": "Take I-95 North to I-75 West toward Fort Myers. Exit at designated Red Cross shelter.",
      "destination": "Fort Myers Red Cross Shelter, 2825 Palm Beach Blvd, Fort Myers, FL 33916",
      "estimated_time": "2.5 hours in normal traffic, 4-6 hours during evacuation",
      "notes": [
        "Avoid Florida Turnpike (typically congested during evacuations)",
        "Fill gas tank BEFORE departing (stations may run out)",
        "Bring pet carrier and vaccination records (shelter accepts pets)"
      ]
    },
    {
      "priority": "secondary",
      "description": "If I-95 blocked, take US-1 North to I-75 West",
      "destination": "Same as primary",
      "estimated_time": "3-4 hours normal, 5-8 hours evacuation",
      "notes": ["Slower route but less congestion"]
    }
  ],
  "evacuation_triggers": [
    "Mandatory evacuation order issued for your zone",
    "Hurricane upgraded to Category 4+",
    "Storm surge warning exceeds 10 feet",
    "Flooding begins near your apartment",
    "You feel unsafe staying"
  ],
  "meeting_points": [
    {
      "location_type": "local",
      "name": "Miami Beach Public Library",
      "address": "2100 Collins Ave, Miami Beach, FL 33139",
      "phone": "(305) 535-4219",
      "notes": "Meet here if separated during pre-evacuation preparation. Library is sturdy building inland from coast."
    },
    {
      "location_type": "out_of_area",
      "name": "Aunt Maria's House",
      "address": "[Fill in out-of-state relative address]",
      "phone": "[Fill in phone]",
      "notes": "Rally point if Miami Beach is inaccessible post-storm. Everyone should know this address."
    },
    {
      "location_type": "emergency_shelter",
      "name": "Fort Myers Red Cross Shelter",
      "address": "2825 Palm Beach Blvd, Fort Myers, FL 33916",
      "phone": "1-800-RED-CROSS",
      "notes": "Designated evacuation destination. Check in at registration desk and leave note for family members."
    }
  ],
  "communication_plan": {
    "primary_method": "Text messages (more reliable than calls during emergencies)",
    "backup_methods": [
      "Facebook Safety Check",
      "Call Aunt Maria in Georgia who will relay messages",
      "Leave notes at meeting points"
    ],
    "check_in_schedule": "Every 4 hours, or immediately after any location change",
    "emergency_keywords": [
      "CODE RED = Immediate danger, need help",
      "CODE GREEN = Safe and accounted for"
    ]
  },
  "emergency_contacts_template": [
    {
      "relationship": "Out-of-state relative",
      "purpose": "Central communication hub when local lines are down",
      "info_needed": ["Full name", "Phone number", "Email", "Address"]
    },
    {
      "relationship": "Nearby friend/neighbor",
      "purpose": "Check on home/pets if you evacuate",
      "info_needed": ["Full name", "Phone number", "Proximity to your home"]
    },
    {
      "relationship": "Child's pediatrician",
      "purpose": "Medical advice if child injured or sick during crisis",
      "info_needed": ["Clinic name", "Phone number", "After-hours emergency number"]
    }
  ],
  "special_needs": [
    "Infant/toddler: Pack formula, diapers (1 week supply), favorite comfort toy",
    "Dog: Carrier, food (1 week), water bowl, leash, vaccination records, photo (if separated)",
    "Medications: 30-day supply of any prescriptions in waterproof bag"
  ],
  "important_documents": [
    "ID cards and passports (in waterproof bag)",
    "Insurance policies (home, auto, health) - copies or photos",
    "Medical records and prescriptions",
    "Bank account information",
    "Photos of valuables for insurance claims",
    "Pet vaccination records (for shelter entry)"
  ],
  "action_timeline": {
    "72_hours_before": [
      "Monitor weather updates every 6 hours",
      "Purchase critical supplies",
      "Fill prescriptions",
      "Notify out-of-state contact of potential evacuation"
    ],
    "48_hours_before": [
      "Fill vehicle gas tank",
      "Withdraw cash ($200-500, ATMs may be down)",
      "Charge all devices",
      "Secure outdoor furniture"
    ],
    "24_hours_before": [
      "Board windows or close storm shutters",
      "Pack evacuation bags",
      "Photograph home contents for insurance",
      "Turn refrigerator to coldest setting (keep food longer if power out)"
    ],
    "12_hours_before": [
      "If evacuation ordered: LEAVE NOW",
      "If sheltering in place: Fill bathtub with water, move to interior room"
    ]
  }
}
```

---

## 5. Economic Plan

**Description**: 30-day financial survival strategy for economic crisis (unemployment, furlough, government shutdown).

### Schema

```python
class ExpenseCategory(BaseModel):
    """Categorized monthly expense."""
    name: str
    current_amount: float
    category: Literal["must_pay", "defer", "eliminate"]
    rationale: str = Field(..., description="Why this categorization")
    negotiation_tips: list[str] = Field(
        default_factory=list,
        description="How to reduce or defer this expense"
    )

class DailyAction(BaseModel):
    """Single action item in 30-day plan."""
    day: int = Field(..., ge=1, le=30)
    priority: Literal["critical", "high", "medium"]
    action: str
    deadline: Optional[str] = None
    resources_needed: list[str] = Field(default_factory=list)
    estimated_time: str = Field(..., description="e.g., '30 minutes', '2 hours'")

class BenefitProgram(BaseModel):
    """Government or assistance program."""
    program_name: str
    eligibility: str = Field(..., description="Who qualifies")
    estimated_amount: Optional[str] = Field(None, description="e.g., '$450/week', 'Varies by household'")
    application_url: str
    required_documents: list[str]
    processing_time: str = Field(..., description="e.g., '2-4 weeks'")
    notes: str

class HardshipLetterTemplate(BaseModel):
    """Template for creditor communication."""
    recipient_type: Literal["landlord", "credit_card", "utility", "student_loan", "mortgage"]
    template_text: str = Field(..., description="Letter template with [PLACEHOLDER] markers")
    tips: list[str] = Field(..., description="How to customize and send effectively")

class EconomicPlan(BaseModel):
    """30-day economic survival strategy."""
    task_id: str
    generated_at: datetime = Field(default_factory=datetime.utcnow)

    crisis_type: str = Field(..., description="e.g., 'government_shutdown', 'layoff'")

    # Financial Snapshot
    financial_summary: dict = Field(..., description="Current situation")
    # financial_summary sub-fields:
    #   - current_monthly_income: float
    #   - total_monthly_expenses: float
    #   - available_savings: float
    #   - monthly_deficit: float (expenses - income)
    #   - runway_days: int (days until savings depleted)

    # Expense Breakdown
    expense_categories: dict[str, list[ExpenseCategory]] = Field(
        ...,
        description="Keys: 'must_pay', 'defer', 'eliminate'"
    )

    revised_monthly_expenses: float = Field(
        ...,
        description="Total after cuts and deferrals"
    )

    # Action Plan
    daily_actions: list[DailyAction]

    # Benefits & Assistance
    eligible_benefits: list[BenefitProgram]
    estimated_total_relief: str = Field(
        ...,
        description="Combined estimated monthly relief from all benefits"
    )

    # Communication Templates
    hardship_letters: list[HardshipLetterTemplate]

    # Resources
    local_resources: list[str] = Field(
        ...,
        description="Nearby food banks, legal aid, etc. (cross-reference with ResourceLocation)"
    )

    # Survival Timeline
    survival_outlook: dict = Field(..., description="Financial projections")
    # survival_outlook sub-fields:
    #   - without_action: str (e.g., "Savings depleted in 15 days")
    #   - with_action: str (e.g., "Can survive 45 days with cuts + benefits")
    #   - best_case: str (e.g., "90 days if all benefits approved quickly")
```

### Example JSON (Truncated for brevity)

```json
{
  "task_id": "b2c3d4e5-f6g7-8901-bcde-fg2345678901",
  "generated_at": "2025-10-28T15:00:00Z",
  "crisis_type": "government_shutdown",
  "financial_summary": {
    "current_monthly_income": 0,
    "total_monthly_expenses": 3200,
    "available_savings": 2000,
    "monthly_deficit": -3200,
    "runway_days": 18
  },
  "expense_categories": {
    "must_pay": [
      {
        "name": "Rent",
        "current_amount": 1500,
        "category": "must_pay",
        "rationale": "Housing is non-negotiable, but can request deferral",
        "negotiation_tips": [
          "Contact landlord immediately with hardship letter",
          "Propose partial payment plan (e.g., $500/month during shutdown)",
          "Reference government shutdown as extraordinary circumstance"
        ]
      },
      {
        "name": "Groceries",
        "current_amount": 600,
        "category": "must_pay",
        "rationale": "Food is essential, but can reduce significantly",
        "negotiation_tips": [
          "Cut to $300/month with meal planning and food bank supplementation",
          "Apply for SNAP benefits (see eligible_benefits)"
        ]
      }
    ],
    "defer": [
      {
        "name": "Credit Card Payments",
        "current_amount": 250,
        "category": "defer",
        "rationale": "Contact creditors to arrange hardship forbearance",
        "negotiation_tips": [
          "Many credit cards offer hardship programs (0% interest, reduced minimums)",
          "Explain government shutdown, request 60-day forbearance",
          "Use hardship letter template provided"
        ]
      }
    ],
    "eliminate": [
      {
        "name": "Streaming Services",
        "current_amount": 45,
        "category": "eliminate",
        "rationale": "Non-essential luxury during crisis",
        "negotiation_tips": ["Cancel immediately, can re-subscribe later"]
      }
    ]
  },
  "revised_monthly_expenses": 1950,
  "daily_actions": [
    {
      "day": 1,
      "priority": "critical",
      "action": "Contact landlord via phone AND written hardship letter to request payment deferral",
      "deadline": "Today (Day 1)",
      "resources_needed": ["Hardship letter template", "Proof of federal employment"],
      "estimated_time": "1 hour"
    },
    {
      "day": 1,
      "priority": "critical",
      "action": "Apply for unemployment benefits (federal workers may qualify depending on state)",
      "deadline": "Today (Day 1)",
      "resources_needed": ["Social Security Number", "Employment history", "Bank account for direct deposit"],
      "estimated_time": "45 minutes"
    },
    {
      "day": 2,
      "priority": "critical",
      "action": "Apply for SNAP (food stamps) online at state benefits portal",
      "deadline": "Day 2-3",
      "resources_needed": ["ID", "Proof of income loss", "Household size info"],
      "estimated_time": "30 minutes"
    }
  ],
  "eligible_benefits": [
    {
      "program_name": "Unemployment Insurance",
      "eligibility": "Federal workers may qualify during extended shutdowns (varies by state)",
      "estimated_amount": "$450-800/week depending on previous salary",
      "application_url": "https://www.careeronestop.org/LocalHelp/UnemploymentBenefits/find-unemployment-benefits.aspx",
      "required_documents": ["ID", "Social Security Number", "Employment history"],
      "processing_time": "2-4 weeks for first payment",
      "notes": "Back pay may be issued once government reopens if shutdown is prolonged."
    },
    {
      "program_name": "SNAP (Food Stamps)",
      "eligibility": "Households with $0 income typically qualify for maximum benefit",
      "estimated_amount": "$680/month for household of 3 (2025 rates)",
      "application_url": "https://www.fns.usda.gov/snap/state-directory",
      "required_documents": ["ID", "Proof of address", "Income/employment verification", "Social Security Numbers"],
      "processing_time": "7-30 days",
      "notes": "Expedited processing available for urgent cases (0 income, <$150 cash)."
    }
  ],
  "estimated_total_relief": "$2,480/month if all benefits approved (unemployment $1,800/mo + SNAP $680/mo)",
  "hardship_letters": [
    {
      "recipient_type": "landlord",
      "template_text": "[Date]\n\nDear [Landlord Name],\n\nI am writing to inform you of an unexpected financial hardship...[FULL TEMPLATE]",
      "tips": [
        "Send via email AND certified mail for documentation",
        "Attach proof of federal employment and shutdown notice",
        "Propose specific payment plan with timeline",
        "Emphasize your commitment to catching up when government reopens"
      ]
    }
  ],
  "local_resources": [
    "[Reference to ResourceLocation entities for Washington D.C. area]"
  ],
  "survival_outlook": {
    "without_action": "Savings depleted in 18 days. Eviction risk by Day 30.",
    "with_action": "Can survive 45+ days with expense cuts, benefit applications, and payment deferrals.",
    "best_case": "90+ days if unemployment and SNAP approved quickly. Back pay from government when shutdown ends."
  }
}
```

---

## 6. Resource Location

**Description**: Local assistance resource (shelter, food bank, unemployment office, etc.).

### Schema

```python
class ResourceLocation(BaseModel):
    """Local assistance resource."""
    resource_id: str = Field(..., description="Unique identifier")
    name: str
    resource_type: Literal[
        "shelter",
        "food_bank",
        "unemployment_office",
        "hospital",
        "police_station",
        "community_center",
        "legal_aid",
        "crisis_hotline"
    ]

    # Location
    address: str
    city: str
    state: str
    zip_code: str
    latitude: float
    longitude: float

    # Contact
    phone: Optional[str] = None
    website: Optional[str] = None
    email: Optional[str] = None

    # Details
    hours_of_operation: Optional[str] = Field(
        None,
        description="e.g., 'Mon-Fri 9am-5pm' or '24/7' or 'Call for hours'"
    )
    services_offered: list[str] = Field(
        ...,
        description="e.g., ['Emergency shelter', 'Pet-friendly', 'Wheelchair accessible']"
    )
    eligibility_requirements: Optional[str] = Field(
        None,
        description="Any restrictions or requirements"
    )

    # Computed Fields
    distance_miles: Optional[float] = Field(
        None,
        description="Distance from user's location (computed at query time)"
    )

    # Source
    data_source: str = Field(
        ...,
        description="Where this data came from (e.g., 'FEMA Shelter Directory', 'OpenStreetMap')"
    )
    last_verified: Optional[datetime] = Field(
        None,
        description="When this data was last verified as accurate"
    )
```

### Example JSON

```json
{
  "resource_id": "shelter-fl-miami-redcross-001",
  "name": "Miami Beach Community Center Emergency Shelter",
  "resource_type": "shelter",
  "address": "2100 Washington Ave",
  "city": "Miami Beach",
  "state": "FL",
  "zip_code": "33139",
  "latitude": 25.7959,
  "longitude": -80.1396,
  "phone": "(305) 673-7730",
  "website": "https://www.miamibeachfl.gov/city-hall/parks-and-recreation/",
  "email": null,
  "hours_of_operation": "Opens when emergency declared, 24/7 during activation",
  "services_offered": [
    "Emergency shelter",
    "Cots and blankets provided",
    "Meals (limited)",
    "Wheelchair accessible",
    "Service animals allowed",
    "Pets NOT allowed (see pet-friendly shelters)"
  ],
  "eligibility_requirements": "Miami-Dade County residents during evacuation orders. No alcohol or weapons permitted.",
  "distance_miles": 0.8,
  "data_source": "Miami Beach Parks & Recreation + FEMA Shelter Directory",
  "last_verified": "2025-10-15T00:00:00Z"
}
```

---

## 7. Video Recommendation

**Description**: Educational video for preparedness guidance.

### Schema

```python
class VideoRecommendation(BaseModel):
    """Educational video resource."""
    video_id: str = Field(..., description="Unique identifier")
    title: str
    url: str = Field(..., description="YouTube URL or other video platform")
    source: str = Field(..., description="e.g., 'FEMA', 'Red Cross', 'NWS'")

    duration_seconds: int
    duration_formatted: str = Field(..., description="e.g., '5:32'")

    crisis_types: list[str] = Field(
        ...,
        description="Which crisis types this video is relevant for"
    )
    topics: list[str] = Field(
        ...,
        description="e.g., ['evacuation', 'supply_planning', 'family_communication']"
    )

    relevance_score: int = Field(
        ...,
        ge=1,
        le=10,
        description="1-10 score for relevance to user's specific crisis (computed by agent)"
    )

    description: str = Field(..., description="Brief summary of video content")
    thumbnail_url: Optional[str] = None

    target_audience: str = Field(
        ...,
        description="e.g., 'Families with children', 'Pet owners', 'General audience'"
    )
```

### Example JSON

```json
{
  "video_id": "vid-fema-hurricane-prep-001",
  "title": "Hurricane Preparedness: Family Emergency Plan",
  "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
  "source": "FEMA",
  "duration_seconds": 332,
  "duration_formatted": "5:32",
  "crisis_types": ["hurricane", "tropical_storm"],
  "topics": ["family_plan", "evacuation", "communication"],
  "relevance_score": 10,
  "description": "Official FEMA guide to creating a family emergency plan for hurricanes, including evacuation routes, meeting points, and communication strategies.",
  "thumbnail_url": "https://img.youtube.com/vi/dQw4w9WgXcQ/hqdefault.jpg",
  "target_audience": "Families with children in hurricane-prone areas"
}
```

---

## 8. Agent Activity Log

**Description**: Real-time status tracking for AI agent processing (displayed in UI dashboard).

### Schema

```python
class AgentActivityLog(BaseModel):
    """Real-time agent status for UI display."""
    log_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    task_id: str = Field(..., description="Associated crisis plan task ID")

    agent_name: str = Field(
        ...,
        description="e.g., 'Coordinator', 'Risk Assessment', 'Supply Planning'"
    )
    agent_type: Literal[
        "coordinator",
        "risk_assessment",
        "supply_planning",
        "financial_advisor",
        "resource_locator",
        "video_curator",
        "documentation"
    ]

    status: Literal["waiting", "active", "complete", "error"]

    current_task_description: str = Field(
        ...,
        description="Human-readable description of what agent is doing right now"
    )

    progress_percentage: int = Field(
        default=0,
        ge=0,
        le=100,
        description="0-100% completion"
    )

    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    execution_time_seconds: Optional[float] = None

    error_message: Optional[str] = None

    # Inter-agent Communication
    messages: list[dict] = Field(
        default_factory=list,
        description="Messages sent/received from other agents"
    )
    # message format: {"from": "agent_name", "to": "agent_name", "content": "str", "timestamp": "datetime"}

    # Metadata
    tokens_used: Optional[int] = Field(None, description="Claude API tokens consumed")
    cost_estimate: Optional[float] = Field(None, description="Estimated cost in USD")
```

### Example JSON

```json
{
  "log_id": "log-a1b2c3-001",
  "task_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "agent_name": "Risk Assessment Agent",
  "agent_type": "risk_assessment",
  "status": "active",
  "current_task_description": "Analyzing historical hurricane data and current weather patterns for Miami Beach, FL...",
  "progress_percentage": 65,
  "started_at": "2025-10-28T14:32:10Z",
  "completed_at": null,
  "execution_time_seconds": null,
  "error_message": null,
  "messages": [
    {
      "from": "coordinator",
      "to": "risk_assessment",
      "content": "Analyze hurricane risk for Miami Beach, FL (25.79, -80.13)",
      "timestamp": "2025-10-28T14:32:10Z"
    }
  ],
  "tokens_used": 1523,
  "cost_estimate": 0.0152
}
```

### Database Schema (SQLite)

```sql
CREATE TABLE agent_logs (
    log_id TEXT PRIMARY KEY,
    task_id TEXT NOT NULL,
    agent_name TEXT NOT NULL,
    agent_type TEXT NOT NULL,
    status TEXT NOT NULL,
    current_task_description TEXT NOT NULL,
    progress_percentage INTEGER DEFAULT 0,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    execution_time_seconds REAL,
    error_message TEXT,
    messages_json TEXT, -- JSON array
    tokens_used INTEGER,
    cost_estimate REAL,
    FOREIGN KEY (task_id) REFERENCES crisis_profiles(task_id)
);

CREATE INDEX idx_agent_logs_task ON agent_logs(task_id);
CREATE INDEX idx_agent_logs_status ON agent_logs(status);
```

---

## 9. Complete Plan Document

**Description**: Aggregated result from all agents, returned to user via API.

### Schema

```python
class CompletePlan(BaseModel):
    """Aggregated plan from all agents."""
    task_id: str
    created_at: datetime
    completed_at: datetime
    total_execution_time_seconds: float

    crisis_profile: CrisisProfile

    # Agent Outputs (optional fields for graceful degradation)
    risk_assessment: Optional[RiskAssessment] = None
    supply_plan: Optional[SupplyPlan] = None
    emergency_plan: Optional[EmergencyPlan] = None
    economic_plan: Optional[EconomicPlan] = None
    resource_locations: list[ResourceLocation] = Field(default_factory=list)
    video_recommendations: list[VideoRecommendation] = Field(default_factory=list)

    # PDF
    pdf_url: Optional[str] = Field(None, description="URL to download PDF")
    pdf_generated: bool = Field(default=False)

    # Status
    status: Literal["complete", "partial", "failed"]
    agents_succeeded: int
    agents_failed: int
    failure_details: list[str] = Field(
        default_factory=list,
        description="Which agents failed and why"
    )

    # Metadata
    total_cost_estimate: float = Field(..., description="Total Claude API cost in USD")
    tokens_used: int
```

---

## 10. Validation Rules

### Crisis Profile
- `household.adults` ≥ 1
- `household.adults` + `household.children` ≤ 20
- `budget_tier` must be one of [50, 100, 200]
- `location.city` and `location.state` required
- If `crisis_mode` == "economic_crisis", `financial_situation` must be provided

### Risk Assessment
- `severity_score` must be 0-100
- `overall_risk_level` must match severity_score ranges:
  - 0-25: LOW
  - 26-50: MEDIUM
  - 51-75: HIGH
  - 76-100: EXTREME

### Supply Plan
- `tiers.critical.total_cost` should not exceed `budget_constraint` by more than 10%
- All items must have `quantity` ≥ 1
- `household_size` must match `crisis_profile.household` totals

### Economic Plan
- `daily_actions` must have at least 20 entries (one per day minimum)
- `financial_summary.monthly_deficit` must equal `total_monthly_expenses - current_monthly_income`
- All benefit programs must have valid `application_url`

---

## 11. Relationships

```
CrisisProfile (1) ---> (1) CompletePlan
CrisisProfile (1) ---> (0..7) AgentActivityLog
CompletePlan (1) ---> (0..1) RiskAssessment
CompletePlan (1) ---> (0..1) SupplyPlan
CompletePlan (1) ---> (0..1) EmergencyPlan
CompletePlan (1) ---> (0..1) EconomicPlan
CompletePlan (1) ---> (0..N) ResourceLocation
CompletePlan (1) ---> (0..N) VideoRecommendation
```

---

## 12. File Storage Patterns

### JSON Files (Static Data)

**backend/src/data/disaster_types.json**
```json
{
  "hurricane": {
    "name": "Hurricane",
    "icon": "hurricane-icon.svg",
    "severity_factors": ["wind_speed", "storm_surge", "coastal_proximity"],
    "base_supplies": ["plywood", "sandbags", "battery_radio"]
  }
}
```

**backend/src/data/supply_templates.json**
Structure: Nested by crisis type → budget tier → item list

**backend/src/data/video_library.json**
Array of VideoRecommendation objects (50-100 pre-curated videos)

**backend/src/data/resources.json**
Array of ResourceLocation objects (200 pre-vetted resources)

**backend/src/data/offline_checklists.json**
Simplified emergency checklists for offline mode

---

## Summary

This data model provides:
- ✅ **Type safety** with Pydantic models
- ✅ **Clear validation rules** for data integrity
- ✅ **Graceful degradation** (Optional fields for agent failures)
- ✅ **API-ready** JSON schemas
- ✅ **Database schemas** for SQLite persistence
- ✅ **Real-time tracking** with AgentActivityLog
- ✅ **Constitutional compliance** (privacy, accessibility, budget-consciousness)

All entities align with the feature specification and support the 7-agent architecture.
