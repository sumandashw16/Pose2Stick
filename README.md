# Pose2Stick
OVERVIEW:
This module processes a video to extract human pose information and convert it into a stick-figure animation.
For every frame in the video:
  -> Human body joints (keypoints) are detected
  -> Selected joints are connected using rods (bones)
  -> A synthetic stick-figure frame is generated
  -> All joint coordinates are saved as structured JSON data

The output consists of:
  -> A stick-figure video
  -> A JSON file containing pose keypoints for each frame
---------------------------------------------------------------------------------------------------------------
CORE Tech USED:
MediaPipe Pose → Human pose estimation (33 landmarks per frame)
OpenCV → Frame handling, drawing joints and rods, video writing
MoviePy (optional) → Audio extraction and re-attachment
NumPy → Frame and image manipulation
----------------------------------------------------------------------------------------------------------------
PIPELINE:
Input Video
   ↓
Read video frame-by-frame (OpenCV)
   ↓
Convert frame to RGB
   ↓
Pose detection (MediaPipe Pose)
   ↓
Extract joint coordinates (x, y, z)
   ↓
Store joints for current frame (JSON)
   ↓
Connect joints using predefined skeleton map
   ↓
Draw joints + rods on synthetic background
   ↓
Write frame to output video
   ↓
(Optional) Merge original audio
   ↓
Final stick-figure video + keypoints JSON
-------------------------------------------------------------------------------------------------------------------
example extracted video:
https://github.com/user-attachments/assets/a127ffe4-2bd3-4fec-8051-d37ac4489865
example extracted JSON:
https://github.com/user-attachments/files/24228132/6528c52f_keypoints.json
[BOX] [BOX]
