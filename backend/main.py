from fastapi import FastAPI, UploadFile, Form
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
import os
import uuid

from backend.processor import process_video  # your processing function

app = FastAPI()

# Allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure outputs folder exists
if not os.path.exists("outputs"):
    os.makedirs("outputs")

# Mount /outputs first so videos and JSON are accessible for preview/download
app.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")

# Mount frontend at /frontend
app.mount("/frontend", StaticFiles(directory="frontend", html=True), name="frontend")

# Redirect root / to frontend index
@app.get("/")
async def root():
    return RedirectResponse(url="/frontend/index.html")

@app.post("/api/process")
async def process_video_api(video: UploadFile, background: str = Form("grid"), include_audio: str = Form("false")):
    # Generate unique job id
    job_id = str(uuid.uuid4())[:8]
    input_path = f"outputs/{job_id}_input.mp4"
    output_video = f"outputs/{job_id}_stick.mp4"
    output_json = f"outputs/{job_id}_keypoints.json"

    # Save uploaded video
    with open(input_path, "wb") as f:
        f.write(await video.read())

    # Debug log
    print(f"Processing video: {input_path}")

    # Process video into stick figure
    process_video(input_path, output_video, output_json, background, include_audio.lower() == "true")

    # Debug log
    print(f"Finished processing: {output_video}")

    # Return browser-accessible URLs
    BASE_URL = "https://pose2stick.onrender.com"  # your backend Render URL

    return {
        "video_url": f"{BASE_URL}/outputs/{job_id}_stick.mp4",
        "keypoints_url": f"{BASE_URL}/outputs/{job_id}_keypoints.json",
    }

