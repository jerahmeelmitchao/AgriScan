import sys
import os
import uuid
import subprocess
from datetime import datetime
from supabase_client import supabase

video_path = sys.argv[1]
flight_id = int(sys.argv[2])

# 1. Extract frames
os.makedirs("temp_frames", exist_ok=True)
output_pattern = "temp_frames/frame_%05d.jpg"

cmd = f"ffmpeg -i {video_path} -vf fps=1 {output_pattern}"
subprocess.run(cmd, shell=True)

# 2. Upload all frames
bucket = supabase.storage.from_("frames")

for file in os.listdir("temp_frames"):
    frame_path = f"temp_frames/{file}"

    # Upload
    unique_name = f"{uuid.uuid4()}_{file}"
    bucket.upload(unique_name, frame_path)
    frame_url = bucket.get_public_url(unique_name)

    # Insert row in frames table
    supabase.table("frames").insert({
        "flight_id": flight_id,
        "timestamp": datetime.now().isoformat(),
        "gps_lat": 0,    # GPS not included in video — we will get GPS from Orange Pi later
        "gps_lon": 0,
        "file_url": frame_url
    }).execute()

    print("Uploaded frame:", frame_url)

    # Send to ML worker
    os.system(f"python3 worker_inference.py {frame_path}")

# Cleanup
for f in os.listdir("temp_frames"):
    os.remove(f"temp_frames/{f}")
