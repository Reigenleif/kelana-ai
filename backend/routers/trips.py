from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

try:
    from database import get_db
    from models.trip import TripCreate, TripOut, TripUpdate
    from models.user import User
    from services.auth_service import get_current_user
    from services.trip_service import (
        create_trip,
        delete_trip,
        generate_trip_recommendation,
        read_trip,
        read_trips,
        update_trip,
    )
except ImportError:
    from backend.database import get_db
    from backend.models.trip import TripCreate, TripOut, TripUpdate
    from backend.models.user import User
    from backend.services.auth_service import get_current_user
    from backend.services.trip_service import (
        create_trip,
        delete_trip,
        generate_trip_recommendation,
        read_trip,
        read_trips,
        update_trip,
    )

router = APIRouter(tags=["Trips & Itineraries"])


@router.post("/trips", response_model=TripOut, status_code=status.HTTP_200_OK)
def create_trip_endpoint(
    trip: TripCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return create_trip(db, trip, user_id=current_user.id)


@router.get("/trips", response_model=list[TripOut])
def read_trips_endpoint(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return read_trips(db, user_id=current_user.id)


@router.get("/trips/{trip_id}", response_model=TripOut)
def read_trip_endpoint(
    trip_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    trip = read_trip(db, trip_id, user_id=current_user.id)
    if trip is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found"
        )
    return trip


@router.put("/trips/{trip_id}", response_model=TripOut)
def update_trip_endpoint(
    trip_id: int,
    trip_update: TripUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    trip = update_trip(db, trip_id, trip_update, user_id=current_user.id)
    if trip is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found"
        )
    return trip


@router.delete("/trips/{trip_id}")
def delete_trip_endpoint(
    trip_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    deleted = delete_trip(db, trip_id, user_id=current_user.id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found"
        )
    return {"message": "Trip deleted successfully"}


@router.post("/trips/{trip_id}/generate", response_model=TripOut)
@router.get("/trips/{trip_id}/generate", response_model=TripOut)
def generate_recommendation_endpoint(
    trip_id: int,
    force_refresh: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        trip = generate_trip_recommendation(
            db, trip_id, user_id=current_user.id, force_refresh=force_refresh
        )
        if trip is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found"
            )
        return trip
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate recommendation: {str(e)}",
        )
