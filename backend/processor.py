import cv2
import json
import numpy as np
import mediapipe as mp
import os
from moviepy.editor import VideoFileClip

def draw_stick_figure(frame, landmarks, background="grid"):
    h, w, _ = frame.shape
    stick = np.zeros_like(frame)

    # Background options
    if background == "grid":
        stick[:] = (30, 30, 30)
        for i in range(0, w, 40):
            cv2.line(stick, (i, 0), (i, h), (50, 50, 50), 1)
        for j in range(0, h, 40):
            cv2.line(stick, (0, j), (w, j), (50, 50, 50), 1)
    elif background == "solid":
        stick[:] = (20, 20, 20)
    elif background == "gradient":
        for i in range(h):
            color = int(255 * (i / h))
            stick[i, :] = (color, color // 2, 255 - color)
    else:
        stick[:] = (0, 0, 0)

    # Connections between landmarks (MediaPipe Pose)
    connections = [
        (11, 13), (13, 15), (12, 14), (14, 16),
        (11, 12), (23, 24), (11, 23), (12, 24),
        (23, 25), (25, 27), (24, 26), (26, 28)
    ]

    # Draw lines
    for start, end in connections:
        if landmarks and len(landmarks) > max(start, end):
            x1, y1 = int(landmarks[start][0] * w), int(landmarks[start][1] * h)
            x2, y2 = int(landmarks[end][0] * w), int(landmarks[end][1] * h)
            cv2.line(stick, (x1, y1), (x2, y2), (0, 255, 0), 2)

    # Draw points
    for lm in landmarks:
        x, y, _ = lm
        cv2.circle(stick, (int(x * w), int(y * h)), 4, (0, 0, 255), -1)

    return stick

def process_video(input_path, output_path, json_path, background="grid", include_audio=False):
    mp_pose = mp.solutions.pose.Pose()
    cap = cv2.VideoCapture(input_path)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    keypoints_data = []

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = mp_pose.process(image_rgb)

        if results.pose_landmarks:
            landmarks = [(lm.x, lm.y, lm.z) for lm in results.pose_landmarks.landmark]
            keypoints_data.append(landmarks)
            frame = draw_stick_figure(frame, landmarks, background)
        else:
            keypoints_data.append([])  # no person detected

        out.write(frame)

    cap.release()
    out.release()

    # Optionally merge original audio into the generated video
    if include_audio:
        temp_output = None
        try:
            import tempfile
            import shutil
            import time
            
            print(f"Starting audio merge for {input_path} -> {output_path}")
            
            # Write to temporary file first to avoid corrupting the original
            # Use .mp4 extension so ffmpeg recognizes the container
            temp_output = output_path + ".tmp.mp4"
            
            # Clean up any existing temp file
            if os.path.exists(temp_output):
                os.remove(temp_output)
            
            with VideoFileClip(input_path) as src_clip:
                print(f"Source video duration: {src_clip.duration}, has audio: {src_clip.audio is not None}")
                
                if src_clip.audio is None:
                    print("Audio merge skipped: source has no audio track.")
                else:
                    with VideoFileClip(output_path) as dst_clip:
                        print(f"Destination video duration: {dst_clip.duration}")
                        
                        audio_duration = min(src_clip.duration or 0, dst_clip.duration or 0)
                        if audio_duration <= 0:
                            print("Audio merge skipped: non-positive duration.")
                        else:
                            print(f"Merging audio for duration: {audio_duration}")
                            audio = src_clip.audio.subclip(0, audio_duration)
                            final = dst_clip.set_audio(audio)
                            
                            # Write to temp file first
                            final.write_videofile(
                                temp_output,
                                codec="libx264",
                                audio_codec="aac",
                                fps=max(1, int(round(dst_clip.fps or 24))),
                                verbose=False,
                                logger=None,
                            )
                            
                            # Wait a moment for file to be fully written
                            time.sleep(0.5)
                            
                            # Only replace original if temp file was created successfully
                            if os.path.exists(temp_output) and os.path.getsize(temp_output) > 0:
                                # Check file sizes to verify audio was added
                                original_size = os.path.getsize(output_path)
                                temp_size = os.path.getsize(temp_output)
                                print(f"Original size: {original_size} bytes, Temp size: {temp_size} bytes")
                                
                                shutil.move(temp_output, output_path)
                                print("Audio successfully merged into video.")
                                temp_output = None  # Mark as successfully moved
                            else:
                                print("Audio merge failed: temp file not created or empty.")
        except Exception as e:
            # Fallback: keep silent video if audio merge fails
            print(f"Audio merge failed: {e}")
            import traceback
            traceback.print_exc()
        finally:
            # Clean up temp file if it still exists
            if temp_output and os.path.exists(temp_output):
                try:
                    os.remove(temp_output)
                    print("Cleaned up temp file")
                except:
                    pass

    # Save keypoints to JSON
    with open(json_path, "w") as f:
        json.dump(keypoints_data, f)
