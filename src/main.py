from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.core.apis.trip import router as trip_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(trip_router, prefix="/api/trip")
