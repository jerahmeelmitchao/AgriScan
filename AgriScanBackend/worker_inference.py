import sys
from supabase_client import supabase

frame_path = sys.argv[1]

# -------------------------------
# Fake ML model (for demo)
# Replace with your real model.
# -------------------------------
def predict(image_path):
    return {
        "disease_type": "brown_spot",
        "confidence": 0.88
    }

result = predict(frame_path)

# Insert into detections table
supabase.table("detections").insert({
    "frame_id": None,          # we must join frame using URL lookup
    "disease_type": result["disease_type"],
    "confidence": result["confidence"],
    "gps_lat": 0,
    "gps_lon": 0
}).execute()
