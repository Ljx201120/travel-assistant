import requests
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()


class PexelsService:
    def __init__(self):
        self.api_key = os.getenv("PEXELS_API_KEY")
        self.base_url = "https://api.pexels.com/v1"

    def get_photo_url(self, query: str) -> Optional[str]:
        try:
            response = requests.get(
                f"{self.base_url}/search",
                headers={"Authorization": self.api_key},
                params={"query": query, "per_page": 1},
                timeout=10,
            )
            response.raise_for_status()
            photos = response.json().get("photos", [])
            return photos[0]["src"]["large"] if photos else None
        except Exception:
            return None
