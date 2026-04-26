from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
import httpx
from src.core.apis.trip import router as trip_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/image-proxy")
async def image_proxy(url: str):
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
        return Response(
            content=resp.content,
            media_type=resp.headers.get("content-type", "image/jpeg"),
        )


app.include_router(trip_router, prefix="/api/trip")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
