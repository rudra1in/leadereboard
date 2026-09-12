"""
Pydantic schemas for data validation and serialization.

Schemas define request/response contracts for API endpoints.
Provides automatic validation, documentation, and type hints.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator


# ============================================================================
# Athlete Schemas
# ============================================================================

class AthleteCreateRequest(BaseModel):
    """Request schema for creating an athlete"""
    athlete_id: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=255)
    team_name: Optional[str] = Field(None, max_length=255)
    profile_data: Optional[Dict[str, Any]] = {}
    federation_id: Optional[str] = None
    federation_source: bool = False
    
    class Config:
        json_schema_extra = {
            "example": {
                "athlete_id": "ATH001",
                "name": "Alex Rodriguez",
                "team_name": "Metropolitan Thunder",
                "federation_source": False
            }
        }


class AthleteResponse(BaseModel):
    """Response schema for athlete"""
    athlete_id: str
    name: str
    team_name: Optional[str]
    federation_source: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# Category Schemas
# ============================================================================

class CategoryCreateRequest(BaseModel):
    """Request schema for creating a category"""
    category_id: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=255)
    sport_id: str = Field(..., min_length=1, max_length=50)
    config_data: Optional[Dict[str, Any]] = {}
    display_order: int = 0
    
    class Config:
        json_schema_extra = {
            "example": {
                "category_id": "CAT001",
                "name": "Elite Mixed",
                "sport_id": "TENNIS",
                "config_data": {"age_min": 18, "age_max": 65}
            }
        }


class CategoryResponse(BaseModel):
    """Response schema for category"""
    category_id: str
    name: str
    sport_id: str
    display_order: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# Ranking Entry Schemas
# ============================================================================

class RankingEntryCreateRequest(BaseModel):
    """Request schema for creating a ranking entry (contributing event)"""
    event_id: str = Field(..., min_length=1)
    event_name: str = Field(..., min_length=1, max_length=255)
    event_date: datetime
    points_awarded: float = Field(..., ge=0)
    placement: Optional[str] = None
    category_id: str = Field(..., min_length=1, max_length=50)
    rule_version: Optional[str] = None


class RankingEntryResponse(BaseModel):
    """Response schema for ranking entry"""
    entry_id: str
    event_id: str
    event_name: str
    event_date: datetime
    points_awarded: float
    placement: Optional[str]
    source: str
    category_id: str
    rule_version: Optional[str]
    
    class Config:
        from_attributes = True


# ============================================================================
# Ranking Schemas
# ============================================================================

class RankingCreateRequest(BaseModel):
    """Request schema for creating a ranking"""
    athlete_id: str
    category_id: str
    config_id: str
    rank: int = Field(..., ge=1)
    points: float = Field(..., ge=0)
    previous_rank: Optional[int] = None
    is_federation_source: bool = False
    source: str = "official"
    event_count: int = 0


class RankingResponse(BaseModel):
    """Response schema for ranking"""
    ranking_id: str
    athlete_id: str
    name: str  # Athlete name
    team_name: Optional[str]
    category_id: str
    rank: int
    points: float
    previous_rank: Optional[int]
    movement: int
    event_count: int
    last_update: datetime
    is_federation_source: bool
    badge: Optional[str] = None
    
    class Config:
        from_attributes = True


class RankingDetailResponse(RankingResponse):
    """Detailed ranking response with contributing events"""
    contributing_events: List[RankingEntryResponse] = []
    
    class Config:
        from_attributes = True


# ============================================================================
# Qualification Scenario Schemas
# ============================================================================

class QualificationScenarioResponse(BaseModel):
    """Response schema for qualification scenario"""
    scenario_id: str
    name: str
    description: Optional[str]
    current_rank: int
    current_points: float
    projected_rank: int
    projected_points: float
    threshold_description: str
    probability: float
    
    class Config:
        from_attributes = True


class AthleteQualificationResponse(BaseModel):
    """Response schema for athlete's qualification data"""
    athlete_id: str
    current_rank: int
    current_points: float
    scenarios: List[QualificationScenarioResponse]
    disclaimers: List[str] = [
        "Scenarios are projections based on published rules and may change",
        "Actual results may differ due to rule updates or special circumstances",
        "Federation-authoritative rankings take precedence over local computations"
    ]
    
    class Config:
        from_attributes = True


# ============================================================================
# Ranking History Schemas
# ============================================================================

class RankingHistoryResponse(BaseModel):
    """Response schema for ranking history"""
    date: datetime = Field(..., alias="recorded_at")
    rank: int
    points: float
    movement: int
    event_triggered: Optional[str]
    
    class Config:
        from_attributes = True
        populate_by_name = True


# ============================================================================
# Ranking Config Schemas
# ============================================================================

class RankingConfigCreateRequest(BaseModel):
    """Request schema for creating ranking configuration"""
    config_id: str = Field(..., min_length=1, max_length=50)
    sport_id: Optional[str] = None
    category_id: Optional[str] = None
    points_table: Dict[int, float]  # placement -> points
    time_window: str = "rolling-12"
    decay_factor: float = Field(0.0, ge=0, le=1)
    max_events: Optional[int] = None
    engine_version: str = "1.0"
    
    class Config:
        json_schema_extra = {
            "example": {
                "config_id": "CFG001",
                "points_table": {1: 2500, 2: 2000, 3: 1500},
                "time_window": "rolling-12",
                "decay_factor": 0.0
            }
        }


class RankingConfigResponse(BaseModel):
    """Response schema for ranking configuration"""
    config_id: str
    version: int
    sport_id: Optional[str]
    category_id: Optional[str]
    points_table: Dict[int, float]
    time_window: str
    decay_factor: float
    max_events: Optional[int]
    engine_version: str
    is_active: bool
    created_at: datetime
    activated_at: Optional[datetime]
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============================================================================
# Rankings List/Filter Schemas
# ============================================================================

class RankingsFilterRequest(BaseModel):
    """Query parameters for filtering rankings"""
    sport: Optional[str] = None
    category: Optional[str] = None
    window: str = "current"  # current, rolling-12, ytd, all-time
    limit: int = Field(50, ge=1, le=1000)
    offset: int = Field(0, ge=0)
    search: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "sport": "Tennis",
                "category": "Elite Mixed",
                "window": "current",
                "limit": 50,
                "offset": 0
            }
        }


class RankingsListResponse(BaseModel):
    """Response schema for rankings list"""
    data: List[RankingResponse]
    total: int
    limit: int
    offset: int
    count: int = Field(..., description="Number of items in this response")
    
    @validator('count', always=True)
    def calculate_count(cls, v, values):
        if 'data' in values:
            return len(values['data'])
        return 0
    
    class Config:
        json_schema_extra = {
            "example": {
                "data": [],
                "total": 100,
                "limit": 50,
                "offset": 0,
                "count": 0
            }
        }


# ============================================================================
# Explainability Schemas
# ============================================================================

class RankingExplainabilityResponse(BaseModel):
    """Response schema for ranking explainability"""
    athlete_id: str
    total_points: float
    contributing_event_count: int
    events: List[RankingEntryResponse]
    period_start: datetime
    period_end: datetime
    window_type: str
    decay_factor: float
    
    class Config:
        from_attributes = True


# ============================================================================
# Admin Schemas
# ============================================================================

class RankingRecomputeRequest(BaseModel):
    """Request schema for triggering ranking recomputation"""
    event_id: str = Field(..., min_length=1)
    sport_id: Optional[str] = None
    category_id: Optional[str] = None
    triggered_by: str = "admin"
    
    class Config:
        json_schema_extra = {
            "example": {
                "event_id": "EVT001",
                "triggered_by": "admin"
            }
        }


class RankingRecomputeResponse(BaseModel):
    """Response schema for ranking recomputation"""
    recompute_id: str
    status: str  # pending, success, failed
    affected_rankings: int
    rankings_changed: int
    compute_time_ms: int
    started_at: datetime
    completed_at: Optional[datetime]
    error_message: Optional[str] = None
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "recompute_id": "RECOMP001",
                "status": "success",
                "affected_rankings": 42,
                "rankings_changed": 8,
                "compute_time_ms": 1250,
                "started_at": "2026-09-11T14:30:00Z",
                "completed_at": "2026-09-11T14:30:01Z"
            }
        }


# ============================================================================
# Error Schemas
# ============================================================================

class ErrorResponse(BaseModel):
    """Standard error response schema"""
    error: str
    detail: Optional[str] = None
    status_code: int = 400
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    path: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "Not Found",
                "detail": "Athlete with ID ATH999 not found",
                "status_code": 404,
                "timestamp": "2026-09-11T14:30:00Z",
                "path": "/api/rankings/ATH999"
            }
        }


# ============================================================================
# Pagination Helper
# ============================================================================

class PaginationParams(BaseModel):
    """Standard pagination parameters"""
    limit: int = Field(50, ge=1, le=1000, description="Items per page")
    offset: int = Field(0, ge=0, description="Number of items to skip")
    
    @property
    def skip(self) -> int:
        """Calculate skip value for database queries"""
        return self.offset
    
    @property
    def take(self) -> int:
        """Calculate take value for database queries"""
        return self.limit
