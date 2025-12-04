import os
import uuid
from fastapi import FastAPI, UploadFile, File, Form
from datetime import datetime
from supabase_client import supabase

app = FastAPI()

# -----------------------------
# Start Flight
# -----------------------------
@app.post("/api/start-flight")
def start_flight(user_id: int = Form(...)):
    data = {
        "user_id": user_id,
        "start_time": datetime.now().isoformat(),
        "status": "active"
    }
    response = supabase.table("flights").insert(data).execute()
    print("Start flight response:", response)
  
    return {"success": True, "flight_data": response.data}

# -----------------------------
# Stop Flight
# -----------------------------
@app.post("/api/stop-flight/{flight_id}")
def stop_flight(flight_id: int):
    data = {
        "status": "completed",
        "end_time": datetime.now().isoformat()
    }
    response = supabase.table("flights").update(data).eq("flight_id", flight_id).execute()
    print("Stop flight response:", response)
   
    return {"success": True, "flight_data": response.data}

# -----------------------------
# Upload Frame
# -----------------------------
@app.post("/api/upload-frame")
async def upload_frame(
    flight_id: int = Form(...),
    timestamp: str = Form(...),
    gps_lat: float = Form(...),
    gps_lon: float = Form(...),
    file: UploadFile = File(...)
):
    # 1. Check flight exists
    flight_check = supabase.table("flights").select("*").eq("flight_id", flight_id).execute()
    if not flight_check.data:
        return {"error": "Flight ID does not exist"}

    # 2. Create temp folder and save file
    os.makedirs("temp_images", exist_ok=True)
    temp_path = f"temp_images/{file.filename}"
    with open(temp_path, "wb") as f:
        f.write(await file.read())
    print("Temp file saved at:", temp_path)

    # 3. Upload to Supabase Storage with unique filename
    bucket = supabase.storage.from_("frames")
    unique_filename = f"{uuid.uuid4()}_{file.filename}"
    bucket.upload(unique_filename, temp_path)
    public_url = bucket.get_public_url(unique_filename)
    print("Uploaded file URL:", public_url)

    # 4. Insert metadata into frames table
    data = {
        "flight_id": flight_id,
        "timestamp": timestamp,
        "gps_lat": gps_lat,
        "gps_lon": gps_lon,
        "file_url": public_url
    }
    response = supabase.table("frames").insert(data).execute()
    print("Insert response:", response)

    # 5. Cleanup temp file
    os.remove(temp_path)

    # 6. Return response
    
    return {"success": True, "frame_data": response.data}

# -----------------------------
# Get Detections for Flight
# -----------------------------
@app.get("/api/detections/{flight_id}")
def get_detections(flight_id: int):
    frames = supabase.table("frames").select("*").eq("flight_id", flight_id).execute().data
    detections = []
    for frame in frames:
        frame_dets = supabase.table("detections").select("*").eq("frame_id", frame["frame_id"]).execute().data
        detections.extend(frame_dets)
    return {"detections": detections}

# -----------------------------
# Get Field Map for Flight
# -----------------------------
@app.get("/api/field-map/{flight_id}")
def get_field_map(flight_id: int):
    response = supabase.table("field_maps").select("*").eq("flight_id", flight_id).execute()
    if response.data:
        return {"field_map": response.data[0]}
    return {"error": "No field map found"}

# -----------------------------
# Upload Video (Orange Pi)
# -----------------------------
# -----------------------------
# Upload Video (Orange Pi)
# -----------------------------
import threading
import requests

WORKER_URL = os.getenv("WORKER_URL", "http://localhost:9000")

@app.post("/api/upload-video")
async def upload_video(
    flight_id: int = Form(...),
    file: UploadFile = File(...)
):
    # 1. Verify flight exists
    flight_check = supabase.table("flights").select("*").eq("flight_id", flight_id).execute()
    if not flight_check.data:
        return {"error": "Invalid flight ID"}

    # 2. Save temporary file
    os.makedirs("temp_videos", exist_ok=True)
    temp_path = f"temp_videos/{file.filename}"

    with open(temp_path, "wb") as f:
        f.write(await file.read())

    print("Video saved temporarily:", temp_path)

    # 3. Upload to Supabase Storage
    bucket = supabase.storage.from_("videos")
    unique_name = f"{uuid.uuid4()}_{file.filename}"

    bucket.upload(unique_name, temp_path)
    public_url = bucket.get_public_url(unique_name)

    print("Uploaded video URL:", public_url)

    # 4. Insert into database
    db_entry = {
        "flight_id": flight_id,
        "file_url": public_url
    }

    response = supabase.table("videos").insert(db_entry).execute()

    # 5. Delete temp file
    os.remove(temp_path)

    # -----------------------------
    # 6. TRIGGER WORKER (background)
    # -----------------------------
    def trigger_worker(video_path, flight_id):
        try:
            print("Triggering worker for processing...")
            requests.post(
                f"{WORKER_URL}/api/process-video",
                json={"supabase_path": video_path, "flight_id": flight_id},
                timeout=5
            )
            print("Worker triggered successfully.")
        except Exception as e:
            print("Worker trigger failed:", e)

    threading.Thread(
        target=trigger_worker,
        args=(unique_name, flight_id),
        daemon=True
    ).start()

    # 7. Return response
    return {
        "success": True,
        "video_url": public_url,
        "db_response": response.data
    }


@app.get("/api/flight-status/{flight_id}")
def flight_status(flight_id: int):
    flight = supabase.table("flights").select("*").eq("flight_id", flight_id).execute()
    if not flight.data:
        return {"error": "Flight not found"}
    return {"status": flight.data[0]["status"]}
