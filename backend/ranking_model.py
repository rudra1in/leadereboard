"""
ORM Models for GameX Leaderboard Microservice

Defines database schema and data models using SQLAlchemy ORM.
Models represent database tables and provide structure for all data operations.
"""

from datetime import datetime
from typing import List, Optional
from sqlalchemy import (
    Column, String, Integer, Float, DateTime, Boolean,
    ForeignKey, Enum, Text, JSON, Index
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum

Base = declarative_base()


class RankingStatusEnum(str, enum.Enum):
    """Ranking computation status"""
    PENDING = "pending"
    COMPUTED = "computed"
    FAILED = "failed"
    INVALID = "invalid"


class ResultSourceEnum(str, enum.Enum):
    """Source of ranking data"""
    OFFICIAL = "official"
    FEDERATION_IMPORT = "federation-import"
    MANUAL = "manual"


class AthleteModel(Base):
    """
    Athlete/Competitor entity.
    
    Represents an individual or team competitor in the ranking system.
    Stores basic profile information and federation status.
    """
    __tablename__ = "athletes"
    
    # Primary key
    athlete_id = Column(String(50), primary_key=True, index=True)
    
    # Basic information
    name = Column(String(255), nullable=False, index=True)
    team_name = Column(String(255), nullable=True)
    profile_data = Column(JSON, default={})  # Extended profile info
    
    # Federation tracking
    federation_id = Column(String(50), nullable=True, index=True)
    federation_source = Column(Boolean, default=False)  # Imported from federation?
    
    # Status and metadata
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    rankings: List['RankingModel'] = relationship(
        "RankingModel",
        back_populates="athlete",
        cascade="all, delete-orphan"
    )
    ranking_entries: List['RankingEntryModel'] = relationship(
        "RankingEntryModel",
        back_populates="athlete",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<AthleteModel(athlete_id={self.athlete_id}, name={self.name})>"


class CategoryModel(Base):
    """
    Competitive category/division.
    
    Represents a category in the ranking system (e.g., Elite Mixed, Junior, etc.)
    Categories can have specific eligibility rules and configurations.
    """
    __tablename__ = "categories"
    
    # Primary key
    category_id = Column(String(50), primary_key=True, index=True)
    
    # Category information
    name = Column(String(255), nullable=False, unique=True, index=True)
    sport_id = Column(String(50), nullable=False, index=True)
    display_order = Column(Integer, default=0)
    
    # Configuration
    config_data = Column(JSON, default={})  # Eligibility rules, age ranges, etc.
    
    # Status and metadata
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    rankings: List['RankingModel'] = relationship(
        "RankingModel",
        back_populates="category"
    )
    
    __table_args__ = (
        Index('idx_sport_active', 'sport_id', 'is_active'),
    )
    
    def __repr__(self) -> str:
        return f"<CategoryModel(category_id={self.category_id}, name={self.name})>"


class SportModel(Base):
    """
    Sport entity.
    
    Represents a sport in the platform (e.g., Tennis, Basketball, etc.)
    Groups categories and manages sport-specific configurations.
    """
    __tablename__ = "sports"
    
    # Primary key
    sport_id = Column(String(50), primary_key=True, index=True)
    
    # Sport information
    name = Column(String(255), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)
    
    # Configuration
    config_data = Column(JSON, default={})  # Sport-specific rules, formats, etc.
    
    # Status and metadata
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self) -> str:
        return f"<SportModel(sport_id={self.sport_id}, name={self.name})>"


class RankingConfigModel(Base):
    """
    Ranking configuration entity.
    
    Stores versioned ranking configurations including points tables,
    decay factors, windows, and other ranking computation parameters.
    """
    __tablename__ = "ranking_configs"
    
    # Primary key and version tracking
    config_id = Column(String(50), primary_key=True, index=True)
    version = Column(Integer, default=1, index=True)
    
    # Configuration scope
    sport_id = Column(String(50), nullable=True, index=True)
    category_id = Column(String(50), nullable=True, index=True)
    
    # Configuration details
    points_table = Column(JSON, nullable=False)  # {placement: points, ...}
    time_window = Column(String(50), default="rolling-12")  # rolling-12, ytd, all-time
    decay_factor = Column(Float, default=0.0)  # Points decay over time
    max_events = Column(Integer, nullable=True)  # Max events to count
    
    # Ranking engine version
    engine_version = Column(String(20), default="1.0")
    
    # Status and metadata
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    activated_at = Column(DateTime, nullable=True)
    deactivated_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    rankings: List['RankingModel'] = relationship(
        "RankingModel",
        back_populates="config"
    )
    
    __table_args__ = (
        Index('idx_sport_category_active', 'sport_id', 'category_id', 'is_active'),
    )
    
    def __repr__(self) -> str:
        return f"<RankingConfigModel(config_id={self.config_id}, version={self.version})>"


class RankingModel(Base):
    """
    Ranking entry entity.
    
    Represents a single ranking position for an athlete in a category.
    Tracks movement, points, and supports multiple ranking systems.
    """
    __tablename__ = "rankings"
    
    # Primary key
    ranking_id = Column(String(50), primary_key=True, index=True)
    
    # Foreign keys
    athlete_id = Column(String(50), ForeignKey('athletes.athlete_id'), nullable=False, index=True)
    category_id = Column(String(50), ForeignKey('categories.category_id'), nullable=False, index=True)
    config_id = Column(String(50), ForeignKey('ranking_configs.config_id'), nullable=False)
    
    # Ranking data
    rank = Column(Integer, nullable=False, index=True)
    points = Column(Float, nullable=False)
    
    # Movement tracking
    previous_rank = Column(Integer, nullable=True)
    movement = Column(Integer, default=0)  # positive = up, negative = down
    
    # Source tracking
    is_federation_source = Column(Boolean, default=False, index=True)
    source = Column(String(50), default="official")
    
    # Metadata
    event_count = Column(Integer, default=0)
    last_update = Column(DateTime, default=datetime.utcnow, index=True)
    computed_at = Column(DateTime, nullable=True)
    
    # Status
    status = Column(String(20), default="computed")
    
    # Relationships
    athlete = relationship("AthleteModel", back_populates="rankings")
    category = relationship("CategoryModel", back_populates="rankings")
    config = relationship("RankingConfigModel", back_populates="rankings")
    entries: List['RankingEntryModel'] = relationship(
        "RankingEntryModel",
        back_populates="ranking",
        cascade="all, delete-orphan"
    )
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_athlete_category_config', 'athlete_id', 'category_id', 'config_id'),
        Index('idx_rank_category', 'rank', 'category_id'),
        Index('idx_points_category', 'points', 'category_id'),
    )
    
    def __repr__(self) -> str:
        return f"<RankingModel(ranking_id={self.ranking_id}, rank={self.rank}, points={self.points})>"


class RankingEntryModel(Base):
    """
    Individual ranking entry (contributing event).
    
    Tracks individual events that contribute to an athlete's ranking.
    Provides explainability for how rankings are calculated.
    """
    __tablename__ = "ranking_entries"
    
    # Primary key
    entry_id = Column(String(50), primary_key=True, index=True)
    
    # Foreign keys
    ranking_id = Column(String(50), ForeignKey('rankings.ranking_id'), nullable=False, index=True)
    athlete_id = Column(String(50), ForeignKey('athletes.athlete_id'), nullable=False, index=True)
    event_id = Column(String(50), nullable=False, index=True)
    
    # Event data
    event_name = Column(String(255), nullable=False)
    event_date = Column(DateTime, nullable=False, index=True)
    
    # Points data
    points_awarded = Column(Float, nullable=False)
    placement = Column(String(50), nullable=True)  # 1st, 2nd, etc.
    
    # Source and metadata
    source = Column(String(50), default="official")
    category_id = Column(String(50), nullable=False)
    rule_version = Column(String(20), nullable=True)
    
    # Relationships
    ranking = relationship("RankingModel", back_populates="entries")
    athlete = relationship("AthleteModel", back_populates="ranking_entries")
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_ranking_event', 'ranking_id', 'event_id'),
        Index('idx_athlete_event', 'athlete_id', 'event_id'),
    )
    
    def __repr__(self) -> str:
        return f"<RankingEntryModel(entry_id={self.entry_id}, points={self.points_awarded})>"


class RankingHistoryModel(Base):
    """
    Ranking history/audit trail.
    
    Tracks all changes to rankings over time for auditing and analysis.
    Enables historical rank tracking and change detection.
    """
    __tablename__ = "ranking_history"
    
    # Primary key
    history_id = Column(String(50), primary_key=True, index=True)
    
    # Foreign keys
    athlete_id = Column(String(50), ForeignKey('athletes.athlete_id'), nullable=False, index=True)
    category_id = Column(String(50), ForeignKey('categories.category_id'), nullable=False, index=True)
    
    # Historical data
    rank = Column(Integer, nullable=False, index=True)
    points = Column(Float, nullable=False)
    movement = Column(Integer, default=0)
    
    # Change tracking
    event_triggered = Column(String(255), nullable=True)
    change_reason = Column(String(255), nullable=True)
    recompute_id = Column(String(50), nullable=True)
    
    # Timestamp for this ranking state
    recorded_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    __table_args__ = (
        Index('idx_athlete_date', 'athlete_id', 'recorded_at'),
        Index('idx_category_date', 'category_id', 'recorded_at'),
    )
    
    def __repr__(self) -> str:
        return f"<RankingHistoryModel(athlete_id={self.athlete_id}, rank={self.rank})>"


class RankingRecomputeModel(Base):
    """
    Ranking recomputation event tracking.
    
    Tracks ranking recomputations for auditing and understanding
    when and why rankings were recalculated.
    """
    __tablename__ = "ranking_recomputes"
    
    # Primary key
    recompute_id = Column(String(50), primary_key=True, index=True)
    
    # Scope
    sport_id = Column(String(50), nullable=True, index=True)
    category_id = Column(String(50), nullable=True, index=True)
    
    # Trigger information
    triggered_by = Column(String(100), nullable=True)  # event, admin, scheduled
    trigger_id = Column(String(50), nullable=True)  # event_id, admin_user, etc.
    
    # Computation details
    affected_rankings = Column(Integer, default=0)
    compute_time_ms = Column(Integer, nullable=True)
    status = Column(String(20), default="pending")  # pending, success, failed
    error_message = Column(Text, nullable=True)
    
    # Configuration used
    config_id = Column(String(50), nullable=True)
    config_version = Column(Integer, nullable=True)
    
    # Results
    rankings_changed = Column(Integer, default=0)
    rankings_stable = Column(Integer, default=0)
    
    # Timestamps
    started_at = Column(DateTime, default=datetime.utcnow, index=True)
    completed_at = Column(DateTime, nullable=True)
    
    __table_args__ = (
        Index('idx_status_timestamp', 'status', 'completed_at'),
    )
    
    def __repr__(self) -> str:
        return f"<RankingRecomputeModel(recompute_id={self.recompute_id}, status={self.status})>"


class QualificationScenarioModel(Base):
    """
    Qualification scenario/projection.
    
    Stores pre-computed qualification scenarios showing potential
    outcomes based on published rules.
    """
    __tablename__ = "qualification_scenarios"
    
    # Primary key
    scenario_id = Column(String(50), primary_key=True, index=True)
    
    # Foreign keys
    athlete_id = Column(String(50), ForeignKey('athletes.athlete_id'), nullable=False, index=True)
    category_id = Column(String(50), ForeignKey('categories.category_id'), nullable=False, index=True)
    
    # Scenario data
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Projections
    current_rank = Column(Integer, nullable=False)
    current_points = Column(Float, nullable=False)
    projected_rank = Column(Integer, nullable=False)
    projected_points = Column(Float, nullable=False)
    
    # Conditions and probability
    threshold_description = Column(String(255), nullable=False)
    probability = Column(Float, default=0.5)  # 0.0 to 1.0
    
    # Metadata
    computed_at = Column(DateTime, default=datetime.utcnow)
    valid_until = Column(DateTime, nullable=True)
    
    __table_args__ = (
        Index('idx_athlete_category_date', 'athlete_id', 'category_id', 'computed_at'),
    )
    
    def __repr__(self) -> str:
        return f"<QualificationScenarioModel(scenario_id={self.scenario_id}, name={self.name})>"
