"""
Service layer for business logic.

Services encapsulate business rules and orchestrate repository operations.
Implements separation of concerns and makes code testable.
"""

from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
from uuid import uuid4
from sqlalchemy.orm import Session
import logging

from models.ranking_model import (
    AthleteModel, RankingModel, RankingEntryModel,
    RankingConfigModel, RankingHistoryModel, RankingRecomputeModel,
    QualificationScenarioModel, CategoryModel
)
from repositories.ranking_repository import (
    AthleteRepository, RankingRepository, RankingEntryRepository,
    RankingConfigRepository, RankingHistoryRepository,
    RankingRecomputeRepository, QualificationScenarioRepository,
    CategoryRepository, RepositoryException
)
from schemas.ranking_schema import (
    RankingResponse, RankingDetailResponse, AthleteQualificationResponse,
    QualificationScenarioResponse, RankingExplainabilityResponse,
    RankingRecomputeResponse
)


logger = logging.getLogger(__name__)


class RankingService:
    """
    Service for ranking operations.
    
    Handles all business logic related to rankings including
    computation, filtering, and data transformation.
    """
    
    def __init__(self, db: Session):
        """Initialize service with repository instances"""
        self.db = db
        self.athlete_repo = AthleteRepository(db)
        self.ranking_repo = RankingRepository(db)
        self.entry_repo = RankingEntryRepository(db)
        self.config_repo = RankingConfigRepository(db)
        self.history_repo = RankingHistoryRepository(db)
        self.recompute_repo = RankingRecomputeRepository(db)
        self.category_repo = CategoryRepository(db)
        self.scenario_repo = QualificationScenarioRepository(db)
    
    # ========================================================================
    # RANKING RETRIEVAL
    # ========================================================================
    
    def get_ranking(self, ranking_id: str) -> Optional[RankingResponse]:
        """Get single ranking by ID"""
        try:
            ranking = self.ranking_repo.get_by_ranking_id(ranking_id)
            if not ranking:
                return None
            return self._to_ranking_response(ranking)
        except RepositoryException as e:
            logger.error(f"Error getting ranking: {str(e)}")
            raise ServiceException(f"Failed to get ranking: {str(e)}")
    
    def get_ranking_detail(self, ranking_id: str) -> Optional[RankingDetailResponse]:
        """Get ranking with all contributing events"""
        try:
            ranking = self.ranking_repo.get_by_ranking_id(ranking_id)
            if not ranking:
                return None
            
            entries = self.entry_repo.get_entries_by_ranking(ranking_id)
            
            response = self._to_ranking_response(ranking)
            response.contributing_events = [
                self._to_entry_response(entry) for entry in entries
            ]
            
            return response
        except RepositoryException as e:
            logger.error(f"Error getting ranking detail: {str(e)}")
            raise ServiceException(f"Failed to get ranking detail: {str(e)}")
    
    def get_rankings(
        self,
        category_id: str,
        sport_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Tuple[List[RankingResponse], int]:
        """Get paginated rankings for category"""
        try:
            rankings, total = self.ranking_repo.get_rankings_by_category(
                category_id, sport_id, limit, offset
            )
            return [self._to_ranking_response(r) for r in rankings], total
        except RepositoryException as e:
            logger.error(f"Error getting rankings: {str(e)}")
            raise ServiceException(f"Failed to get rankings: {str(e)}")
    
    def search_rankings(
        self,
        category_id: str,
        search_term: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Tuple[List[RankingResponse], int]:
        """Search rankings by athlete name"""
        try:
            rankings, total = self.ranking_repo.search_rankings(
                category_id, search_term, limit, offset
            )
            return [self._to_ranking_response(r) for r in rankings], total
        except RepositoryException as e:
            logger.error(f"Error searching rankings: {str(e)}")
            raise ServiceException(f"Failed to search rankings: {str(e)}")
    
    def get_top_rankings(
        self,
        category_id: str,
        limit: int = 10
    ) -> List[RankingResponse]:
        """Get top N rankings in category"""
        try:
            rankings = self.ranking_repo.get_top_rankings(category_id, limit)
            return [self._to_ranking_response(r) for r in rankings]
        except RepositoryException as e:
            logger.error(f"Error getting top rankings: {str(e)}")
            raise ServiceException(f"Failed to get top rankings: {str(e)}")
    
    # ========================================================================
    # RANKING EXPLANATION AND SCENARIOS
    # ========================================================================
    
    def get_ranking_explainability(
        self,
        athlete_id: str,
        category_id: str
    ) -> Optional[RankingExplainabilityResponse]:
        """Get ranking explanation with contributing events"""
        try:
            ranking = self.ranking_repo.get_ranking_by_athlete_category(
                athlete_id, category_id
            )
            
            if not ranking:
                return None
            
            entries = self.entry_repo.get_contributing_events(ranking.ranking_id)
            config = self.config_repo.get_by_config_id(ranking.config_id)
            
            # Determine time window
            time_window = config.time_window if config else "rolling-12"
            if time_window == "rolling-12":
                period_start = datetime.utcnow() - timedelta(days=365)
            else:
                period_start = datetime.utcnow().replace(month=1, day=1)
            
            return RankingExplainabilityResponse(
                athlete_id=athlete_id,
                total_points=ranking.points,
                contributing_event_count=len(entries),
                events=[self._to_entry_response(e) for e in entries],
                period_start=period_start,
                period_end=datetime.utcnow(),
                window_type=time_window,
                decay_factor=config.decay_factor if config else 0.0
            )
        except RepositoryException as e:
            logger.error(f"Error getting explainability: {str(e)}")
            raise ServiceException(f"Failed to get explainability: {str(e)}")
    
    def get_qualification_scenarios(
        self,
        athlete_id: str,
        category_id: str
    ) -> Optional[AthleteQualificationResponse]:
        """Get qualification scenarios for athlete"""
        try:
            ranking = self.ranking_repo.get_ranking_by_athlete_category(
                athlete_id, category_id
            )
            
            if not ranking:
                return None
            
            scenarios = self.scenario_repo.get_scenarios_for_athlete(
                athlete_id, category_id
            )
            
            return AthleteQualificationResponse(
                athlete_id=athlete_id,
                current_rank=ranking.rank,
                current_points=ranking.points,
                scenarios=[
                    QualificationScenarioResponse.from_orm(s) for s in scenarios
                ]
            )
        except RepositoryException as e:
            logger.error(f"Error getting qualification scenarios: {str(e)}")
            raise ServiceException(f"Failed to get qualification scenarios: {str(e)}")
    
    # ========================================================================
    # RANKING HISTORY
    # ========================================================================
    
    def get_ranking_history(
        self,
        athlete_id: str,
        category_id: str,
        days: Optional[int] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get ranking history for athlete"""
        try:
            history = self.history_repo.get_athlete_history(
                athlete_id, category_id, days, limit
            )
            
            return [
                {
                    "date": h.recorded_at,
                    "rank": h.rank,
                    "points": h.points,
                    "movement": h.movement,
                    "event_triggered": h.event_triggered
                }
                for h in history
            ]
        except RepositoryException as e:
            logger.error(f"Error getting ranking history: {str(e)}")
            raise ServiceException(f"Failed to get ranking history: {str(e)}")
    
    def record_ranking_history(
        self,
        athlete_id: str,
        category_id: str,
        rank: int,
        points: float,
        movement: int,
        event_triggered: Optional[str] = None,
        change_reason: Optional[str] = None
    ) -> RankingHistoryModel:
        """Record ranking change in history"""
        try:
            history = RankingHistoryModel(
                history_id=str(uuid4()),
                athlete_id=athlete_id,
                category_id=category_id,
                rank=rank,
                points=points,
                movement=movement,
                event_triggered=event_triggered,
                change_reason=change_reason
            )
            
            return self.history_repo.create(history)
        except RepositoryException as e:
            logger.error(f"Error recording history: {str(e)}")
            raise ServiceException(f"Failed to record ranking history: {str(e)}")
    
    # ========================================================================
    # RANKING COMPUTATION
    # ========================================================================
    
    def compute_rankings(
        self,
        category_id: str,
        config_id: str,
        athlete_ids: Optional[List[str]] = None
    ) -> Tuple[int, int]:
        """
        Compute rankings for category using config.
        
        Returns: (total_affected, total_changed)
        """
        try:
            config = self.config_repo.get_by_config_id(config_id)
            if not config:
                raise ServiceException(f"Config {config_id} not found")
            
            # Get athletes to compute
            if athlete_ids:
                athletes = [self.athlete_repo.get_by_athlete_id(aid) for aid in athlete_ids]
            else:
                athletes, _ = self.athlete_repo.get_active_athletes(limit=10000)
            
            total_affected = len([a for a in athletes if a])
            total_changed = 0
            
            # Compute each athlete's ranking
            for athlete in athletes:
                if not athlete:
                    continue
                
                old_rank = None
                old_points = None
                
                # Get existing ranking
                existing = self.ranking_repo.get_ranking_by_athlete_category(
                    athlete.athlete_id, category_id
                )
                
                if existing:
                    old_rank = existing.rank
                    old_points = existing.points
                
                # Compute new ranking
                new_rank, new_points = self._compute_athlete_ranking(
                    athlete.athlete_id, category_id, config
                )
                
                # Update or create ranking
                if existing:
                    existing.rank = new_rank
                    existing.points = new_points
                    existing.previous_rank = old_rank
                    existing.movement = old_rank - new_rank if old_rank else 0
                    existing.last_update = datetime.utcnow()
                    self.db.commit()
                    
                    if new_rank != old_rank or new_points != old_points:
                        total_changed += 1
                        
                        # Record history
                        self.record_ranking_history(
                            athlete.athlete_id, category_id,
                            new_rank, new_points,
                            existing.movement
                        )
                else:
                    new_ranking = RankingModel(
                        ranking_id=str(uuid4()),
                        athlete_id=athlete.athlete_id,
                        category_id=category_id,
                        config_id=config_id,
                        rank=new_rank,
                        points=new_points,
                        previous_rank=None,
                        movement=0
                    )
                    self.ranking_repo.create(new_ranking)
                    total_changed += 1
            
            logger.info(f"Computed {total_affected} rankings, {total_changed} changed")
            return total_affected, total_changed
        except Exception as e:
            logger.error(f"Error computing rankings: {str(e)}")
            raise ServiceException(f"Failed to compute rankings: {str(e)}")
    
    def _compute_athlete_ranking(
        self,
        athlete_id: str,
        category_id: str,
        config: RankingConfigModel
    ) -> Tuple[int, float]:
        """Compute ranking position and points for athlete"""
        try:
            # Get athlete's entries
            entries = self.entry_repo.get_entries_by_athlete(athlete_id)
            
            if not entries:
                return float('inf'), 0.0
            
            # Filter to config window
            window_start = self._get_window_start(config.time_window)
            filtered_entries = [
                e for e in entries
                if e.event_date >= window_start
            ]
            
            # Apply max events limit
            if config.max_events:
                filtered_entries = sorted(
                    filtered_entries,
                    key=lambda e: e.points_awarded,
                    reverse=True
                )[:config.max_events]
            
            # Calculate total points with decay
            total_points = 0.0
            for entry in filtered_entries:
                points = entry.points_awarded
                
                if config.decay_factor > 0:
                    age_days = (datetime.utcnow() - entry.event_date).days
                    decay = config.decay_factor * (age_days / 365.0)
                    points = points * (1 - decay)
                
                total_points += points
            
            # Get rank (simplified - would normally count how many are ahead)
            rank = self._calculate_rank(athlete_id, category_id, total_points)
            
            return rank, total_points
        except Exception as e:
            logger.error(f"Error computing athlete ranking: {str(e)}")
            raise ServiceException(f"Failed to compute athlete ranking: {str(e)}")
    
    def _calculate_rank(
        self,
        athlete_id: str,
        category_id: str,
        points: float
    ) -> int:
        """Calculate rank based on points"""
        try:
            # Count how many athletes have more points
            higher_ranking = self.db.query(
                func.count(RankingModel.ranking_id)
            ).filter(
                RankingModel.category_id == category_id,
                RankingModel.points > points
            ).scalar()
            
            return higher_ranking + 1
        except Exception as e:
            logger.error(f"Error calculating rank: {str(e)}")
            return 1
    
    def _get_window_start(self, window_type: str) -> datetime:
        """Get start date for time window"""
        now = datetime.utcnow()
        
        if window_type == "rolling-12":
            return now - timedelta(days=365)
        elif window_type == "ytd":
            return now.replace(month=1, day=1, hour=0, minute=0, second=0)
        elif window_type == "current":
            return now.replace(month=1, day=1, hour=0, minute=0, second=0)
        else:
            return datetime.min
    
    # ========================================================================
    # HELPER METHODS
    # ========================================================================
    
    def _to_ranking_response(self, ranking: RankingModel) -> RankingResponse:
        """Convert ranking model to response schema"""
        return RankingResponse(
            ranking_id=ranking.ranking_id,
            athlete_id=ranking.athlete_id,
            name=ranking.athlete.name if ranking.athlete else "",
            team_name=ranking.athlete.team_name if ranking.athlete else None,
            category_id=ranking.category_id,
            rank=ranking.rank,
            points=ranking.points,
            previous_rank=ranking.previous_rank,
            movement=ranking.movement,
            event_count=ranking.event_count,
            last_update=ranking.last_update,
            is_federation_source=ranking.is_federation_source,
            badge=self._get_rank_badge(ranking.rank, ranking.movement)
        )
    
    def _to_entry_response(self, entry: RankingEntryModel) -> Dict[str, Any]:
        """Convert entry model to response schema"""
        return {
            "entry_id": entry.entry_id,
            "event_id": entry.event_id,
            "event_name": entry.event_name,
            "event_date": entry.event_date,
            "points_awarded": entry.points_awarded,
            "placement": entry.placement,
            "source": entry.source,
            "category_id": entry.category_id,
            "rule_version": entry.rule_version
        }
    
    def _get_rank_badge(self, rank: int, movement: int) -> str:
        """Determine badge type for rank"""
        if rank == 1:
            return "leader"
        elif movement > 0 and movement >= 3:
            return "climbing"
        return "none"


class RankingRecomputeService:
    """
    Service for managing ranking recomputation events.
    
    Handles triggering, tracking, and completing ranking recomputation.
    """
    
    def __init__(self, db: Session, ranking_service: RankingService):
        """Initialize service with dependencies"""
        self.db = db
        self.ranking_service = ranking_service
        self.recompute_repo = RankingRecomputeRepository(db)
        self.config_repo = RankingConfigRepository(db)
        self.category_repo = CategoryRepository(db)
    
    def trigger_recompute(
        self,
        event_id: str,
        sport_id: Optional[str] = None,
        category_id: Optional[str] = None,
        triggered_by: str = "system"
    ) -> RankingRecomputeResponse:
        """Trigger ranking recomputation"""
        try:
            recompute_id = str(uuid4())
            started_at = datetime.utcnow()
            
            # Create recompute record
            recompute = RankingRecomputeModel(
                recompute_id=recompute_id,
                sport_id=sport_id,
                category_id=category_id,
                triggered_by=triggered_by,
                trigger_id=event_id,
                started_at=started_at,
                status="pending"
            )
            
            self.recompute_repo.create(recompute)
            
            # Get config and compute rankings
            config = self.config_repo.get_active_config(sport_id, category_id)
            if not config:
                recompute.status = "failed"
                recompute.error_message = "No active ranking config found"
                self.db.commit()
                raise ServiceException("No active ranking configuration")
            
            # Get affected categories
            if category_id:
                categories = [self.category_repo.get_by_category_id(category_id)]
            else:
                categories = self.category_repo.get_categories_by_sport(sport_id)
            
            affected = 0
            changed = 0
            
            # Compute for each category
            for cat in categories:
                if cat:
                    total, modified = self.ranking_service.compute_rankings(
                        cat.category_id, config.config_id
                    )
                    affected += total
                    changed += modified
            
            # Update recompute record
            recompute.affected_rankings = affected
            recompute.rankings_changed = changed
            recompute.compute_time_ms = int(
                (datetime.utcnow() - started_at).total_seconds() * 1000
            )
            recompute.status = "success"
            recompute.completed_at = datetime.utcnow()
            self.db.commit()
            
            logger.info(
                f"Recompute {recompute_id} completed: "
                f"{affected} affected, {changed} changed"
            )
            
            return self._to_recompute_response(recompute)
        except Exception as e:
            logger.error(f"Error triggering recompute: {str(e)}")
            raise ServiceException(f"Failed to trigger recomputation: {str(e)}")
    
    def _to_recompute_response(
        self,
        recompute: RankingRecomputeModel
    ) -> RankingRecomputeResponse:
        """Convert recompute model to response"""
        return RankingRecomputeResponse(
            recompute_id=recompute.recompute_id,
            status=recompute.status,
            affected_rankings=recompute.affected_rankings,
            rankings_changed=recompute.rankings_changed,
            compute_time_ms=recompute.compute_time_ms or 0,
            started_at=recompute.started_at,
            completed_at=recompute.completed_at,
            error_message=recompute.error_message
        )


class ServiceException(Exception):
    """Custom exception for service operations"""
    pass
