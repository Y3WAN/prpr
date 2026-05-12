from pydantic import BaseModel


class RecommendationResponse(BaseModel):
    truck_id: int
    truck_name: str
    food_type: str
    distance_m: int
    latitude: float
    longitude: float
