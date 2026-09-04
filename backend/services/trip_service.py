from datetime import datetime

from models.trip import Trip, TripCreate, TripOut, TripUpdate
from services import bedrock_service


def get_trip_category(budget):
    if budget < 1000:
        return "Backpacker"
    elif budget <= 3000:
        return "Standard"
    else:
        return "Luxury"


def get_travel_season(month):
    if month == "December":
        return "Peak Season"
    elif month == "June":
        return "Holiday Season"
    else:
        return "Regular Season"


def calculate_daily_budget(budget, days):
    return budget / days


def serialize_trip(trip: Trip) -> TripOut:
    return TripOut.model_validate(trip)


def create_trip(db, trip: TripCreate, user_id: int) -> TripOut:
    daily_budget = trip.daily_budget
    if daily_budget is None:
        daily_budget = trip.budget / trip.days

    db_trip = Trip(
        user_id=user_id,
        destination=trip.destination,
        days=trip.days,
        budget=trip.budget,
        category=trip.category,
        daily_budget=daily_budget,
        created_at=datetime.utcnow(),
    )
    db.add(db_trip)
    db.commit()
    db.refresh(db_trip)
    return serialize_trip(db_trip)


def read_trips(db, user_id: int) -> list[TripOut]:
    trips = db.query(Trip).filter(Trip.user_id == user_id).order_by(Trip.id.desc()).all()
    return [serialize_trip(trip) for trip in trips]


def read_trip(db, trip_id: int, user_id: int) -> TripOut | None:
    trip = db.query(Trip).filter(Trip.id == trip_id, Trip.user_id == user_id).first()
    if trip is None:
        return None
    return serialize_trip(trip)


def update_trip(db, trip_id: int, trip_update: TripUpdate, user_id: int) -> TripOut | None:
    trip = db.query(Trip).filter(Trip.id == trip_id, Trip.user_id == user_id).first()
    if trip is None:
        return None

    if hasattr(trip_update, "model_dump"):
        update_data = trip_update.model_dump(exclude_unset=True)
    else:
        update_data = trip_update.dict(exclude_unset=True)

    if "days" in update_data or "budget" in update_data or "daily_budget" in update_data:
        next_days = update_data.get("days", trip.days)
        next_budget = update_data.get("budget", trip.budget)
        if update_data.get("daily_budget") is None and ("days" in update_data or "budget" in update_data):
            update_data["daily_budget"] = next_budget / next_days

    for field, value in update_data.items():
        setattr(trip, field, value)

    db.commit()
    db.refresh(trip)
    return serialize_trip(trip)


def delete_trip(db, trip_id: int, user_id: int) -> bool:
    trip = db.query(Trip).filter(Trip.id == trip_id, Trip.user_id == user_id).first()
    if trip is None:
        return False

    db.delete(trip)
    db.commit()
    return True


def generate_trip_recommendation(db, trip_id: int, user_id: int, force_refresh: bool = False) -> TripOut | None:
    trip = db.query(Trip).filter(Trip.id == trip_id, Trip.user_id == user_id).first()
    if trip is None:
        return None

    # Check cache first if available and not forcing refresh
    if trip.ai_recommendation and not force_refresh:
        return serialize_trip(trip)

    # Call AWS Bedrock service for generation
    recommendation = bedrock_service.generate_recommendation(
        destination=trip.destination,
        days=trip.days,
        budget=trip.budget,
        category=trip.category,
    )

    trip.ai_recommendation = recommendation
    db.commit()
    db.refresh(trip)
    return serialize_trip(trip)


def get_recommended_places():
    return [
        "Eiffel Tower, Paris, France",
        "Great Wall of China, China",
        "Machu Picchu, Peru",
        "Santorini, Greece",
        "Grand Canyon, USA",
    ]
