"""
API Router layer for ranking endpoints.

Routers define HTTP API endpoints and request/response handling.
Implements FastAPI patterns with proper error handling and validation.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
import logging

from database import get_db
from services.ranking_service import RankingService, RankingRecomputeService, ServiceException
from schemas.ranking_schema import (
    RankingsFilterRequest, RankingsListResponse, RankingResponse,
    RankingDetailResponse, AthleteQualificationResponse,
    RankingRecomputeRequest, RankingRecomputeResponse,
    ErrorResponse, RankingHistoryResponse
)


logger = logging.getLogger(__name__)


class RankingRouter:
    """
    Router class for ranking endpoints.
    
    Implements the API layer with FastAPI, handling HTTP requests and responses.
    Uses dependency injection for service layer.
    """
    
    def __init__(self):
        """Initialize router"""
        self.router = APIRouter(
            prefix="/api/rankings",
            tags=["rankings"],
            responses={
                400: {"model": ErrorResponse, "description": "Bad Request"},
                404: {"model": ErrorResponse, "description": "Not Found"},
                500: {"model": ErrorResponse, "description": "Internal Server Error"}
            }
        )
        self._register_routes()
    
    def _register_routes(self):
        """Register all routes"""
        self.router.get("/", response_model=RankingsListResponse)(self.get_rankings)
        self.router.get("/{ranking_id}", response_model=RankingResponse)(self.get_ranking)
        self.router.get("/{ranking_id}/detail", response_model=RankingDetailResponse)(
            self.get_ranking_detail
        )
        self.router.get(
            "/{athlete_id}/explainability",
            response_model=dict
        )(self.get_ranking_explainability)
        self.router.get(
            "/{athlete_id}/qualification-scenarios",
            response_model=AthleteQualificationResponse
        )(self.get_qualification_scenarios)
        self.router.get(
            "/{athlete_id}/history",
            response_model=list
        )(self.get_ranking_history)
        self.router.post("/search", response_model=RankingsListResponse)(self.search_rankings)
    
    # ========================================================================
    # GET ENDPOINTS
    # ========================================================================
    
    async def get_rankings(
        self,
        sport: Optional[str] = Query(None, description="Filter by sport"),
        category: Optional[str] = Query(None, description="Filter by category"),
        window: str = Query("current", description="Time window"),
        limit: int = Query(50, ge=1, le=1000),
        offset: int = Query(0, ge=0),
        search: Optional[str] = Query(None, description="Search by athlete name"),
        db: Session = Depends(get_db)
    ) -> RankingsListResponse:
        """
        Get rankings list with optional filtering.
        
        - **sport**: Filter by sport ID
        - **category**: Filter by category ID
        - **window**: Time window (current, rolling-12, ytd, all-time)
        - **limit**: Results per page (max 1000)
        - **offset**: Pagination offset
        - **search**: Search by athlete name
        """
        try:
            # Use category if provided, otherwise use sport
            category_id = category or sport or "all"
            
            service = RankingService(db)
            
            if search:
                rankings, total = service.search_rankings(
                    category_id, search, limit, offset
                )
            else:
                rankings, total = service.get_rankings(
                    category_id, sport, limit, offset
                )
            
            return RankingsListResponse(
                data=rankings,
                total=total,
                limit=limit,
                offset=offset,
                count=len(rankings)
            )
        except ServiceException as e:
            logger.error(f"Service error in get_rankings: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
        except Exception as e:
            logger.error(f"Unexpected error in get_rankings: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )
    
    async def get_ranking(
        self,
        ranking_id: str,
        db: Session = Depends(get_db)
    ) -> RankingResponse:
        """
        Get single ranking by ID.
        
        - **ranking_id**: Ranking ID
        """
        try:
            service = RankingService(db)
            ranking = service.get_ranking(ranking_id)
            
            if not ranking:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Ranking {ranking_id} not found"
                )
            
            return ranking
        except HTTPException:
            raise
        except ServiceException as e:
            logger.error(f"Service error in get_ranking: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
    
    async def get_ranking_detail(
        self,
        ranking_id: str,
        db: Session = Depends(get_db)
    ) -> RankingDetailResponse:
        """
        Get ranking with all contributing events.
        
        - **ranking_id**: Ranking ID
        """
        try:
            service = RankingService(db)
            ranking = service.get_ranking_detail(ranking_id)
            
            if not ranking:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Ranking {ranking_id} not found"
                )
            
            return ranking
        except HTTPException:
            raise
        except ServiceException as e:
            logger.error(f"Service error in get_ranking_detail: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
    
    async def get_ranking_explainability(
        self,
        athlete_id: str,
        category_id: str = Query(..., description="Category ID"),
        db: Session = Depends(get_db)
    ) -> dict:
        """
        Get ranking explainability with contributing events.
        
        - **athlete_id**: Athlete ID
        - **category_id**: Category ID
        """
        try:
            service = RankingService(db)
            explainability = service.get_ranking_explainability(athlete_id, category_id)
            
            if not explainability:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Ranking for athlete {athlete_id} not found"
                )
            
            return explainability.dict()
        except HTTPException:
            raise
        except ServiceException as e:
            logger.error(f"Service error in get_ranking_explainability: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
    
    async def get_qualification_scenarios(
        self,
        athlete_id: str,
        category_id: str = Query(..., description="Category ID"),
        db: Session = Depends(get_db)
    ) -> AthleteQualificationResponse:
        """
        Get qualification scenarios for athlete.
        
        - **athlete_id**: Athlete ID
        - **category_id**: Category ID
        """
        try:
            service = RankingService(db)
            scenarios = service.get_qualification_scenarios(athlete_id, category_id)
            
            if not scenarios:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"No scenarios found for athlete {athlete_id}"
                )
            
            return scenarios
        except HTTPException:
            raise
        except ServiceException as e:
            logger.error(f"Service error in get_qualification_scenarios: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
    
    async def get_ranking_history(
        self,
        athlete_id: str,
        category_id: str = Query(..., description="Category ID"),
        days: Optional[int] = Query(None, description="Last N days"),
        limit: int = Query(100, ge=1, le=1000),
        db: Session = Depends(get_db)
    ) -> list:
        """
        Get ranking history for athlete.
        
        - **athlete_id**: Athlete ID
        - **category_id**: Category ID
        - **days**: Optional number of days to look back
        - **limit**: Maximum results
        """
        try:
            service = RankingService(db)
            history = service.get_ranking_history(
                athlete_id, category_id, days, limit
            )
            
            return history
        except ServiceException as e:
            logger.error(f"Service error in get_ranking_history: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
    
    # ========================================================================
    # POST ENDPOINTS
    # ========================================================================
    
    async def search_rankings(
        self,
        filters: RankingsFilterRequest,
        db: Session = Depends(get_db)
    ) -> RankingsListResponse:
        """
        Search rankings with advanced filters.
        
        - **filters**: Filter request with sport, category, window
        """
        try:
            service = RankingService(db)
            rankings, total = service.search_rankings(
                filters.category or "all",
                filters.search,
                filters.limit,
                filters.offset
            )
            
            return RankingsListResponse(
                data=rankings,
                total=total,
                limit=filters.limit,
                offset=filters.offset,
                count=len(rankings)
            )
        except ServiceException as e:
            logger.error(f"Service error in search_rankings: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )


class AdminRankingRouter:
    """
    Router class for admin ranking endpoints.
    
    Implements admin-only operations like recomputation.
    """
    
    def __init__(self):
        """Initialize router"""
        self.router = APIRouter(
            prefix="/api/admin/rankings",
            tags=["admin-rankings"],
            responses={
                400: {"model": ErrorResponse, "description": "Bad Request"},
                401: {"model": ErrorResponse, "description": "Unauthorized"},
                404: {"model": ErrorResponse, "description": "Not Found"},
                500: {"model": ErrorResponse, "description": "Internal Server Error"}
            }
        )
        self._register_routes()
    
    def _register_routes(self):
        """Register all routes"""
        self.router.post("/recompute", response_model=RankingRecomputeResponse)(
            self.trigger_recompute
        )
    
    # ========================================================================
    # ADMIN ENDPOINTS
    # ========================================================================
    
    async def trigger_recompute(
        self,
        request: RankingRecomputeRequest,
        db: Session = Depends(get_db)
    ) -> RankingRecomputeResponse:
        """
        Trigger ranking recomputation (admin only).
        
        - **event_id**: Event ID that triggered recomputation
        - **sport_id**: Optional sport ID to limit scope
        - **category_id**: Optional category ID to limit scope
        - **triggered_by**: Who triggered the recomputation
        """
        try:
            # TODO: Add authentication check here
            # if not user.is_admin:
            #     raise HTTPException(status_code=403, detail="Unauthorized")
            
            ranking_service = RankingService(db)
            recompute_service = RankingRecomputeService(db, ranking_service)
            
            response = recompute_service.trigger_recompute(
                request.event_id,
                request.sport_id,
                request.category_id,
                request.triggered_by
            )
            
            logger.info(f"Recompute triggered by {request.triggered_by}: {response.recompute_id}")
            
            return response
        except ServiceException as e:
            logger.error(f"Service error in trigger_recompute: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
        except Exception as e:
            logger.error(f"Unexpected error in trigger_recompute: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )


def create_ranking_routers() -> tuple:
    """Create and return ranking routers"""
    return (RankingRouter().router, AdminRankingRouter().router)
