import fastapi

app = fastapi.FastAPI()

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
