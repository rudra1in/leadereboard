"""
Repository layer for data access operations.

Repositories provide a clean abstraction over the database layer.
They implement the Data Access Object (DAO) pattern.
"""

from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
from sqlalchemy import and_, desc, func
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from models.ranking_model import (
    AthleteModel, CategoryModel, SportModel, RankingModel,
    RankingEntryModel, RankingConfigModel, RankingHistoryModel,
    RankingRecomputeModel, QualificationScenarioModel
)


class BaseRepository:
    """
    Base repository providing common CRUD operations.
    
    Implements generic repository pattern for consistent data access
    across all repository implementations.
    """
    
    def __init__(self, db: Session, model):
        """
        Initialize repository with database session and model.
        
        Args:
            db: SQLAlchemy database session
            model: SQLAlchemy model class
        """
        self.db = db
        self.model = model
    
    def get_by_id(self, id: str) -> Optional[Any]:
        """Get single record by primary key"""
        try:
            return self.db.query(self.model).filter(
                self.model.id == id if hasattr(self.model, 'id')
                else list(self.model.__table__.primary_key)[0] == id
            ).first()
        except SQLAlchemyError as e:
            raise RepositoryException(f"Failed to get {self.model.__name__}: {str(e)}")
    
    def create(self, obj: Any) -> Any:
        """Create new record"""
        try:
            self.db.add(obj)
            self.db.commit()
            self.db.refresh(obj)
            return obj
        except SQLAlchemyError as e:
            self.db.rollback()
            raise RepositoryException(f"Failed to create {self.model.__name__}: {str(e)}")
    
    def update(self, id: str, data: Dict[str, Any]) -> Optional[Any]:
        """Update existing record"""
        try:
            obj = self.get_by_id(id)
            if not obj:
                return None
            
            for key, value in data.items():
                if hasattr(obj, key):
                    setattr(obj, key, value)
            
            self.db.commit()
            self.db.refresh(obj)
            return obj
        except SQLAlchemyError as e:
            self.db.rollback()
            raise RepositoryException(f"Failed to update {self.model.__name__}: {str(e)}")
    
    def delete(self, id: str) -> bool:
        """Delete record"""
        try:
            obj = self.get_by_id(id)
            if not obj:
                return False
            
            self.db.delete(obj)
            self.db.commit()
            return True
        except SQLAlchemyError as e:
            self.db.rollback()
            raise RepositoryException(f"Failed to delete {self.model.__name__}: {str(e)}")
    
    def list_all(self, limit: int = 100, offset: int = 0) -> Tuple[List[Any], int]:
        """List all records with pagination"""
        try:
            query = self.db.query(self.model)
            total = query.count()
            items = query.offset(offset).limit(limit).all()
            return items, total
        except SQLAlchemyError as e:
            raise RepositoryException(f"Failed to list {self.model.__name__}: {str(e)}")


class AthleteRepository(BaseRepository):
    """Repository for athlete data operations"""
    
    def __init__(self, db: Session):
        super().__init__(db, AthleteModel)
    
    def get_by_athlete_id(self, athlete_id: str) -> Optional[AthleteModel]:
        """Get athlete by athlete_id"""
        try:
            return self.db.query(AthleteModel).filter(
                AthleteModel.athlete_id == athlete_id
            ).first()
        except SQLAlchemyError as e:
            raise RepositoryException(f"Failed to get athlete {athlete_id}: {str(e)}")
    
    def get_active_athletes(
        self,
        limit: int = 100,
        offset: int = 0
    ) -> Tuple[List[AthleteModel], int]:
        """Get all active athletes"""
        try:
            query = self.db.query(AthleteModel).filter(
                AthleteModel.is_active == True
            )
            total = query.count()
            athletes = query.offset(offset).limit(limit).all()
            return athletes, total
        except SQLAlchemyError as e:
            raise RepositoryException(f"Failed to get active athletes: {str(e)}")
    
    def search_athletes(
        self,
        search_term: str,
        limit: int = 100,
        offset: int = 0
    ) -> Tuple[List[AthleteModel], int]:
        """Search athletes by name"""
        try:
            query = self.db.query(AthleteModel).filter(
                AthleteModel.name.ilike(f"%{search_term}%"),
                AthleteModel.is_active == True
            )
            total = query.count()
            athletes = query.offset(offset).limit(limit).all()
            return athletes, total
        except SQLAlchemyError as e:
            raise RepositoryException(f"Failed to search athletes: {str(e)}")
    
    def get_federation_athletes(self) -> List[AthleteModel]:
        """Get all federation-sourced athletes"""
        try:
            return self.db.query(AthleteModel).filter(
                AthleteModel.federation_source == True,
                AthleteModel.is_active == True
            ).all()
        except SQLAlchemyError as e:
            raise RepositoryException(f"Failed to get federation athletes: {str(e)}")


class CategoryRepository(BaseRepository):
    """Repository for category data operations"""
    
    def __init__(self, db: Session):
        super().__init__(db, CategoryModel)
    
    def get_by_category_id(self, category_id: str) -> Optional[CategoryModel]:
        """Get category by category_id"""
        try:
            return self.db.query(CategoryModel).filter(
                CategoryModel.category_id == category_id
            ).first()
        except SQLAlchemyError as e:
            raise RepositoryException(f"Failed to get category {category_id}: {str(e)}")
    
    def get_categories_by_sport(self, sport_id: str) -> List[CategoryModel]:
        """Get all categories for a sport"""
        try:
            return self.db.query(CategoryModel).filter(
                CategoryModel.sport_id == sport_id,
                CategoryModel.is_active == True
            ).order_by(CategoryModel.display_order).all()
        except SQLAlchemyError as e:
            raise RepositoryException(f"Failed to get categories for sport {sport_id}: {str(e)}")
    
    def get_active_categories(self) -> List[CategoryModel]:
        """Get all active categories"""
        try:
            return self.db.query(CategoryModel).filter(
                CategoryModel.is_active == True
            ).order_by(CategoryModel.display_order).all()
        except SQLAlchemyError as e:
            raise RepositoryException(f"Failed to get active categories: {str(e)}")


class RankingRepository(BaseRepository):
    """Repository for ranking data operations"""
    
    def __init__(self, db: Session):
        super().__init__(db, RankingModel)
    
    def get_by_ranking_id(self, ranking_id: str) -> Optional[RankingModel]:
        """Get ranking by ranking_id"""
        try:
            return self.db.query(RankingModel).filter(
                RankingModel.ranking_id == ranking_id
            ).first()
        except SQLAlchemyError as e:
            raise RepositoryException(f"Failed to get ranking {ranking_id}: {str(e)}")
    
    def get_rankings_by_category(
        self,
        category_id: str,
        sport_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> Tuple[List[RankingModel], int]:
        """Get rankings for a category, optionally filtered by sport"""
        try:
            query = self.db.query(RankingModel).filter(
                RankingModel.category_id == category_id
            )
            
            if sport_id:
                query = query.filter(
                    RankingModel.category.has(CategoryModel.sport_id == sport_id)
                )
            
            total = query.count()
            rankings = query.order_by(RankingModel.rank).offset(offset).limit(limit).all()
            return rankings, total
        except SQLAlchemyError as e:
            raise RepositoryException(f"Failed to get rankings for category: {str(e)}")
    
    def get_ranking_by_athlete_category(
        self,
        athlete_id: str,
        category_id: str
    ) -> Optional[RankingModel]:
        """Get ranking for specific athlete in category"""
        try:
            return self.db.query(RankingModel).filter(
                RankingModel.athlete_id == athlete_id,
                RankingModel.category_id == category_id
            ).order_by(desc(RankingModel.last_update)).first()
        except SQLAlchemyError as e:
            raise RepositoryException(f"Failed to get athlete ranking: {str(e)}")
    
    def get_rankings_by_sport(
        self,
        sport_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> Tuple[List[RankingModel], int]:
        """Get rankings for all categories in a sport"""
        try:
            query = self.db.query(RankingModel).filter(
                RankingModel.category.has(CategoryModel.sport_id == sport_id)
            )
            total = query.count()
            rankings = query.order_by(RankingModel.rank).offset(offset).limit(limit).all()
            return rankings, total
        except SQLAlchemyError as e:
            raise RepositoryException(f"Failed to get rankings for sport: {str(e)}")
    
    def get_top_rankings(
        self,
        category_id: str,
        limit: int = 10
    ) -> List[RankingModel]:
        """Get top N rankings in category"""
        try:
            return self.db.query(RankingModel).filter(
                RankingModel.category_id == category_id
            ).order_by(RankingModel.rank).limit(limit).all()
        except SQLAlchemyError as e:
            raise RepositoryException(f"Failed to get top rankings: {str(e)}")
    
    def get_federation_rankings(
        self,
        category_id: Optional[str] = None
    ) -> List[RankingModel]:
        """Get all federation-sourced rankings"""
        try:
            query = self.db.query(RankingModel).filter(
                RankingModel.is_federation_source == True
            )
            
            if category_id:
                query = query.filter(RankingModel.category_id == category_id)
            
            return query.all()
        except SQLAlchemyError as e:
            raise RepositoryException(f"Failed to get federation rankings: {str(e)}")
    
    def search_rankings(
        self,
        category_id: str,
        search_term: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> Tuple[List[RankingModel], int]:
        """Search rankings by athlete name"""
        try:
            query = self.db.query(RankingModel).filter(
                RankingModel.category_id == category_id
            )
            
            if search_term:
                query = query.filter(
                    RankingModel.athlete.has(
                        AthleteModel.name.ilike(f"%{search_term}%")
                    )
                )
            
            total = query.count()
            rankings = query.order_by(RankingModel.rank).offset(offset).limit(limit).all()
            return rankings, total
        except SQLAlchemyError as e:
            raise RepositoryException(f"Failed to search rankings: {str(e)}")


class RankingEntryRepository(BaseRepository):
    """Repository for ranking entry (contributing event) operations"""
    
    def __init__(self, db: Session):
        super().__init__(db, RankingEntryModel)
    
    def get_entries_by_ranking(self, ranking_id: str) -> List[RankingEntryModel]:
        """Get all entries for a ranking"""
        try:
            return self.db.query(RankingEntryModel).filter(
                RankingEntryModel.ranking_id == ranking_id
            ).order_by(desc(RankingEntryModel.points_awarded)).all()
        except SQLAlchemyError as e:
            raise RepositoryException(f"Failed to get ranking entries: {str(e)}")
    
    def get_entries_by_athlete(
        self,
        athlete_id: str,
        days: Optional[int] = None
    ) -> List[RankingEntryModel]:
        """Get all entries for an athlete, optionally within timeframe"""
        try:
            query = self.db.query(RankingEntryModel).filter(
                RankingEntryModel.athlete_id == athlete_id
            )
            
            if days:
                start_date = datetime.utcnow() - timedelta(days=days)
                query = query.filter(RankingEntryModel.event_date >= start_date)
            
            return query.order_by(desc(RankingEntryModel.event_date)).all()
        except SQLAlchemyError as e:
            raise RepositoryException(f"Failed to get athlete entries: {str(e)}")
    
    def get_contributing_events(self, ranking_id: str) -> List[RankingEntryModel]:
        """Get all contributing events for ranking explainability"""
        try:
            return self.db.query(RankingEntryModel).filter(
                RankingEntryModel.ranking_id == ranking_id
            ).order_by(desc(RankingEntryModel.event_date)).all()
        except SQLAlchemyError as e:
            raise RepositoryException(f"Failed to get contributing events: {str(e)}")


class RankingConfigRepository(BaseRepository):
    """Repository for ranking configuration operations"""
    
    def __init__(self, db: Session):
        super().__init__(db, RankingConfigModel)
    
    def get_by_config_id(self, config_id: str) -> Optional[RankingConfigModel]:
        """Get config by config_id"""
        try:
            return self.db.query(RankingConfigModel).filter(
                RankingConfigModel.config_id == config_id
            ).first()
        except SQLAlchemyError as e:
            raise RepositoryException(f"Failed to get config {config_id}: {str(e)}")
    
    def get_active_config(
        self,
        sport_id: Optional[str] = None,
        category_id: Optional[str] = None
    ) -> Optional[RankingConfigModel]:
        """Get active config for sport/category"""
        try:
            query = self.db.query(RankingConfigModel).filter(
                RankingConfigModel.is_active == True
            )
            
            if sport_id:
                query = query.filter(RankingConfigModel.sport_id == sport_id)
            
            if category_id:
                query = query.filter(RankingConfigModel.category_id == category_id)
            
            return query.order_by(desc(RankingConfigModel.activated_at)).first()
        except SQLAlchemyError as e:
            raise RepositoryException(f"Failed to get active config: {str(e)}")
    
    def get_config_versions(self, config_id: str) -> List[RankingConfigModel]:
        """Get all versions of a config"""
        try:
            return self.db.query(RankingConfigModel).filter(
                RankingConfigModel.config_id == config_id
            ).order_by(desc(RankingConfigModel.version)).all()
        except SQLAlchemyError as e:
            raise RepositoryException(f"Failed to get config versions: {str(e)}")


class RankingHistoryRepository(BaseRepository):
    """Repository for ranking history/audit operations"""
    
    def __init__(self, db: Session):
        super().__init__(db, RankingHistoryModel)
    
    def get_athlete_history(
        self,
        athlete_id: str,
        category_id: str,
        days: Optional[int] = None,
        limit: int = 100
    ) -> List[RankingHistoryModel]:
        """Get ranking history for athlete in category"""
        try:
            query = self.db.query(RankingHistoryModel).filter(
                RankingHistoryModel.athlete_id == athlete_id,
                RankingHistoryModel.category_id == category_id
            )
            
            if days:
                start_date = datetime.utcnow() - timedelta(days=days)
                query = query.filter(RankingHistoryModel.recorded_at >= start_date)
            
            return query.order_by(desc(RankingHistoryModel.recorded_at)).limit(limit).all()
        except SQLAlchemyError as e:
            raise RepositoryException(f"Failed to get athlete history: {str(e)}")
    
    def get_category_history(
        self,
        category_id: str,
        days: int = 90
    ) -> List[RankingHistoryModel]:
        """Get ranking changes for category over period"""
        try:
            start_date = datetime.utcnow() - timedelta(days=days)
            return self.db.query(RankingHistoryModel).filter(
                RankingHistoryModel.category_id == category_id,
                RankingHistoryModel.recorded_at >= start_date
            ).order_by(desc(RankingHistoryModel.recorded_at)).all()
        except SQLAlchemyError as e:
            raise RepositoryException(f"Failed to get category history: {str(e)}")


class RankingRecomputeRepository(BaseRepository):
    """Repository for ranking recomputation tracking"""
    
    def __init__(self, db: Session):
        super().__init__(db, RankingRecomputeModel)
    
    def get_by_recompute_id(self, recompute_id: str) -> Optional[RankingRecomputeModel]:
        """Get recompute event by ID"""
        try:
            return self.db.query(RankingRecomputeModel).filter(
                RankingRecomputeModel.recompute_id == recompute_id
            ).first()
        except SQLAlchemyError as e:
            raise RepositoryException(f"Failed to get recompute event: {str(e)}")
    
    def get_recent_recomputes(self, limit: int = 20) -> List[RankingRecomputeModel]:
        """Get recent recomputation events"""
        try:
            return self.db.query(RankingRecomputeModel).order_by(
                desc(RankingRecomputeModel.started_at)
            ).limit(limit).all()
        except SQLAlchemyError as e:
            raise RepositoryException(f"Failed to get recent recomputes: {str(e)}")
    
    def get_failed_recomputes(self) -> List[RankingRecomputeModel]:
        """Get failed recomputation events"""
        try:
            return self.db.query(RankingRecomputeModel).filter(
                RankingRecomputeModel.status == "failed"
            ).order_by(desc(RankingRecomputeModel.started_at)).all()
        except SQLAlchemyError as e:
            raise RepositoryException(f"Failed to get failed recomputes: {str(e)}")


class QualificationScenarioRepository(BaseRepository):
    """Repository for qualification scenario operations"""
    
    def __init__(self, db: Session):
        super().__init__(db, QualificationScenarioModel)
    
    def get_scenarios_for_athlete(
        self,
        athlete_id: str,
        category_id: str
    ) -> List[QualificationScenarioModel]:
        """Get all scenarios for athlete in category"""
        try:
            return self.db.query(QualificationScenarioModel).filter(
                QualificationScenarioModel.athlete_id == athlete_id,
                QualificationScenarioModel.category_id == category_id
            ).filter(
                QualificationScenarioModel.valid_until >= datetime.utcnow()
            ).all()
        except SQLAlchemyError as e:
            raise RepositoryException(f"Failed to get qualification scenarios: {str(e)}")


class RepositoryException(Exception):
    """Custom exception for repository operations"""
    pass
