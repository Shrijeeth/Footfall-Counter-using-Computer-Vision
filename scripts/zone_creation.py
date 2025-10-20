import argparse
import os
import sys

import cv2

roi = []


def draw_rectangle(event, x, y, flags, param):
    global roi, img_copy
    if event == cv2.EVENT_LBUTTONDOWN:
        roi = [(x, y)]
    elif event == cv2.EVENT_LBUTTONUP:
        roi.append((x, y))
        cv2.rectangle(img_copy, roi[0], roi[1], (0, 255, 255), 2)
        cv2.imshow("Frame", img_copy)
        print("ROI coordinates:", roi)


# Parse command line arguments
parser = argparse.ArgumentParser(
    description="Create zones for footfall counter by drawing ROI on video frame"
)
parser.add_argument("video_path", help="Path to the input video file")
args = parser.parse_args()

# Validate video file exists
if not os.path.exists(args.video_path):
    print(f"Error: Video file '{args.video_path}' not found.")
    sys.exit(1)

# Load video
video_path = args.video_path
cap = cv2.VideoCapture(video_path)

# Get total frame count and select a middle frame
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
if total_frames == 0:
    raise ValueError("Video has no frames or frame count could not be determined")

# Use middle frame, or frame 100 if video is long enough
target_frame = min(100, total_frames // 2)
print(f"Video has {total_frames} frames, using frame {target_frame}")

cap.set(cv2.CAP_PROP_POS_FRAMES, target_frame)
ret, frame = cap.read()
cap.release()

if not ret:
    raise ValueError("Could not read frame from video")

img_copy = frame.copy()
cv2.imshow("Frame", img_copy)
cv2.setMouseCallback("Frame", draw_rectangle)

print("Click and drag to draw the door ROI, release to confirm.")
cv2.waitKey(0)
cv2.destroyAllWindows()

# Extract coordinates
if len(roi) == 2:
    x_min, y_min = roi[0]
    x_max, y_max = roi[1]
    door_roi = (x_min, y_min, x_max, y_max)
    print("Final ROI:", door_roi)
    frame_h, frame_w = frame.shape[:2]

    x_min_norm = x_min / frame_w
    y_min_norm = y_min / frame_h
    x_max_norm = x_max / frame_w
    y_max_norm = y_max / frame_h

    door_roi_normalized = (x_min_norm, y_min_norm, x_max_norm, y_max_norm)
    print("Normalized ROI:", door_roi_normalized)

    frame = cv2.rectangle(frame, roi[0], roi[1], (0, 255, 0), 2)

# Save frame
image_path = os.path.expanduser("data/roi_frame.jpg")
cv2.imwrite(image_path, frame)
print(f"Frame saved to {image_path}")
