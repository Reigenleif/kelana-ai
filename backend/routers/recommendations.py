from fastapi import APIRouter

router = APIRouter(tags=["Recommendations & Options"])


@router.get("/recommendations")
async def get_recommendations():
    recommendations = [
        "Tokyo Tower",
        "Mount Fuji",
        "Shibuya",
        "Kyoto Temples",
        "Swiss Alps",
        "Bali Beaches",
    ]
    return {"recommendations": recommendations}


@router.get("/transportations")
async def get_transportations():
    transportations = [
        "High-speed Bullet Train",
        "Rental Car",
        "Flight",
        "Ferry",
        "Public Transit",
    ]
    return {"transportations": transportations}
