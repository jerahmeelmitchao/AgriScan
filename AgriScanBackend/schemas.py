from pydantic import BaseModel
from typing import Optional

# -------------------------------
# Flight Schemas
# -------------------------------
class FlightCreate(BaseModel):
    user_id: int

class FlightResponse(BaseModel):
    flight_id: int
    user_id: int
    start_time: str
    end_time: Optional[str] = None
    status: str

# -------------------------------
# Frame Schemas
# -------------------------------
class FrameCreate(BaseModel):
    flight_id: int
    timestamp: str
    gps_lat: float
    gps_lon: float
    file_url: str

class FrameResponse(FrameCreate):
    frame_id: int

# -------------------------------
# Detection Schemas
# -------------------------------
class DetectionResponse(BaseModel):
    detection_id: int
    frame_id: int
    disease_type: str
    confidence: float
    gps_lat: float
    gps_lon: float

# -------------------------------
# Field Map Schemas
# -------------------------------
class FieldMapResponse(BaseModel):
    map_id: int
    flight_id: int
    map_url: str
