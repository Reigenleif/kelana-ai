from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException

from database import get_db, init_db
from models.trip import TripCreate, TripUpdate
from services.trip_service import (
    create_trip,
    delete_trip,
    generate_trip_recommendation,
    read_trip,
    read_trips,
    update_trip,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def root():
    # Untuk heartbeat
    return {"message": "Welcome to the Travel API!"}

@app.get("/recommendations")
async def get_recommendations():
    # Mengembalikan daftar rekomendasi tempat wisata
    recommendations = ["Tokyo Tower", "Mount Fuji", "Shibuya"]
    return {"recommendations": recommendations}

@app.get("/transportations")
async def get_transportations():
    # Mengembalikan daftar moda transportasi
    transportations = ["Tokyo Tower", "Mount Fuji", "Shibuya"]
    return {"transportations": transportations}

@app.post("/trips")
def create_trip_route(trip: TripCreate, db=Depends(get_db)):
    # Membuat perjalanan baru
    return create_trip(db, trip)


@app.get("/trips")
def read_trips_route(db=Depends(get_db)):
    # Mengembalikan daftar perjalanan
    return read_trips(db)


@app.get("/trips/{trip_id}")
def read_trip_route(trip_id: int, db=Depends(get_db)):
    # Mengembalikan detail perjalanan berdasarkan ID
    trip = read_trip(db, trip_id)
    if trip is None:
        raise HTTPException(status_code=404, detail="Trip not found")
    return trip


@app.put("/trips/{trip_id}")
def update_trip_route(trip_id: int, trip_update: TripUpdate, db=Depends(get_db)):
    # Memperbarui detail perjalanan berdasarkan ID
    trip = update_trip(db, trip_id, trip_update)
    if trip is None:
        raise HTTPException(status_code=404, detail="Trip not found")
    return trip


@app.delete("/trips/{trip_id}")
def delete_trip_route(trip_id: int, db=Depends(get_db)):
    # Menghapus perjalanan berdasarkan ID
    deleted = delete_trip(db, trip_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Trip not found")
    return {"message": "Trip deleted successfully"}


@app.post("/trips/{trip_id}/generate")
@app.get("/trips/{trip_id}/generate")
def generate_recommendation_route(trip_id: int, force_refresh: bool = False, db=Depends(get_db)):
    # Membuat atau mengembalikan rekomendasi perjalanan berdasarkan ID
    try:
        trip = generate_trip_recommendation(db, trip_id, force_refresh=force_refresh)
        if trip is None:
            raise HTTPException(status_code=404, detail="Trip not found")
        return trip
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate recommendation: {str(e)}")

