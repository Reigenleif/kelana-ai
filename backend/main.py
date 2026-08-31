from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from database import get_db, init_db
from migrate_seed import run_migration_and_seed
from models.chat import ConversationCreate, ConversationOut, MessageCreate, MessageOut
from models.trip import TripCreate, TripOut, TripUpdate
from models.user import Token, User, UserCreate, UserLogin, UserOut
from services.auth_service import (
    authenticate_user,
    get_current_user,
    list_users,
    register_user,
)
from services.chat_service import (
    create_conversation,
    get_conversation_messages,
    list_conversations,
    send_message,
)
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
    try:
        run_migration_and_seed()
    except Exception as e:
        print(f"Migration / seed info: {e}")
    yield


app = FastAPI(
    title="Kelana AI API",
    description="Smart travel itinerary planning, AI recommendations, authentication & AI assistant chat.",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Root / Heartbeat ---
@app.get("/")
async def root():
    return {"message": "Welcome to Kelana AI Travel API v2.0", "status": "online"}


# --- Auth Routes ---
@app.post("/auth/register", response_model=Token)
def register_route(user_in: UserCreate, db: Session = Depends(get_db)):
    return register_user(db, user_in)


@app.post("/auth/login", response_model=Token)
def login_route(credentials: UserLogin, db: Session = Depends(get_db)):
    return authenticate_user(db, credentials)


@app.get("/auth/me", response_model=UserOut)
def get_me_route(current_user: User = Depends(get_current_user)):
    return UserOut.model_validate(current_user)


@app.get("/users", response_model=list[UserOut])
def get_users_route(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return list_users(db, current_user)


# --- Recommendations & Static Options ---
@app.get("/recommendations")
async def get_recommendations():
    recommendations = ["Tokyo Tower", "Mount Fuji", "Shibuya", "Kyoto Temples", "Swiss Alps", "Bali Beaches"]
    return {"recommendations": recommendations}


@app.get("/transportations")
async def get_transportations():
    transportations = ["High-speed Bullet Train", "Rental Car", "Flight", "Ferry", "Public Transit"]
    return {"transportations": transportations}


# --- Trips Routes (Per User) ---
@app.post("/trips", response_model=TripOut)
def create_trip_route(
    trip: TripCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return create_trip(db, trip, user_id=current_user.id)


@app.get("/trips", response_model=list[TripOut])
def read_trips_route(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return read_trips(db, user_id=current_user.id)


@app.get("/trips/{trip_id}", response_model=TripOut)
def read_trip_route(
    trip_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    trip = read_trip(db, trip_id, user_id=current_user.id)
    if trip is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")
    return trip


@app.put("/trips/{trip_id}", response_model=TripOut)
def update_trip_route(
    trip_id: int,
    trip_update: TripUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    trip = update_trip(db, trip_id, trip_update, user_id=current_user.id)
    if trip is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")
    return trip


@app.delete("/trips/{trip_id}")
def delete_trip_route(
    trip_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    deleted = delete_trip(db, trip_id, user_id=current_user.id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")
    return {"message": "Trip deleted successfully"}


@app.post("/trips/{trip_id}/generate", response_model=TripOut)
@app.get("/trips/{trip_id}/generate", response_model=TripOut)
def generate_recommendation_route(
    trip_id: int,
    force_refresh: bool = False,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        trip = generate_trip_recommendation(db, trip_id, user_id=current_user.id, force_refresh=force_refresh)
        if trip is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trip not found")
        return trip
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to generate recommendation: {str(e)}")


# --- AI Chat & Conversations Routes ---
@app.get("/conversations", response_model=list[ConversationOut])
def list_conversations_route(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return list_conversations(db, current_user.id)


@app.post("/conversations", response_model=ConversationOut)
def create_conversation_route(
    conv_in: ConversationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return create_conversation(db, current_user.id, conv_in.title)


@app.get("/conversations/{conversation_id}/messages", response_model=list[MessageOut])
def get_messages_route(
    conversation_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_conversation_messages(db, conversation_id, current_user.id)


@app.post("/conversations/{conversation_id}/messages", response_model=list[MessageOut])
def send_message_route(
    conversation_id: int,
    msg_in: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return send_message(db, conversation_id, current_user.id, msg_in)
